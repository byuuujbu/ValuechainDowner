# Objective Value-chain Stock Agent

OVSA is a research-assistant MVP for value-chain based stock screening. It is not an investment recommendation, advisory, alarm, or automated trading service.

## Current Scope

Implemented:

- Next.js web dashboard at `apps/web`
- FastAPI backend at `apps/api`
- PostgreSQL Docker Compose setup
- `GET /health`
- SQLAlchemy/Alembic schema for assets, value-chain maps, prices, fundamentals, scores, rules, journals, portfolios, and backtests
- Sample CSV data provider
- Common-stock scoring engine
- KRW million display conversion helper for foreign financial data
- Rule engine for candidate/watch/exclude status
- Multi-industry map foundation with reviewed Space seed map
- Watchlist and journal requirement surfaces
- Sample structural backtest endpoint
- FMP and SEC EDGAR live-data provider scaffolding with safe sample fallback
- Discord command preview script without bot token access

Excluded from the MVP:

- Paid live-data production sync jobs
- Brokerage connection or order execution
- Real Discord bot deployment
- Investment recommendation wording
- AI-driven company relocation or value-chain restructuring

## Default Ports

OpenHands or other local tools may already use `3000`, so this project defaults to:

- Web: `3001`
- API: `8001`
- PostgreSQL: `5433`

## Local Setup

```powershell
Copy-Item .env.example .env
npm install
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .\apps\api[dev]
docker compose up db
```

Run API:

```powershell
npm run dev:api
```

Run Web:

```powershell
npm run dev:web
```

Open:

- Web: <http://localhost:3001>
- API health: <http://localhost:8001/health>
- Data provider status: <http://localhost:8001/data-providers/status>

## Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

## Verification

```powershell
npm run build:web
cd apps/api
python -m pytest
python -m ruff check . ..\..\scripts
```

## Database

After Docker is running:

```powershell
docker compose exec api alembic upgrade head
python scripts/seed_space_industry.py
python scripts/load_sample_assets.py
```

Local migration:

```powershell
cd apps/api
alembic upgrade head
cd ../..
```

## Sample Data

Generate sample data:

```powershell
python scripts/generate_sample_market_data.py
```

Files:

- `data/sample/assets.csv`
- `data/sample/price_daily_sample.csv`
- `data/sample/fundamentals_sample.csv`

Provider interfaces:

- `SampleCsvDataProvider`
- `FinancialModelingPrepProvider`
- `SecEdgarClient`
- `MarketDataProvider`
- `FundamentalDataProvider`
- `AssetReferenceProvider`

Sample data is deterministic development data. It is not evidence for a real investment decision.

## Live Data Provider Scaffold

Default mode remains sample data:

```powershell
DATA_PROVIDER_MODE=sample
```

FMP and SEC EDGAR are scaffolded but disabled until environment variables are configured:

```powershell
DATA_PROVIDER_MODE=fmp
FMP_API_KEY=your_fmp_key
SEC_USER_AGENT=ValuechainDowner research contact@example.com
```

Notes:

- `FMP_API_KEY` is required before Financial Modeling Prep calls are made.
- `SEC_USER_AGENT` is required before SEC EDGAR calls are made.
- `/data-providers/status` reports whether providers are configured without exposing secrets.
- `/data-providers/fmp/{ticker}/diagnostics` checks profile, price, and fundamental fetches
  for one ticker without changing the dashboard data source.
- `/data-providers/sec/{ticker}/diagnostics` checks SEC CIK lookup and annual 10-K
  fact extraction for one ticker without changing the dashboard data source.
- `/data-providers/sec/{ticker}/fundamentals` normalizes SEC companyfacts into annual
  financial rows while preserving tag, filing, accession, and original value metadata.
- `/data-providers/sec/{ticker}/metrics-preview` calculates raw metrics with sample
  prices plus SEC fundamentals to preview scoring-input impact before changing official scores.
- If credentials are absent, existing sample-data screens continue to work.

## Scoring

Run sample common-stock scoring and persist results:

```powershell
python scripts/run_scoring_job.py
```

Persisted tables:

- `calculated_metrics`
- `scores_daily`
- `score_logs`

Scoring dimensions:

- Quality: 30%
- Trend: 25%
- Risk: 15%
- Valuation: 30%

Low-quality assets receive a valuation cap. Scoring uses source currency data; KRW conversion is display/audit only.

## KRW Million Conversion

Foreign fundamentals are preserved in source currency, normally USD. KRW million display is handled separately:

```powershell
python scripts/preview_fundamentals_krw.py
```

Notes:

- The sample preview uses a fixed development rate, `USD/KRW=1350`.
- Production FX rates must come from a provider or user input.
- The LLM must not guess exchange rates or financial numbers.

## Rule Engine

Evaluate candidate/watch/exclude status:

```powershell
python scripts/evaluate_rules.py
```

Implemented gates:

- Minimum total, quality, trend, risk, valuation, and confidence scores
- Exclude after short-term surge events
- Watch flag for large one-day US-stock moves

## API Endpoints

- `GET /health`
- `GET /data-providers/status`
- `GET /data-providers/fmp/{ticker}/diagnostics`
- `GET /data-providers/sec/{ticker}/diagnostics`
- `GET /data-providers/sec/{ticker}/fundamentals`
- `GET /data-providers/sec/{ticker}/metrics-preview`
- `GET /screening/results`
- `GET /industries`
- `GET /industries/space/value-chain`
- `GET /watchlist`
- `GET /journals/requirements`
- `POST /backtests/run`

## Discord Preview

```powershell
python scripts/discord_command_preview.py
```

This only prints a sample command response. It does not access Discord credentials.

## Copy Rules

Allowed wording:

- candidate
- watch
- exclude
- journal required
- final judgment remains user responsibility

Forbidden wording:

- buy recommendation
- sell recommendation
- target price
- guaranteed return
- upside probability
