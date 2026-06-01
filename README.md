# Objective Value-chain Stock Agent

OVSA는 투자 추천/자문/일임/자동매매 서비스가 아니다. 객관 지표 기반 후보 검토, 기록, 리스크 점검, 감정매매 방지를 돕는 리서치 보조 도구다.

## Phase 1 범위

포함:

- `apps/web`: Next.js + TypeScript
- `apps/api`: FastAPI + Python
- PostgreSQL Docker Compose
- `.env.example`
- `GET /health`
- 로컬 실행 방법

제외:

- 점수 계산
- Rule Engine
- 산업맵 UI
- 관심종목
- 투자일지
- 백테스트
- Discord

## 요구사항

- Node.js 20+
- Python 3.11+
- Docker Desktop

## 기본 포트

OpenHands 등 다른 로컬 도구와 충돌하지 않도록 OVSA는 다음 포트를 기본으로 사용한다.

- Web: `3001`
- API: `8001`
- PostgreSQL: `5433`

## 로컬 실행

```powershell
Copy-Item .env.example .env
npm install
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -e .\\apps\\api[dev]
docker compose up db
```

별도 터미널에서 API:

```powershell
npm run dev:api
```

별도 터미널에서 Web:

```powershell
npm run dev:web
```

접속:

- Web: <http://localhost:3001>
- API health: <http://localhost:8001/health>

## Docker 실행

```powershell
Copy-Item .env.example .env
docker compose up --build
```

## 검증

```powershell
npm run lint:web
npm run build:web
npm run test:api
```

## DB 마이그레이션

Docker 실행 후:

```powershell
docker compose exec api alembic upgrade head
python scripts/seed_space_industry.py
python scripts/load_sample_assets.py
```

로컬 Python으로 migration 실행:

```powershell
cd apps/api
alembic upgrade head
cd ../..
```

## 샘플 데이터

샘플 데이터 생성:

```powershell
python scripts/generate_sample_market_data.py
```

생성 파일:

- `data/sample/assets.csv`
- `data/sample/price_daily_sample.csv`
- `data/sample/fundamentals_sample.csv`

샘플 Provider:

- `SampleCsvDataProvider`
- `MarketDataProvider`
- `FundamentalDataProvider`
- `AssetReferenceProvider`

주의: 샘플 가격/재무 데이터는 개발 검증용 더미 데이터다. 실제 투자 판단 근거가 아니다.

## 점수 계산

샘플 데이터 기준 개별주 점수 계산과 DB 저장:

```powershell
python scripts/run_scoring_job.py
```

저장 대상:

- `calculated_metrics`
- `scores_daily`
- `score_logs`

주의: 이 단계는 계산 엔진 검증이다. 후보 가능/관망/제외 판정과 Rule Engine은 아직 구현하지 않았다.

## 문구 원칙

금지:

- 매수 추천
- 매도 추천
- 사세요
- 파세요
- 수익 가능성
- 상승 확률
- 목표가

허용:

- 후보 가능
- 관망
- 제외
- 투자일지 작성 필요
- 최종 판단은 사용자 책임
