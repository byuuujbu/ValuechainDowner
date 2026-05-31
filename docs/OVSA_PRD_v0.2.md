# OVSA PRD v0.2

작성일: 2026-05-31

## Problem Statement

개인 투자자는 산업과 기업의 장기적 매력을 이해하더라도, 실제 의사결정 시 급등주 추격, 손실 중 추가매수, 매수 이유 없는 진입, 손절 실패 같은 감정적 행동에 흔들리기 쉽다. 기존 도구들은 가격 차트, 뉴스, 재무 지표를 흩어진 형태로 보여주거나 투자 추천처럼 보이는 결론을 제공한다. 사용자는 추천이 아니라, 객관 지표와 룰에 기반해 후보를 검토하고 자신의 행동을 기록·교정할 수 있는 리서치 보조 도구가 필요하다.

## Solution

OVSA v0.1은 개인/가족/지인용 리서치 보조 웹앱이다. 제품의 중심은 객관 지표 기반 후보 검토와 감정매매 방지이며, 우주 산업 Value-chain 맵은 후보 탐색과 산업 이해를 돕는 주요 탭으로 제공한다.

OVSA는 투자 추천/자문/일임/자동매매 서비스가 아니다. 모든 상태값은 투자 행동 지시가 아니라 검토 상태이며, 최종 판단과 주문 실행은 사용자 책임이다.

v0.1은 샘플 데이터와 Mock/Sample Provider로 시작한다. Backend 계산 엔진이 점수와 룰 결과를 만들고, LLM은 저장된 계산 결과와 룰 이벤트만 설명한다. LLM은 숫자, 가격, 재무 데이터, 후보 판정을 임의로 만들지 않는다.

## User Stories

1. As a personal investor, I want to see objective candidate statuses, so that I can avoid acting on impulse.
2. As a personal investor, I want candidate status to mean review eligibility, so that I do not confuse it with a buy recommendation.
3. As a personal investor, I want every asset to show `후보 가능`, `관망`, or `제외`, so that I can understand the review state quickly.
4. As a personal investor, I want total score and the four sub-scores shown together, so that I do not overtrust a single number.
5. As a personal investor, I want score calculation logs, so that I can understand why a score was produced.
6. As a personal investor, I want risk minimum criteria to block candidate status, so that high total scores cannot bypass fragile risk conditions.
7. As a personal investor, I want Strategic Fit Score separated from investment score, so that strategically interesting companies do not bypass objective filters.
8. As a personal investor, I want short-term surge rules to block new candidate status, so that I avoid chasing price spikes.
9. As a personal investor, I want -10% loss alerts framed as review prompts, so that I revisit my thesis without receiving an automatic sell instruction.
10. As a personal investor, I want journal prompts when adding to a losing position, so that I must restate my thesis before acting.
11. As a personal investor, I want post-sale reviews, so that I can learn whether my original thesis and invalidation conditions worked.
12. As a personal investor, I want a dashboard first screen, so that I can see screening results, rule events, and journal tasks before exploring maps.
13. As a personal investor, I want an Industry Map tab, so that I can explore companies through a Value-chain view.
14. As a personal investor, I want the space industry map implemented first, so that the MVP has one concrete domain.
15. As a product owner, I want the Industry Map architecture to support AI, semiconductor, medicine/bio, and robotics later, so that the UI is not hardcoded to space.
16. As a product owner, I want AI-generated Value-chain drafts to require human review before display, so that unverified interpretation does not affect the product.
17. As a product owner, I want sample data and mock providers first, so that scoring, rules, UI, and backtest flows can be verified before real data integration.
18. As a product owner, I want Provider Interfaces, so that real Korean and US market data adapters can be added later.
19. As a product owner, I want comparison groups logged, so that score changes can be explained and later refined.
20. As a product owner, I want ETFs included as benchmarks and watchlist items but excluded from the common stock total score model, so that invalid financial metrics are not forced onto ETFs.
21. As a product owner, I want screening every 3 days, so that candidate changes are monitored more often than weekly.
22. As a product owner, I want rebalancing review every 2 weeks, so that the app prompts review without implying automatic trading.
23. As a product owner, I want backtests framed as sample-based structural checks, so that users do not mistake them for performance guarantees.
24. As a product owner, I want Discord implemented last, so that it only calls stable backend workflows.
25. As a developer, I want Phase 1 to be only the project skeleton, so that later scoring and rules are not mixed into setup work.
26. As a developer, I want phase approval gates, so that sensitive scoring, rules, UI language, and backtest assumptions are reviewed before moving forward.

## Implementation Decisions

- Build a monorepo with `apps/web`, `apps/api`, shared docs, sample data, scripts, and future shared types.
- Frontend uses Next.js and TypeScript.
- Backend uses FastAPI and Python.
- PostgreSQL is the primary database.
- Data processing and scoring use Python code, not LLM-generated values.
- Phase 1 includes only project skeleton, Docker Compose, environment examples, health check, README, and project guidance files.
- The first screen is Dashboard, not the Industry Map.
- Main navigation is Dashboard, Industry Map, Watchlist, Journal, Backtest, Settings.
- Industry Map supports multiple industries. Space is the only detailed v0.1 industry.
- Space Value-chain nodes are seeded and human-reviewed before display.
- AI may draft Value-chain structures and company placements, but auto-application is out of scope.
- Total score for common stocks is quality 30%, trend 25%, risk 15%, valuation 30%.
- Candidate criteria include total score, sub-score minimums, score confidence, and rule engine results.
- Strategic Fit Score is displayed separately and never added to total score.
- ETF handling is separated from common stock total score calculation.
- v0.1 comparison groups are sample-wide, sector/industry, and Value-chain node groups.
- Comparison group details are stored in score logs for later refinement.
- Rule Engine is configuration-driven and records rule events.
- Screening cadence is every 3 days.
- Rebalancing review cadence is every 2 weeks and never implies automatic execution.
- Journal includes interest/addition reasons, invalidation conditions, risk factors, expected holding period, external content influence, emotional state, and post-sale review fields.
- Backtest results must show assumptions, data scope, transaction cost assumptions, MDD, benchmark comparison, and downside defense.
- Discord is a final-phase command and alert surface that calls backend APIs.

## Testing Decisions

- Tests should verify external behavior and business rules, not private implementation details.
- Scoring tests must cover weight calculations, reverse-scored indicators, N/A handling, valuation caps, risk minimum blocking, and score confidence effects.
- Rule Engine tests must cover 5-day +25%, 20-day +50%, same-day +10%, Korea limit-up/down cooldown, US ±15% move cooldown, -10% loss alert, and averaging-down journal requirement.
- UI tests must verify that total score and sub-scores appear together, Strategic Fit Score is separate, statuses include reasons, and rule events are visible.
- Journal tests must verify mandatory prompts for risky actions and post-sale review requirements after rule events.
- Backtest tests must verify 3-day screening cadence, 2-week rebalancing review cadence, benchmark comparison, MDD output, and assumption display.
- Provider tests should use sample/mock data first and keep real API adapters replaceable.

## Out of Scope

- Automatic order execution.
- Buy/sell instruction language.
- Investment recommendation, advisory, discretionary management, or performance guarantee claims.
- Real-time day-trading signals.
- User signup, login, billing, organization management, and multi-tenancy.
- Production SaaS operation.
- Real market data integration in the first development pass.
- AI auto-applying Value-chain structure changes.
- AI auto-replacing human-reviewed company placement.
- ETF-specific full scoring model.
- Discord before backend and web core workflows are stable.

## Further Notes

The working path for this project is:

```text
C:\Users\USER\Desktop\개발\ValuechainDowner\
```

Existing v0.1 planning documents should be preserved as source material. This v0.2 PRD captures the decisions made through the clarification session and should be treated as the implementation planning baseline until superseded.
