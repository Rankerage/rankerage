# Rankerage.com

세계 국가 랭킹 비교 사이트. 순수 정적 HTML/JS — 외부 CDN 의존성 없음.

## 구조

```
rankerage/
├── public/                  ← 서비스할 정적 파일
│   ├── index.html           메인 페이지
│   ├── vendor/              Tabulator 라이브러리 (자체 호스팅)
│   │   ├── tabulator.min.js   (383KB)
│   │   └── tabulator.min.css  (25KB)
│   ├── css/style.css        커스텀 스타일
│   ├── js/table.js          테이블 설정
│   └── data/countries.json  국가 데이터 (199개국)
├── data/                    원본 CSV/Excel
├── scripts/                 변환 스크립트
└── experiments/             서브 프로젝트
```

## 화웨이 클라우드 배포

```bash
# 1. 서버에 업로드
scp -r public/ root@159.138.109.172:/var/www/rankerage/

# 2. Nginx 설정
server {
    listen 80;
    server_name rankerage.com;
    root /var/www/rankerage/public;
    index index.html;

    # gzip 압축
    gzip on;
    gzip_types text/css application/javascript application/json;
}
```

## 특징

- 외부 CDN 제로 — 전 세계 어디서나 동일 속도
- 전체 사이트 크기: 744KB (사진 한 장 수준)
- DB 불필요 — JSON 파일 하나가 데이터베이스
- Tabulator 5.5.2, 자체 호스팅
