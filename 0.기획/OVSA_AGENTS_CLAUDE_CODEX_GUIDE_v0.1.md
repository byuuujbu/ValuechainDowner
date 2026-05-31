# OVSA AGENTS / CLAUDE CODE / CODEX GUIDE v0.1

> 이 문서는 `OVSA_Codex_ClaudeCode_Project_Spec_v0.1.md`의 실행 지침만 압축한 개발 에이전트용 가이드다.  
> Claude Code, Codex, OpenHands worker는 이 문서를 먼저 읽고, 세부 구현은 마스터 사양서를 따른다.

---

## 1. 절대 원칙

```text
LLM은 숫자를 만들지 않는다.
Python/Backend 계산 엔진이 숫자를 만든다.
LLM은 계산된 숫자와 룰 엔진 결과만 설명한다.
```

```text
이 앱은 투자 추천 앱이 아니다.
이 앱은 객관 지표 기반 후보 검토 및 감정매매 방지 도구다.
```

---

## 2. 금지 사항

```text
자동 주문 실행 구현 금지
매수/매도 지시 문구 금지
수익률 보장 문구 금지
LLM이 가격/재무 데이터를 추정하는 행위 금지
LLM이 점수를 임의 생성하는 행위 금지
Strategic Fit Score를 종합 투자점수에 섞는 것 금지
위험 점수 기준 미달을 종합점수로 우회하는 것 금지
```

---

## 3. 핵심 점수 공식

```text
종합 투자점수 =
퀄리티 점수 × 30%
+ 추세 점수 × 25%
+ 위험 점수 × 15%
+ 밸류에이션 점수 × 30%
```

후보 가능 기본 기준:

```text
종합 투자점수 ≥ 75
퀄리티 점수 ≥ 65
추세 점수 ≥ 65
위험 점수 ≥ 60
밸류에이션 점수 ≥ 40
점수 신뢰도 ≥ 70%
```

위험 점수는 종합점수 내 가중치가 15%이지만, 후보 판정에서는 별도 최소 기준으로 적용한다.

---

## 4. 하위 점수 공식

### 4.1 퀄리티

```text
퀄리티 점수 =
ROIC 30%
+ FCF 전환율 25%
+ 이익 안정성 25%
+ 영업이익률 상대점수 20%
```

### 4.2 추세

```text
추세 점수 =
6개월 수익률 35%
+ 12개월-1개월 모멘텀 35%
+ 벤치마크 대비 상대강도 30%
```

### 4.3 위험

```text
위험 점수 =
1년 MDD 역점수 40%
+ 하방 변동성 역점수 35%
+ 평균 거래대금 점수 25%
```

### 4.4 밸류에이션

```text
밸류에이션 점수 =
FCF Yield 25%
+ EV/EBITDA 20%
+ 섹터 상대 밸류에이션 20%
+ PER 상대점수 20%
+ PSR 상대점수 15%
```

---

## 5. 룰 엔진 활성 규칙

```text
최근 5거래일 +25% 이상 상승: 신규매수 후보 제외
최근 20거래일 +50% 이상 상승: 신규매수 후보 제외
당일 또는 최근 수집 기준 +10% 이상 급등: 당일 신규매수 후보 제외
한국 주식 상한가/하한가 직후 5거래일: 신규매수 후보 제외
미국 주식 하루 ±15% 이상 급변: 3거래일 관망
-10% 손실 도달: 매도 검토 알림
손실 중 추가매수: 투자일지 재작성 필수
```

---

## 6. v0.1 개발 순서

```text
Phase 1. 프로젝트 골격
Phase 2. 데이터 모델
Phase 3. 점수 계산 엔진
Phase 4. Rule Engine
Phase 5. 우주 산업맵 UI
Phase 6. 관심종목/투자일지
Phase 7. 백테스트
Phase 8. Discord 운영
```

각 Phase는 이전 Phase의 테스트가 통과된 뒤 진행한다.

---

## 7. 권장 역할 분담

### Claude Code

```text
아키텍처 검토
요구사항 정리
도메인 로직 리뷰
에이전트 책임 분리
설명 문구 품질 개선
테스트 케이스 설계
후보/관망/제외 판정 검수
```

### Codex

```text
프로젝트 골격 생성
FastAPI 엔드포인트 구현
PostgreSQL 모델 작성
Pandas 기반 점수 계산 구현
Rule Engine 구현
React/Next.js 컴포넌트 구현
테스트 코드 작성
Docker Compose 구성
```

---

## 8. 첫 작업 프롬프트

```text
You are working on Objective Value-chain Stock Agent (OVSA) v0.1.
Read OVSA_Codex_ClaudeCode_Project_Spec_v0.1.md first.

Your first task is Phase 1 only:
- Create a monorepo structure with apps/web and apps/api.
- apps/web uses Next.js + TypeScript.
- apps/api uses FastAPI + Python.
- Add docker-compose.yml with PostgreSQL.
- Add .env.example.
- Implement GET /health in FastAPI.
- Add README.md with local run instructions.

Do not implement scoring, rules, or UI yet.
Do not add investment recommendation language.
Keep all code OS-independent and Docker-friendly.
```
