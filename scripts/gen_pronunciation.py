#!/usr/bin/env python3
"""Generate Korean Hangul pronunciation for all 195 anthems"""
import json, re

with open(r"C:\Users\mathe\Desktop\rankerage\docs\data\anthems.json", encoding='utf-8') as f:
    anthems = json.load(f)

def roman_to_korean(text):
    """Convert romanized text to Hangul using phonetic mapping"""
    if not text:
        return ""
    
    # Character-by-character Hangul mapping for common European sounds
    hangul = {
        # Vowels
        'a': 'ㅏ', 'e': 'ㅔ', 'i': 'ㅣ', 'o': 'ㅗ', 'u': 'ㅜ',
        'â': 'ㅏ', 'ê': 'ㅔ', 'î': 'ㅣ', 'ô': 'ㅗ', 'û': 'ㅜ',
        'ä': 'ㅐ', 'ö': 'ㅚ', 'ü': 'ㅟ', 'å': 'ㅗ',
        'œ': 'ㅚ', 'æ': 'ㅐ',
        
        # Consonant + vowel combos (most common)
        'ba': '바', 'be': '베', 'bi': '비', 'bo': '보', 'bu': '부',
        'ca': '카', 'ce': '세', 'ci': '시', 'co': '코', 'cu': '쿠',
        'da': '다', 'de': '데', 'di': '디', 'do': '도', 'du': '두',
        'fa': '파', 'fe': '페', 'fi': '피', 'fo': '포', 'fu': '푸',
        'ga': '가', 'ge': '제', 'gi': '지', 'go': '고', 'gu': '구',
        'ha': '하', 'he': '헤', 'hi': '히', 'ho': '호', 'hu': '후',
        'ja': '자', 'je': '제', 'ji': '지', 'jo': '조', 'ju': '주',
        'ka': '카', 'ke': '케', 'ki': '키', 'ko': '코', 'ku': '쿠',
        'la': '라', 'le': '레', 'li': '리', 'lo': '로', 'lu': '루',
        'ma': '마', 'me': '메', 'mi': '미', 'mo': '모', 'mu': '무',
        'na': '나', 'ne': '네', 'ni': '니', 'no': '노', 'nu': '누',
        'pa': '파', 'pe': '페', 'pi': '피', 'po': '포', 'pu': '푸',
        'ra': '라', 're': '레', 'ri': '리', 'ro': '로', 'ru': '루',
        'sa': '사', 'se': '세', 'si': '시', 'so': '소', 'su': '수',
        'ta': '타', 'te': '테', 'ti': '티', 'to': '토', 'tu': '투',
        'va': '바', 've': '베', 'vi': '비', 'vo': '보', 'vu': '부',
        'wa': '와', 'we': '웨', 'wi': '위', 'wo': '워',
        'xa': '샤', 'xe': '셰', 'xi': '시', 'xo': '쇼', 'xu': '슈',
        'ya': '야', 'ye': '예', 'yi': '이', 'yo': '요', 'yu': '유',
        'za': '자', 'ze': '제', 'zi': '지', 'zo': '조', 'zu': '주',
        
        # Single consonants (word-final)
        'b': '브', 'c': '크', 'd': '드', 'f': '프', 'g': '그',
        'h': '흐', 'j': '즈', 'k': '크', 'l': 'ㄹ', 'm': 'ㅁ',
        'n': 'ㄴ', 'p': '프', 'q': '크', 'r': '르', 's': '스',
        't': '트', 'v': '브', 'w': '우', 'x': '스', 'z': '즈',
        
        # Special clusters
        'ch': '치', 'sh': '시', 'th': '트', 'ph': '프', 'gh': '그',
        'sch': '슈', 'tsch': '츠', 'tch': '치', 'dch': '즈',
        'ng': '응', 'nk': '응크', 'nt': '은트', 'nd': '은드',
        'st': '스트', 'sp': '스프', 'sk': '스크',
        'str': '스트', 'spr': '스프',
        'br': '브르', 'cr': '크르', 'dr': '드르', 'fr': '프르',
        'gr': '그르', 'pr': '프르', 'tr': '트르', 'wr': '우르',
        'bl': '블', 'cl': '클', 'fl': '플', 'gl': '글', 'pl': '플', 'sl': '슬',
        
        # Vowel combinations
        'ai': '아이', 'ei': '에이', 'oi': '오이', 'ui': '우이',
        'au': '아우', 'eu': '에우', 'ou': '오우',
        'ea': '이아', 'ee': '이', 'oo': '우',
        'ie': '이에', 'ia': '이아', 'io': '이오', 'iu': '이우',
        
        # Common endings
        'tion': '션', 'sion': '전', 'ment': '먼트', 'ness': '네스',
        'land': '란드', 'berg': '베르크', 'burg': '부르크',
        
        # Punctuation
        ',': ',', '.': '.', '!': '!', '?': '?', "'": "'",
        '-': '-', ' ': ' ', '\n': '\n',
    }
    
    result = []
    i = 0
    text_lower = text.lower()
    
    while i < len(text_lower):
        # Try 4-char sequences first
        matched = False
        for length in [4, 3, 2, 1]:
            if i + length <= len(text_lower):
                chunk = text_lower[i:i+length]
                if chunk in hangul:
                    result.append(hangul[chunk])
                    i += length
                    matched = True
                    break
        
        if not matched:
            # Keep original character
            result.append(text[i])
            i += 1
    
    return ''.join(result)


updated = 0
for code, anthem in anthems.items():
    # Skip if already has proper pronunciation (not placeholder)
    if anthem.get('pronunciation_ko') and '(발음 작업 중)' not in anthem.get('pronunciation_ko', ''):
        continue
    
    lyrics = anthem.get('lyrics', '')
    if lyrics and len(lyrics) > 3:
        # Generate Korean pronunciation using phonetic mapping
        pronunciation = roman_to_korean(lyrics)
        anthem['pronunciation_ko'] = pronunciation
        updated += 1
    else:
        anthem['pronunciation_ko'] = '(발음 작업 중)'

with open(r"C:\Users\mathe\Desktop\rankerage\docs\data\anthems.json", 'w', encoding='utf-8') as f:
    json.dump(anthems, f, ensure_ascii=False, indent=2)

# Show a few samples
print(f"Updated: {updated} anthems")
total = len(anthems) - updated
print(f"Already had + placeholder: {anthems.get('KR', {}).get('pronunciation_ko','')[:40]}...")
print(f"Sample FR: {anthems.get('FR',{}).get('pronunciation_ko','')[:60]}...")
print(f"Sample DE: {anthems.get('DE',{}).get('pronunciation_ko','')[:60]}...")
print(f"Sample JP: {anthems.get('JP',{}).get('pronunciation_ko','')[:40]}...")
