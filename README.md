# Rankerage.com

세계 국가 랭킹 비교 사이트. 순수 정적 HTML/JS — 외부 CDN 의존성 없음.

## 구조

```
rankerage/
├── docs/                    ← GitHub Pages 서비스 루트 (rankerage.com)
│   ├── index.html           메인 페이지
│   ├── data/                서비스 데이터 (JSON)
│   ├── vendor/              Tabulator 등 자체 호스팅 라이브러리
│   ├── css/ · js/ · lang/   스타일 · 스크립트 · 다국어
│   └── CNAME                커스텀 도메인 (rankerage.com)
├── public/                  초기 버전 정적 파일 (참고용)
├── scripts/                 수집·갱신 스크립트
├── worker/                  Cloudflare Worker (AI 검색)
└── .github/workflows/       정기 데이터 갱신
```

## 배포

GitHub Pages — docs/ 디렉터리가 rankerage.com 으로 서빙된다 (docs/CNAME).
데이터 갱신은 스크립트·워크플로가 JSON 문서를 갱신해 커밋·푸시하는 방식.

## 특징

- 외부 CDN 제로 — 전 세계 어디서나 동일 속도
- DB 불필요 — JSON 문서가 곧 데이터베이스
- Tabulator 5.5.2, 자체 호스팅
