# Read the full .env and look for telegram-related lines
with open(r'C:\Users\mathe\AppData\Local\hermes\.env', 'r') as f:
    for i, line in enumerate(f):
        if 'telegram' in line.lower() or 'TELEGRAM' in line or 'CHANNEL' in line:
            # Don't print token values but show keys
            if '=' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip()
                print(f'Line {i}: {key}=<set>')
            else:
                print(f'Line {i}: {line.rstrip()}')
