import json
import re
import requests

# Read token
with open(r'C:\Users\mathe\AppData\Local\hermes\.env', 'r') as f:
    for line in f:
        if line.startswith('TELEGRAM_BOT_TOKEN='):
            token = line.strip().split('=', 1)[1]
            break

print(f"Token length: {len(token)}")

# First, get updates to find chat IDs
url = f"https://api.telegram.org/bot{token}/getUpdates"
resp = requests.get(url, timeout=10)
data = resp.json()
print(f"getUpdates ok: {data.get('ok')}")

if data.get('ok'):
    results = data.get('result', [])
    print(f"Number of updates: {len(results)}")
    
    # Collect unique chat IDs
    chat_ids = {}
    for update in results:
        msg = update.get('message', {}) or update.get('channel_post', {})
        chat = msg.get('chat', {})
        cid = chat.get('id')
        if cid:
            chat_type = chat.get('type', 'unknown')
            title = chat.get('title', '') or f"{chat.get('first_name', '')} {chat.get('last_name', '')}"
            username = chat.get('username', '')
            if cid not in chat_ids:
                chat_ids[cid] = {'type': chat_type, 'title': title.strip(), 'username': username}
    
    for cid, info in chat_ids.items():
        print(f"Chat ID: {cid}, type: {info['type']}, title: {info['title']}")
else:
    print(f"Error: {data}")
