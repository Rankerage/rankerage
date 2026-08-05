with open(r'C:\Users\mathe\AppData\Local\hermes\.env', 'r') as f:
    for line in f:
        if 'TELEGRAM' in line and not line.strip().startswith('#'):
            print(line.strip())
