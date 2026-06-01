# AGENTS.md

## Project Scope

Work from `docs/OVSA_PRD_v0.2.md` and `docs/OVSA_DECISIONS_v0.2.md`.

Phase 1 only includes project skeleton, Docker Compose, env example, health check, README, and agent guidance. Do not implement scoring, rules, industry map UI, watchlist, journal, backtest, or Discord during Phase 1.

## Product Guardrails

OVSA is not an investment recommendation, advisory, discretionary management, auto-trading, or performance guarantee product.

Never use:

- Buy recommendation language
- Sell recommendation language
- Profit guarantee language
- Target price language
- LLM-generated prices, financial data, scores, or candidate decisions

Use review-state language only:

- 후보 가능
- 관망
- 제외
- 투자일지 작성 필요
- 최종 판단은 사용자 책임

## Agent skills

### Issue tracker

Issues live in GitHub Issues for `byuuujbu/ValuechainDowner`.

### Triage labels

Default labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.

### Domain docs

Single-context docs layout. Use root docs and future `CONTEXT.md` / `docs/adr/` when added.
