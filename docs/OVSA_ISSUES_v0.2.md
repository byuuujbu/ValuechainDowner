# OVSA Issues v0.2

작성일: 2026-05-31

이 문서는 `OVSA_PRD_v0.2.md`를 구현 가능한 작업 단위로 분해한 초안이다. 실제 개발은 사용자 최종 승인 후 시작한다.

## Issue 001. Establish OVSA Monorepo Skeleton

Type: AFK

Blocked by: None

User stories covered: 25, 26

### What to build

Create the project skeleton with a Next.js web app, FastAPI API app, PostgreSQL Docker Compose setup, environment example, health check endpoint, README, and agent guidance files. Do not implement scoring, rules, UI workflows, database schema, or sample data beyond what is necessary for the skeleton to run.

### Acceptance criteria

- [ ] Web, API, and PostgreSQL can be started locally.
- [ ] API exposes a working health check.
- [ ] README explains local run instructions.
- [ ] Project guidance states that investment recommendation language is forbidden.
- [ ] No scoring, rule, journal, backtest, or industry map feature is implemented in this issue.

## Issue 002. Add Local Planning Baseline and Agent Context

Type: AFK

Blocked by: 001

User stories covered: 24, 25, 26

### What to build

Add the approved PRD, decision record, issue plan, and agent operating context into the repo. Configure local markdown issue tracking unless a remote tracker is later selected.

### Acceptance criteria

- [ ] PRD v0.2 is available in project docs.
- [ ] Decision record v0.2 is available in project docs.
- [ ] Issue breakdown v0.2 is available in project docs.
- [ ] Agent guidance documents identify the issue tracker, triage labels, and domain docs layout.

## Issue 003. Seed Core Data Model for Assets, Industries, and Value-chain

Type: AFK

Blocked by: 001, 002

User stories covered: 13, 14, 15, 16, 18

### What to build

Implement the initial schema and seed path for assets, industries, Value-chain nodes, and asset-to-node mappings. Support multiple industries, multiple node mappings per company, and human review status for Value-chain data.

### Acceptance criteria

- [ ] Assets, industries, Value-chain nodes, and asset mappings can be stored.
- [ ] A company can map to multiple nodes.
- [ ] Mapping role supports primary, secondary, and optional.
- [ ] Human review status exists and unreviewed AI drafts are not shown as approved map data.
- [ ] Space industry seed data can be loaded.

## Issue 004. Implement Sample Data and Mock Provider Interfaces

Type: AFK

Blocked by: 003

User stories covered: 17, 18, 20

### What to build

Add sample assets, price history, fundamentals, and provider interfaces for market data and fundamentals. Keep real data adapters out of scope while preserving extension points.

### Acceptance criteria

- [ ] Sample assets include common stocks, ETFs, benchmarks, gold proxy, and BTC proxy.
- [ ] Sample price data supports at least 260 trading days.
- [ ] Sample fundamentals include the fields needed for v0.1 common stock scoring.
- [ ] Mock/Sample Provider returns data through stable interfaces.
- [ ] ETF assets are identifiable and not routed through the common stock total score model.

## Issue 005. Implement Common Stock Scoring and Score Logs

Type: AFK

Blocked by: 004

User stories covered: 4, 5, 6, 7, 19, 20

### What to build

Implement quality, trend, risk, valuation, total score, score confidence, comparison group logs, and calculation logs for common stocks using deterministic Python code.

### Acceptance criteria

- [ ] Total score equals quality 30%, trend 25%, risk 15%, valuation 30%.
- [ ] Strategic Fit Score is stored/displayed separately and never included in total score.
- [ ] Risk minimum criteria can block candidate status.
- [ ] Comparison group details are logged.
- [ ] N/A, reverse scoring, and insufficient comparison group cases are handled.
- [ ] Unit tests cover scoring formulas and edge cases.

## Issue 006. Implement Candidate Status and Rule Engine

Type: AFK

Blocked by: 005

User stories covered: 1, 2, 3, 6, 8, 9, 10

### What to build

Implement configuration-driven rules that convert scores, confidence, surge checks, volatility events, and position events into `후보 가능`, `관망`, or `제외` statuses with persisted reasons.

### Acceptance criteria

- [ ] Candidate status is limited to `후보 가능`, `관망`, and `제외`.
- [ ] 5-day +25% and 20-day +50% moves block new candidate status.
- [ ] Same-day +10% move blocks same-day new candidate status.
- [ ] Korea limit-up/down cooldown and US ±15% cooldown rules are represented.
- [ ] -10% loss produces a review alert, not a sell instruction.
- [ ] Rule events are stored with reasons.
- [ ] Tests cover each active rule.

## Issue 007. Build Dashboard Review Surface

Type: AFK

Blocked by: 005, 006

User stories covered: 1, 2, 3, 4, 5, 8, 12

### What to build

Build the dashboard as the first screen. Show 3-day screening results, candidate states, rule events, score summaries, and journal-required tasks without using investment recommendation language.

### Acceptance criteria

- [ ] Dashboard is the default landing screen.
- [ ] Candidate lists are grouped by `후보 가능`, `관망`, and `제외`.
- [ ] Total score and four sub-scores are visible together.
- [ ] Rule event reasons are visible.
- [ ] Forbidden investment recommendation phrases are not used.

## Issue 008. Build Multi-industry Map Shell and Space Map

Type: HITL

Blocked by: 003, 005

User stories covered: 13, 14, 15, 16

### What to build

Build the Industry Map tab with a multi-industry shell and detailed Space map. Show reviewed Value-chain nodes, company nodes, mapping roles, Strategic Fit Score emphasis, hover cards, and click detail panels.

### Acceptance criteria

- [ ] Industry selector includes Space, AI, Semiconductor, Medicine/Bio, and Robotics.
- [ ] Only Space has detailed v0.1 data.
- [ ] Other industries show a non-final placeholder state.
- [ ] Space map is not hardcoded in a way that prevents future industries.
- [ ] Unreviewed AI drafts are not shown as approved map data.
- [ ] Strategic Fit Score is visually separate from total investment score.

## Issue 009. Implement Watchlist and Journal Workflow

Type: AFK

Blocked by: 006, 007

User stories covered: 10, 11, 12

### What to build

Implement watchlist add/remove, review notes, mandatory journal prompts for risky actions, and post-sale review fields.

### Acceptance criteria

- [ ] Watchlist items can be added and removed.
- [ ] Watchlist items show current status and reasons.
- [ ] Losing-position add actions require a journal update.
- [ ] Continuing review for `관망` or `제외` items requires a reason.
- [ ] Post-sale review is available for every sale record.
- [ ] Post-sale review is mandatory after rule-event-related positions.

## Issue 010. Implement Sample Backtest Structural Check

Type: AFK

Blocked by: 005, 006, 009

User stories covered: 21, 22, 23

### What to build

Implement sample-data backtest flow for 3-day screening and 2-week rebalancing review simulation. Report assumptions, transaction cost assumptions, strategy return, MDD, benchmark comparison, and downside defense.

### Acceptance criteria

- [ ] Screening cadence is every 3 days.
- [ ] Rebalancing review cadence is every 2 weeks.
- [ ] Results include strategy return, MDD, benchmark comparison, and downside defense.
- [ ] Output clearly states that it is a sample-based structural check.
- [ ] Output does not imply performance guarantee.

## Issue 011. Add Discord Command Surface

Type: AFK

Blocked by: 007, 008, 009, 010

User stories covered: 24

### What to build

Add Discord command and alert integration after core backend and web flows are stable. Discord should call backend APIs and summarize stored results without creating scores or recommendations.

### Acceptance criteria

- [ ] Discord commands call backend workflows rather than implementing calculations.
- [ ] Responses summarize candidate status, score data, and rule reasons.
- [ ] Responses link back to Web App details where available.
- [ ] Responses avoid investment recommendation language.

## 승인 확인 필요

`to-issues` 절차상, 위 분해안을 실제 개별 이슈로 등록하기 전에 아래를 확인해야 한다.

- 이슈 단위가 너무 크거나 작지 않은가?
- 의존 관계가 맞는가?
- HITL/AFK 구분이 맞는가?
- 병합하거나 더 쪼갤 이슈가 있는가?
