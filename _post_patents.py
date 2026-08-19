# -*- coding: utf-8 -*-
"""Rankerage daily post: 특허 (patents) top 3 — 인구 100만 명당 특허 출원."""
import json
import requests

ENV_PATH = r'C:\Users\mathe\AppData\Local\hermes\.env'
DATA_PATH = r'C:\Users\mathe\Desktop\rankerage\docs\data\countries.json'

# ---- Load token & allowed users from Hermes .env ----
token = None
allowed_users = []
with open(ENV_PATH, 'r', encoding='utf-8') as f:
    for line in f:
        s = line.strip()
        if s.startswith('TELEGRAM_BOT_TOKEN=') and not s.startswith('#'):
            token = s.split('=', 1)[1]
        elif s.startswith('TELEGRAM_ALLOWED_USERS=') and not s.startswith('#'):
            allowed_users = [u.strip() for u in s.split('=', 1)[1].split(',') if u.strip()]

# ---- Verify data from countries.json (single source of truth) ----
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    countries = json.load(f)
top = sorted([c for c in countries if c.get('patents') is not None],
             key=lambda c: -c['patents'])[:3]
assert [c['country_name_en'] for c in top] == ['South Korea', 'Japan', 'China'], \
    f'Unexpected top-3 {[c["country_name_en"] for c in top]}, aborting rather than posting wrong data'
assert top[0]['patents'] == 2791
assert top[1]['patents'] == 1999
assert top[2]['patents'] == 1278

# ---- Compose Korean message ----
message = (
    "🌍 오늘의 세계 순위: 특허\n\n"
    "🥇 🇰🇷 대한민국 — 2,791건\n"
    "🥈 🇯🇵 일본 — 1,999건\n"
    "🥉 🇨🇳 중국 — 1,278건\n\n"
    "💡 놀라운 사실: 인구 100만 명당 특허 출원 수에서 대한민국이 세계 1위! "
    "인구가 각각 2.5배, 25배 많은 일본과 중국을 모두 제쳤어요. 작지만 강한 K-혁신의 힘입니다.\n\n"
    "#랭커리지 #세계순위 #특허"
)

print(f'Message length: {len(message)} chars (limit 500)')
print('---MESSAGE---')
print(message)
print('---END---')
assert len(message) < 500, 'Message exceeds 500 chars!'

# ---- Send via Telegram API if token & recipient available ----
if not token or token == '***':
    print('\n[LOG] TELEGRAM_BOT_TOKEN not configured. Message logged above only.')
elif not allowed_users:
    print('\n[LOG] No TELEGRAM_ALLOWED_USERS configured. Message logged above only.')
else:
    sent = False
    for uid in allowed_users:
        try:
            r = requests.post(
                f'https://api.telegram.org/bot{token}/sendMessage',
                data={'chat_id': uid, 'text': message},
                timeout=15,
            )
            j = r.json()
            if j.get('ok'):
                print(f'\n[SENT] Delivered to chat_id={uid} (message_id={j["result"]["message_id"]})')
                sent = True
                break
            else:
                print(f'\n[FAIL] chat_id={uid}: {j.get("description")}')
        except Exception as e:
            print(f'\n[ERROR] chat_id={uid}: {e}')
    if not sent:
        print('\n[LOG] Telegram send failed for all recipients. Message logged above.')
