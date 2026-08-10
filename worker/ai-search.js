/**
 * rankerage.com — AI-powered search + election news summarizer
 * Cloudflare Worker (ES Modules syntax)
 *
 * POST /  { "query": "한국 GDP 순위" }     → search action
 * POST /  { "action": "election", "country": "Zambia", "title": "Presidency" } → 10-line summary
 *
 * Deploy: npx wrangler deploy
 * Secret:  npx wrangler secret put DEEPSEEK_API_KEY
 */

// ── Rate Limiter ─────────────────────────────────────────────────────
const RL_WINDOW_MS = 60_000;
const RL_MAX        = 30;
const rateStore = new Map();

function rateLimitOk(ip) {
  const now = Date.now();
  const entry = rateStore.get(ip);
  if (!entry || now - entry.windowStart > RL_WINDOW_MS) {
    rateStore.set(ip, { count: 1, windowStart: now });
    return true;
  }
  if (entry.count >= RL_MAX) return false;
  entry.count++;
  return true;
}

export async function scheduled(controller, env, ctx) {
  const now = Date.now();
  for (const [ip, entry] of rateStore) {
    if (now - entry.windowStart > RL_WINDOW_MS * 2) rateStore.delete(ip);
  }
}

// ── System Prompt (search) ───────────────────────────────────────────
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

RESPONSE FORMAT (exactly this — no extra text):
{"type":"search|compare_chart|top_n|filter|unknown","metric":"field","countries":["kr"],"topN":null,"explanation":"한국의 GDP 순위"}

COUNTRY CODES: use 2-letter ISO codes (kr, us, jp, cn, gb, fr, de, etc.)
For "한국" or "Korea" use "kr". For "미국" or "USA" use "us".
For "세계 최고" or "world top" use type "top_n" with a number.
For comparisons like "한국 vs 일본" use type "compare_chart".
If the user wrote in Korean, respond in Korean in the explanation field.`;

// ── Fetch Handler ─────────────────────────────────────────────────────
export default {
  async fetch(request, env, ctx) {
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

    if (request.method !== 'POST') return json({ error: 'POST only' }, 405);

    const ip = request.headers.get('CF-Connecting-IP')
            || request.headers.get('X-Forwarded-For')
            || 'unknown';

    if (!rateLimitOk(ip)) {
      return json({ type: 'unknown', explanation: '너무 많은 요청이 들어왔어요. 잠시 후 다시 시도해 주세요.', rate_limited: true }, 429);
    }

    let body;
    try { body = await request.json(); } catch { return json({ error: 'Invalid JSON body' }, 400); }

    // ── Election summary endpoint ──
    if (body.action === 'election') {
      const country = (body.country || '').trim();
      const title = (body.title || '').trim();
      if (!country) return json({ error: 'country required' }, 400);
      const apiKey = env.DEEPSEEK_API_KEY;
      if (!apiKey) return json({ summary: 'AI 서비스가 아직 설정되지 않았어요.', error: true });
      try {
        const result = await summarizeElection(country, title, apiKey);
        return json(result);
      } catch (e) {
        return json({ summary: '죄송합니다. 뉴스를 가져오지 못했어요.', error: true });
      }
    }

    // ── Search endpoint ──
    const query = (body.query || '').trim();
    if (!query || query.length < 2) return json({ error: 'Query too short (min 2 chars)' }, 400);

    const apiKey = env.DEEPSEEK_API_KEY;
    if (!apiKey) {
      return json({ type: 'unknown', explanation: 'AI 검색이 아직 설정되지 않았어요.' });
    }

    try {
      const result = await classifyQuery(query, apiKey);
      return json(result);
    } catch (e) {
      return json({ type: 'unknown', explanation: '죄송합니다. 검색어를 이해하지 못했어요.' });
    }
  }
};

// ── Election News Summarizer ──────────────────────────────────────────
async function summarizeElection(country, title, apiKey) {
  const prompt = `Search for the latest news about the upcoming or recent election in ${country}${title ? ' (' + title + ')' : ''}. Find:
- Latest opinion polls and approval ratings (with percentages if available)
- Key candidates and their platforms
- Major campaign issues
- Predicted outcomes
- Links to 2-3 most relevant recent news articles

Respond as JSON: {"summary": "10-line Korean summary", "links": [{"title": "...", "url": "https://..."}]}
Keep summary within 10 lines. Include specific numbers. Use Korean.`;

  const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: 'deepseek-chat',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.5,
      max_tokens: 500,
      web_search: true,
    })
  });

  if (!response.ok) throw new Error(`DeepSeek API returned ${response.status}`);

  const data = await response.json();
  const content = data.choices?.[0]?.message?.content || '{}';
  
  // Parse JSON response
  let result = { summary: '뉴스를 가져오지 못했어요.', links: [] };
  try {
    const cleaned = content.trim().replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '');
    const parsed = JSON.parse(cleaned.match(/\{[\s\S]*\}/)?.[0] || '{}');
    result.summary = parsed.summary || result.summary;
    result.links = Array.isArray(parsed.links) ? parsed.links : [];
  } catch (e) {
    result.summary = content.trim().substring(0, 500) || result.summary;
  }
  
  return result;
}

// ── Search Classifier ─────────────────────────────────────────────────
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
      max_tokens: 200,
      response_format: { type: 'json_object' }
    })
  });

  if (!response.ok) throw new Error(`DeepSeek API returned ${response.status}`);

  const data = await response.json();
  const content = data.choices?.[0]?.message?.content || '';

  let cleaned = content.trim();
  if (cleaned.startsWith('```')) {
    cleaned = cleaned.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '');
  }

  const jsonMatch = cleaned.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    return { type: 'unknown', metric: null, countries: [], topN: null, explanation: '죄송합니다. 검색어를 이해하지 못했어요.' };
  }

  try {
    const parsed = JSON.parse(jsonMatch[0]);
    return {
      type: ['search', 'compare_chart', 'top_n', 'filter', 'unknown'].includes(parsed.type) ? parsed.type : 'unknown',
      metric: parsed.metric || null,
      countries: Array.isArray(parsed.countries) ? parsed.countries : [],
      topN: typeof parsed.topN === 'number' ? parsed.topN : null,
      explanation: parsed.explanation || '검색 결과',
    };
  } catch {
    return { type: 'unknown', metric: null, countries: [], topN: null, explanation: '검색 결과 파싱 오류' };
  }
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Access-Control-Allow-Origin': '*',
    }
  });
}
