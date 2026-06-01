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
