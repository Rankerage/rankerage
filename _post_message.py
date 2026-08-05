import requests
import json

# Read token
with open(r'C:\Users\mathe\AppData\Local\hermes\.env', 'r') as f:
    for line in f:
        if line.startswith('TELEGRAM_BOT_TOKEN='):
            token = line.strip().split('=', 1)[1]
            break

# Korean message about coffee consumption
message = """🌍 오늘의 세계 순위: 1인당 커피 소비량

🥇 🇫🇮 핀란드 - 12.0kg
🥈 🇳🇴 노르웨이 - 9.9kg
🥉 🇮🇸 아이슬란드 - 9.0kg

놀라운 사실: 핀란드인이 1년에 마시는 커피는 무려 12kg! 1인당 하루 3~4잔 꼴입니다. 북유럽 3국이 커피 소비량 TOP3를 싹쓸이했어요. 추운 날씨 덕분일까요? 참고로 커피 공화국 한국은 1.8kg로 39위!

#랭커리지 #세계순위 #커피소비량"""

print(f"Message length: {len(message)} chars")
print("---MESSAGE---")
print(message)
print("---END MESSAGE---")

# Try to send to any available chat from getUpdates (empty, so skip)
# Since we have no chat ID, let's log it
print("\nNo Telegram chat ID available. Message logged above.")
print("The cron system will deliver this response automatically.")
