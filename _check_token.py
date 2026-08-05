import os

# Try env vars first
token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
if token:
    print(f'ENV token length: {len(token)}')
else:
    # Read from .env file
    with open(r'C:\Users\mathe\AppData\Local\hermes\.env', 'r') as f:
        for line in f:
            if 'TELEGRAM_BOT_TOKEN' in line and not line.strip().startswith('#'):
                token = line.strip().split('=', 1)[1] if '=' in line else ''
                print(f'Token found, length: {len(token)}')
                break

# Also check for channel
with open(r'C:\Users\mathe\AppData\Local\hermes\.env', 'r') as f:
    for line in f:
        if 'TELEGRAM_HOME_CHANNEL' in line and not line.strip().startswith('#'):
            print(f'Channel found: {line.strip()}')
            break
