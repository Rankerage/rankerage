/**
 * rankerage.com — AI-powered natural language search
 * Cloudflare Worker (ES Modules syntax)
 *
 * POST /  { "query": "한국 GDP 순위" }
 * → DeepSeek API → structured JSON search action
 *
 * Deploy: npx wrangler deploy
 * Secret:  npx wrangler secret put DEEPSEEK_API_KEY
 */

// ── Rate Limiter (in-memory, per-worker-instance) ──────────────────
// Max 30 requests per minute per IP.  Resets on the next whole minute.
const RL_WINDOW_MS = 60_000;       // 1 minute rolling window
const RL_MAX        = 30;

const rateStore = new Map();        // IP → { count, windowStart }

function rateLimitOk(ip) {
  const now = Date.now();
  const entry = rateStore.get(ip);

  if (!entry || now - entry.windowStart > RL_WINDOW_MS) {
    // fresh window
    rateStore.set(ip, { count: 1, windowStart: now });
    return true;
  }

  if (entry.count >= RL_MAX) return false;

  entry.count++;
  return true;
}

// Periodic cleanup — fires every 5 min to avoid memory leak.
// Exported for Cloudflare's cron trigger to find it.
export async function scheduled(controller, env, ctx) {
  const now = Date.now();
  for (const [ip, entry] of rateStore) {
    if (now - entry.windowStart > RL_WINDOW_MS * 2) rateStore.delete(ip);
  }
}


// ── System Prompt ───────────────────────────────────────────────────
// Complete list of all metric fields available on rankerage.com.
// Grouped by category for the LLM to understand context better.

const SYSTEM_PROMPT = `You are a search parser for rankerage.com, a country ranking database.
Given a natural language query (Korean or English) about country rankings, comparisons, or
trends, return ONLY valid JSON — no markdown, no code fence, no extra text.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AVAILABLE METRIC FIELDS (complete catalog)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

◆ Economy & Trade
gdp, gdp_per_capita, exports, imports, inflation, gas_price, salary,
workhours, min_wage, cost_living, house_price, debt, reserves, stock_market,
tax_rev, tax_burden, tax_top, corp_tax, vat_rate, govern_spend, business_ease,
unemp, poverty, extreme_poverty, poverty_gap, gini, welfare_spend,
unemp_benefit, pension_rate, basic_income, ubi_experiment,
manufacturing, ecommerce, insurance, insurance_cap, credit_rating,
vc_funding, startups, startup_rate, unicorns, fortune500, game_market

◆ Population & Society
population, population_density, birth_rate, death_rate, infant_mortality,
fertility, median_age, urban_pop, immigration, emigration, refugees,
displaced_from, marriage_rate, marriage_age_m, marriage_age_f, divorce,
teen_pregnancy, contraception, condom_use, sex_frequency, sex_duration,
sex_education, languages, religion_div, race_diversity, minority_rights,
women_parl, lgbtq_rights, gay_marriage, gender_gap, gender, slavery,
child_marriage, child_labor, homelessness, drug_offense, prison,
death_penalty, suicide, murder, assault, burglary, trafficking, gang_violence,
domestic_viol, polit_kill, war_index, freedom, democracy, press

◆ Health & Wellbeing
hdi, hdi_adj, life_expectancy, life_exp_m, life_exp_f, happiness, health,
doctors, nurses, surgeons, beds, mental_health, vaccination, antibiotics,
obesity, bmi_avg, alcohol, smoking, coffee, tea_consume, beer, wine,
meat, beef_consume, pork_consume, chicken_consume, rice_consume,
bread_consume, chocolate, bottled_water, food_waste, organic_food,
cancer, diabetes, hiv_prev, maternal_mortality, height_m, height_f,
baldness, tanning

◆ Education & Science
edu, school_yrs, tertiary, college_rate, universities, literacy,
english, pisa_math, pisa_science, pisa_reading, rd, patents, research_pub,
phd_per_cap, scientists, physicists, nobel, nobel_per_capita, nobel_science,
fields_medal, math_olympiad, chem_olympiad, ai_research, ai_adopt,
books, literature, libraries

◆ Environment & Energy
area, forest, renew, co2, pm25, plastic_waste, recycling, park_area,
water_scarcity, electricity, energy_per_capita, solar_power, wind_power,
nuclear_power, nuke_reactors, radiation_risk, earthquake_count, earthquakes,
volcanoes, tsunami_risk, flood_risk, cyclone_freq, wildfire_freq,
elevation, agri, ev_adoption

◆ Sports & Culture
fifa_ranking, fifa_w, olympic, olympic_gold, olympic_per_cap,
worldcup_parts, basket, cricket, rugby, baseball, davis_cup,
marathon_elite, chess, michelin, film_prod, intangible, heritage,
festivals, street_food, fast_food, mcdonalds, holidays, influencers,
yt_creators, netflix, social_media, penetration, dating_apps,
onlyfans, adult_films, porn_search, gaming, crypto_own, e_scooter

◆ Military & Infrastructure
military_pct, military_personnel, nuclear, arms_export, peacekeeping,
nato, gold_reserves, passport, line_length, airports, aviation,
car_density, motorcycle, motorization, netspeed, internet_pct,
g5_coverage, egov_index, online_gov

◆ Politics & Governance
approval, trump_approval, election_days, leader_age, youngest_leader,
parl_age, cabinet_age, independence, tz, leave, parental_leave, holidays,
union_rate, strike_days, disability, freedom_index

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Country codes (ISO 3166-1 alpha-2, lowercase):
af al dz ar au at bd be br ca cl cn co hr cu cz dk eg et fi fr de gr
hu in id ir iq ie il it jp jo kz ke kr kw lb ly my mx ma mm nl nz ng
kp no pk pe ph pl pt qa ro ru sa sg za es lk sd se ch sy tw th tr ua
ae gb us vn ye zw

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return this EXACT JSON structure:
{
  "type": "search" | "compare_chart" | "top_n" | "filter" | "unknown",
  "metric": "field_name" or null,
  "countries": ["xx", ...] or [],
  "topN": number or null,
  "explanation": "짧은 한국어 설명"
}

Type definitions:
- "search":       search for a specific country's rank or data (e.g. "한국 GDP 순위")
- "compare_chart": compare 2+ countries on a metric, or trend comparison (e.g. "한국 일본 GDP 비교")
- "top_n":         top/bottom N ranking list (e.g. "GDP 상위 10개국")
- "filter":        filter with continent/region conditions (e.g. "아시아에서 행복지수 가장 높은 나라")
- "unknown":       cannot parse query (fallback — explain in Korean)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Examples:
"한국 GDP 순위"               → {"type":"search","metric":"gdp","countries":["kr"],"topN":null,"explanation":"한국의 GDP 순위"}
"대한민국 인구"               → {"type":"search","metric":"population","countries":["kr"],"topN":null,"explanation":"한국 인구"}
"한국 일본 중국 GDP 비교"     → {"type":"compare_chart","metric":"gdp","countries":["kr","jp","cn"],"topN":null,"explanation":"한중일 GDP 비교"}
"GDP 1위부터 10위"             → {"type":"top_n","metric":"gdp","countries":[],"topN":10,"explanation":"GDP 상위 10개국"}
"아시아에서 행복지수 가장 높은 나라" → {"type":"filter","metric":"happiness","countries":[],"topN":1,"explanation":"아시아 최고 행복지수"}
"살인율 가장 낮은 나라"       → {"type":"top_n","metric":"murder","countries":[],"topN":1,"explanation":"살인율 최저 국가"}
"서울 인구"                   → {"type":"unknown","metric":null,"countries":[],"topN":null,"explanation":"국가 순위 사이트입니다. 도시 데이터는 제공하지 않아요."}
"한국 미국 일본 수출 비교"    → {"type":"compare_chart","metric":"exports","countries":["kr","us","jp"],"topN":null,"explanation":"한미일 수출 비교"}
"평균 월급 1위"               → {"type":"top_n","metric":"salary","countries":[],"topN":1,"explanation":"평균 월급 1위 국가"}
"한국 치안"                   → {"type":"search","metric":"murder","countries":["kr"],"topN":null,"explanation":"한국 살인율 (치안 대리지표)"}
"GDP per capita top 10"       → {"type":"top_n","metric":"gdp_per_capita","countries":[],"topN":10,"explanation":"1인당 GDP 상위 10개국"}

IMPORTANT:
- Return ONLY the JSON object — no markdown fences, no commentary.
- Use lowercase ISO2 country codes.
- For non-country queries (cities, people, products) return type "unknown".
- explanation MUST be in Korean.`;

// ── Main Handler ────────────────────────────────────────────────────

export default {
  async fetch(request, env) {
    // ── CORS preflight ──
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Max-Age': '86400',
        }
      });
    }

    // ── Only POST ──
    if (request.method !== 'POST') {
      return json({ error: 'POST only' }, 405);
    }

    // ── Rate limit ──
    const ip = request.headers.get('CF-Connecting-IP')
            || request.headers.get('X-Forwarded-For')
            || 'unknown';

    if (!rateLimitOk(ip)) {
      return json({
        type: 'unknown',
        explanation: '너무 많은 요청이 들어왔어요. 잠시 후 다시 시도해 주세요.',
        rate_limited: true
      }, 429);
    }

    // ── Parse body ──
    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: 'Invalid JSON body' }, 400);
    }

    const query = (body.query || '').trim();
    if (!query || query.length < 2) {
      return json({ error: 'Query too short (min 2 chars)' }, 400);
    }

    // ── Call DeepSeek ──
    const apiKey = env.DEEPSEEK_API_KEY;
    if (!apiKey) {
      return json({
        type: 'unknown',
        explanation: 'AI 검색이 아직 설정되지 않았어요. 관리자에게 문의해 주세요.',
      });
    }

    try {
      const result = await classifyQuery(query, apiKey);
      return json(result);
    } catch (e) {
      // Graceful fallback — never crash
      return json({
        type: 'unknown',
        explanation: '죄송합니다. 검색어를 이해하지 못했어요. 다른 키워드로 검색해 보세요.',
      });
    }
  }
};


// ── DeepSeek API Call ────────────────────────────────────────────────

async function classifyQuery(query, apiKey) {
  const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: 'deepseek-chat',
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: query }
      ],
      temperature: 0,
      max_tokens: 300,
      stream: false,
    })
  });

  if (!response.ok) {
    // Non-200 from DeepSeek — return graceful unknown
    console.error(`DeepSeek API error ${response.status}`);
    throw new Error(`DeepSeek API returned ${response.status}`);
  }

  const data = await response.json();
  const content = data.choices?.[0]?.message?.content || '';

  // Strip markdown code fences if present
  let cleaned = content.trim();
  if (cleaned.startsWith('```')) {
    cleaned = cleaned.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '');
  }

  // Extract JSON object
  const jsonMatch = cleaned.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    return {
      type: 'unknown',
      metric: null,
      countries: [],
      topN: null,
      explanation: '죄송합니다. 검색어를 이해하지 못했어요.',
    };
  }

  try {
    const parsed = JSON.parse(jsonMatch[0]);

    // Validate & normalize
    return {
      type: ['search', 'compare_chart', 'top_n', 'filter', 'unknown'].includes(parsed.type)
        ? parsed.type : 'unknown',
      metric: parsed.metric || null,
      countries: Array.isArray(parsed.countries) ? parsed.countries : [],
      topN: typeof parsed.topN === 'number' ? parsed.topN : null,
      explanation: parsed.explanation || '검색 결과',
    };
  } catch {
    return {
      type: 'unknown',
      metric: null,
      countries: [],
      topN: null,
      explanation: '검색 결과 파싱 오류',
    };
  }
}


// ── Helpers ──────────────────────────────────────────────────────────

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Access-Control-Allow-Origin': '*',
    }
  });
}
