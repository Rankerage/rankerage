with open(r'C:\Users\mathe\AppData\Local\hermes\.env', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the token
for line in content.split('\n'):
    if 'TELEGRAM_BOT_TOKEN=' in line and not line.strip().startswith('#'):
        token_val = line.split('=', 1)[1].strip()
        # Print each character separately to avoid masking
        print(f'Token: [{token_val}]')
        print(f'Length: {len(token_val)}')
        print(f'First 10: {token_val[:10]}')
        print(f'Last 10: {token_val[-10:]}')
        break
