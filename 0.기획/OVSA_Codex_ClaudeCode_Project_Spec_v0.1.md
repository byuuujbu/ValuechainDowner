# Objective Value-chain Stock Agent (OVSA) v0.1

> Codex / Claude Code / OpenHands 작업용 프로젝트 사양서  
> 작성일: 2026-05-31  
> 문서 목적: 감정매매를 줄이고, 객관 지표 기반으로 주식·ETF 후보를 선별하는 웹앱의 MVP 개발 사양을 명확히 정의한다.

---

## 0. 사용 방법

이 문서는 Codex, Claude Code, OpenHands, 일반 개발자가 모두 읽을 수 있도록 작성한 **마스터 구현 사양서**다.

개발 에이전트는 이 문서를 기준으로 다음 순서로 작업한다.

1. 프로젝트 골격 생성
2. DB 스키마 생성
3. 점수 계산 엔진 구현
4. Rule Engine 구현
5. 우주 산업 Value-chain 데이터 모델 구현
6. Web UI 구현
7. 관심종목/투자일지 구현
8. 백테스트 구현
9. Discord Bot 연동

중요 원칙:

```text
LLM은 숫자를 만들지 않는다.
Python/Backend 계산 엔진이 숫자를 만든다.
LLM은 계산된 숫자와 룰 엔진 결과만 설명한다.
```

---

## 1. 프로젝트 개요

### 1.1 제품명

```text
Objective Value-chain Stock Agent
약칭: OVSA
```

### 1.2 제품 목적

OVSA는 다음을 목표로 한다.

```text
1. 산업 Value-chain을 시각적으로 이해한다.
2. 사용자가 관심 있는 기업을 객관 지표로 진단한다.
3. 퀄리티·추세·위험·밸류에이션 기준으로 후보를 선별한다.
4. 급등주 추격, 손절 실패, 매수 이유 없는 진입을 차단한다.
5. 투자일지와 백테스트를 통해 사용자 행동을 교정한다.
```

### 1.3 제품 성격

```text
개인/지인용 투자 의사결정 보조 웹앱
산업 Value-chain 기반 기업 탐색 도구
객관 지표 기반 종목 선별 도구
투자일지 및 감정매매 방지 도구
Discord 기반 에이전트 조종실 확장 가능
```

### 1.4 제품이 하지 않는 것

```text
자동 주문 실행
매수/매도 지시
수익률 보장
개별 사용자에게 맞춤형 투자자문처럼 보이는 행위
레버리지/파생상품 추천
실시간 단타 신호 제공
```

### 1.5 서비스 문구 원칙

피해야 할 문구:

```text
오늘 살 종목
AI 추천 매수
상승 확률 높은 종목
수익 가능성 높은 종목
이 종목 사세요
```

사용할 문구:

```text
이번 주 객관 지표 통과 후보
관심종목 진단
후보 가능
관망
제외
매수 금지 조건 해당
투자일지 작성 필요
최종 판단은 사용자 책임
```

기본 고지 문구:

```text
본 서비스는 투자 추천/자문/일임 서비스가 아니라,
사용자의 투자 후보 검토와 투자일지 작성을 돕는 리서치 보조 도구입니다.
최종 투자 판단과 주문 실행은 사용자 본인의 책임입니다.
```

---

## 2. 확정된 기본 방향

| 항목 | v0.1 확정 방향 |
|---|---|
| 시장 | 한국 + 미국 |
| 자산 | 개별주 + ETF |
| 관심종목 | 사용자가 직접 추가 가능 |
| 투자 스타일 | 저변동성 + 퀄리티 + 추세 + 밸류에이션 |
| 평균 보유 기간 | 1~3개월 이상 |
| 스크리닝 | 매주 |
| 리밸런싱 | 월 1회 |
| 보유 수 | 개별주 5~10개 또는 ETF 3~5개 |
| 손실 제한 | 개별 종목 -10% 기준 |
| AI 역할 | 데이터 수집, 점수 계산, 랭킹, 근거 요약, 후보 구성, 체크리스트, 투자일지 분석 |
| 주문 실행 | 제외 |
| 백테스트 성공 기준 | MDD, 벤치마크 대비 성과, 하락장 방어력 |
| 한국 벤치마크 | KODEX 200 + KODEX 코스닥150 |
| 미국 벤치마크 | SPY + QQQ |
| 공통 벤치마크 | 금 가격 + 비트코인 가격 |
| 초기 목적 | 가족/지인 공유 + 투자 기록/분석 |
| 장기 목적 | SaaS 확장 가능성 |
| v0.1 상세 산업 | 우주 산업만 우선 구현 |

---

## 3. 전체 시스템 철학

OVSA는 세 개의 레이어로 구성한다.

```text
[Strategic Map Layer]
산업 / Value-chain / 기업 위치 / 수직계열화 / 시장 관심도 / 뉴스

        ↓

[Quant Decision Layer]
퀄리티 / 추세 / 위험 / 밸류에이션 / 점수 산출 로그 / 후보 판정

        ↓

[Behavior Guard Layer]
급등주 추격 방지 / -10% 손실 알림 / 추가매수 일지 / 투자일지 / 백테스트
```

각 레이어의 권한은 다르다.

| 레이어 | 역할 | 매수 후보 결정 권한 |
|---|---|---|
| Strategic Map Layer | 산업과 기업을 이해하게 해줌 | 없음 |
| Quant Decision Layer | 객관 점수로 후보 자격 심사 | 있음 |
| Behavior Guard Layer | 감정매매와 규칙 위반 차단 | 있음 |

핵심 원칙:

```text
산업맵은 호기심을 만든다.
객관 지표는 후보를 걸러낸다.
금지 규칙은 충동을 막는다.
투자일지는 행동을 교정한다.
백테스트는 착각을 검증한다.
```

---

## 4. 산업 Value-chain 맵

### 4.1 산업 메뉴

v0.1의 상단 산업 메뉴는 5개다.

```text
1. 우주
2. AI
3. 반도체
4. 의학·바이오
5. 로봇
```

단, v0.1에서 상세 구현은 **우주 산업만 먼저** 한다.

```text
우주: 상세 구현
AI: 메뉴 뼈대만, Coming Soon 가능
반도체: 메뉴 뼈대만, Coming Soon 가능
의학·바이오: 메뉴 뼈대만, Coming Soon 가능
로봇: 메뉴 뼈대만, Coming Soon 가능
```

### 4.2 우주 산업 Value-chain 초안

우주 산업의 초기 Value-chain은 다음과 같이 확정한다.

```text
소재/부품
→ 추진체/엔진
→ 발사체
→ 위성 제조
→ 지상국/통신
→ 우주 데이터
→ 국방/상업/탐사 응용
```

기업은 하나의 노드에만 배치하지 않는다. 여러 노드에 걸친 기업은 복수 노드에 배치될 수 있다.

예시:

```text
Rocket Lab
- 발사체: primary
- 위성 제조: primary 또는 secondary
- 우주 시스템/부품: secondary
- 우주 데이터/응용: optional
```

### 4.3 Value-chain 정의 방식

```text
AI가 초안 생성
→ 사람이 검수
→ 검수된 구조만 화면에 표시
→ 이후 데이터 기반 자동 업데이트로 확장
```

처음부터 완전 자동화하지 않는다. 산업 Value-chain은 해석이 들어가기 때문에, AI 초안을 사람이 검수하는 구조가 필요하다.

### 4.4 기업 배치 기준

기업을 Value-chain에 배치할 때는 다음 세 가지 기준을 사용한다.

```text
1. 매출 비중
2. 핵심 제품/서비스
3. 산업 내 전략적 역할
```

배치 신뢰도 산식:

```text
Value-chain 배치 신뢰도 =
매출 비중 근거 40%
+ 핵심 제품/서비스 근거 35%
+ 전략적 역할 근거 25%
```

---

## 5. 수직계열화 점수

### 5.1 목적

수직계열화 점수는 기업이 산업 Value-chain의 핵심 단계들을 얼마나 직접 통제하고 있는지 평가한다.

단순히 “사업 영역이 많다”는 의미가 아니다. 핵심 질문은 다음이다.

```text
핵심 기술을 내재화했는가?
외부 공급자 의존도를 줄이고 있는가?
```

### 5.2 산식

```text
수직계열화 점수 =
핵심 기술 내재화 점수 55%
+ 외부 공급자 의존도 감소 점수 45%
```

### 5.3 핵심 기술 내재화 점수

| 점수 | 의미 |
|---:|---|
| 0 | 핵심 기술 대부분 외부 의존 |
| 25 | 일부 기술 보유, 핵심은 외부 의존 |
| 50 | 핵심 기술 일부 내재화 |
| 75 | 핵심 기술 다수 내재화 |
| 100 | 핵심 기술과 생산/운영 역량 대부분 내재화 |

### 5.4 외부 공급자 의존도 감소 점수

| 점수 | 의미 |
|---:|---|
| 0 | 단일 공급자 또는 외부 파트너 의존도 높음 |
| 25 | 대체 공급자 일부 존재 |
| 50 | 주요 부품 일부 자체 조달 가능 |
| 75 | 핵심 공급망 상당 부분 통제 가능 |
| 100 | 핵심 공급망 대부분 자체 통제 가능 |

v0.1에서는 AI가 초안을 만들고 사람이 검수한다. 완전 자동 점수화는 후속 버전에서 확장한다.

---

## 6. Strategic Fit Score

### 6.1 정의

Strategic Fit Score는 다음 질문에 답하기 위한 점수다.

```text
이 회사는 해당 산업의 미래에서 정말 중요한 위치에 있는가?
```

이 점수는 **종합 투자점수에 반영하지 않는다.**

### 6.2 산식

```text
Strategic Fit Score =
수직계열화 35%
+ 영업현금흐름 신뢰도 25%
+ 거대한 문제 해결 능력 20%
+ 기술 독점성 20%
```

### 6.3 사용 용도

사용하는 곳:

```text
산업맵에서 강조 표시
관심종목 우선순위 정렬
심층분석 대상 선정
뉴스/공시 추적 우선순위 설정
투자 아이디어 기록
```

사용하지 않는 곳:

```text
매수 후보 자동 편입
종합 투자점수 가산
위험 점수 우회
밸류에이션 부담 무시
급등주 추격 금지 룰 우회
```

예시:

```text
Rocket Lab

Strategic Fit Score: 88
종합 투자점수: 62
위험 점수: 38
밸류에이션 점수: 34

판정:
전략적으로 매우 흥미로운 기업.
하지만 현재 기준 신규매수 후보는 아님.
관심종목 유지 + 심층분석 대상으로 분류.
```

---

## 7. 시장 관심도 점수

### 7.1 목적

시장 관심도 점수는 “시장이 이 기업을 보기 시작했는가”를 측정한다.

```text
관심도가 높다 = 사람들이 보고 있다
관심도가 높다 ≠ 사야 한다
```

### 7.2 산식

```text
시장 관심도 점수 =
거래대금 증가 점수 50%
+ 뉴스 언급량 점수 25%
+ 검색 트렌드 점수 25%
```

### 7.3 거래대금 증가 점수

거래대금 증가 점수는 주요 측정요소로 둔다.

```text
최근 5일 평균 거래대금 / 최근 60일 평균 거래대금
최근 20일 평균 거래대금 / 최근 120일 평균 거래대금
거래대금 증가율의 산업 내 백분위
```

거래대금 증가는 시장 관심도에는 반영하되, 급등주 추격 방지 룰과 별도로 관리한다.

---

## 8. 종합 투자점수 체계

### 8.1 핵심 원칙

점수는 AI의 의견이 아니다.

```text
점수 =
정해진 데이터
+ 정해진 비교집단
+ 정해진 가중치
+ 정해진 계산식
+ 정해진 룰 엔진
```

AI의 역할은 점수를 만드는 것이 아니라, 계산된 점수를 사람이 이해할 수 있게 설명하는 것이다.

### 8.2 종합 투자점수 산식

확정된 가중치:

```text
종합 투자점수 =
퀄리티 점수 × 30%
+ 추세 점수 × 25%
+ 위험 점수 × 15%
+ 밸류에이션 점수 × 30%
```

v0.1의 투자 철학:

```text
좋은 회사 30%
적절한 가격 30%
시장 추세 25%
위험 통제 15% + 하드 필터
```

### 8.3 위험 점수 예외

위험 점수는 종합점수 안에서는 15%만 반영되지만, 후보 판정에서는 별도의 최소 통과 기준으로도 사용한다.

```text
위험 점수 < 60이면 종합점수가 높아도 후보 가능 상태가 될 수 없다.
```

예시:

```text
퀄리티: 85
추세: 90
위험: 50
밸류에이션: 88

종합 투자점수:
85 × 30% = 25.5
90 × 25% = 22.5
50 × 15% = 7.5
88 × 30% = 26.4

합계 = 81.9 → 82점

하지만 위험 점수 50점은 최소 기준 60점 미달.
최종 상태: 관망 또는 제외.
```

---

## 9. 4대 점수 상세 구성

종목 상세 화면에는 기본적으로 다음을 표시한다.

```text
종합 투자점수: 77점
퀄리티: 82점 | 추세: 80점 | 위험: 65점 | 밸류에이션: 76점
점수 신뢰도: 92%
Strategic Fit Score: 88
최종 상태: 후보 가능
```

사용자가 각 점수를 클릭하면 구성요소와 계산 로그를 볼 수 있어야 한다.

---

### 9.1 퀄리티 점수

#### 정의

퀄리티 점수는 다음 질문에 답한다.

```text
이 회사는 좋은 사업을 하고 있는가?
이익을 효율적으로 만들고 있는가?
회계상 이익이 실제 현금으로 바뀌고 있는가?
산업 평균 및 경쟁사 대비 수익성이 좋은가?
```

#### 산식

```text
퀄리티 점수 =
ROIC 30%
+ FCF 전환율 25%
+ 이익 안정성 25%
+ 영업이익률 상대점수 20%
```

#### 구성요소

| 구성요소 | 의미 | 점수 방향 |
|---|---|---|
| ROIC | 투하자본 대비 이익 창출력 | 높을수록 좋음 |
| FCF 전환율 | 회계상 이익이 실제 잉여현금흐름으로 전환되는 정도 | 높을수록 좋음 |
| 이익 안정성 | 흑자 지속성, 이익 변동성, 적자 전환 빈도 | 안정적일수록 좋음 |
| 영업이익률 상대점수 | 산업 평균 및 경쟁사 대비 본업 수익성 | 높을수록 좋음 |

#### 화면 설명 예시

```text
퀄리티 82점

구성:
ROIC: 85점
FCF 전환율: 78점
이익 안정성: 84점
영업이익률 상대점수: 80점

계산:
85 × 30% = 25.5
78 × 25% = 19.5
84 × 25% = 21.0
80 × 20% = 16.0

합계 = 82.0점

해석:
이 회사는 ROIC가 산업 평균 대비 높고,
이익 안정성도 양호합니다.
FCF 전환율은 좋지만 압도적 수준은 아니며,
영업이익률은 경쟁사 대비 우수한 편입니다.
```

---

### 9.2 추세 점수

#### 정의

추세 점수는 다음 질문에 답한다.

```text
시장이 이 회사를 인정하고 있는가?
최근 중기 흐름이 좋은가?
단기 급등을 제외해도 강한가?
벤치마크보다 강한가?
```

#### 산식

```text
추세 점수 =
6개월 수익률 35%
+ 12개월-1개월 모멘텀 35%
+ 벤치마크 대비 상대강도 30%
```

#### 구성요소

| 구성요소 | 의미 | 점수 방향 |
|---|---|---|
| 6개월 수익률 | 중기 가격 흐름 | 높을수록 좋음 |
| 12개월-1개월 모멘텀 | 최근 1개월 급등분을 제외한 장기 모멘텀 | 높을수록 좋음 |
| 벤치마크 대비 상대강도 | SPY+QQQ 또는 KODEX 200/코스닥150 대비 강도 | 높을수록 좋음 |

#### 화면 설명 예시

```text
추세 80점

구성:
6개월 수익률: 78점
12개월-1개월 모멘텀: 84점
벤치마크 대비 상대강도: 78점

계산:
78 × 35% = 27.3
84 × 35% = 29.4
78 × 30% = 23.4

합계 = 80.1점 → 80점

해석:
최근 6개월 흐름이 양호하고,
최근 1개월 급등분을 제외한 모멘텀도 좋습니다.
벤치마크 대비 상대강도도 기준 이상입니다.
```

#### 주의

단기 급등은 추세 점수에서 과도하게 보상하지 않는다.

```text
최근 5거래일 +25% 이상
최근 20거래일 +50% 이상
당일 +10% 이상
```

이런 경우는 추세 점수와 별도로 급등주 추격 방지 룰에서 관리한다.

---

### 9.3 위험 점수

#### 정의

위험 점수는 다음 질문에 답한다.

```text
이 종목은 감당 가능한 수준으로 흔들리는가?
하락할 때 너무 크게 무너지지 않는가?
유동성이 충분한가?
```

위험 점수는 높을수록 “위험이 낮다”는 의미다.

#### 산식

```text
위험 점수 =
1년 MDD 역점수 40%
+ 하방 변동성 역점수 35%
+ 평균 거래대금 점수 25%
```

#### 구성요소

| 구성요소 | 의미 | 점수 방향 |
|---|---|---|
| 1년 MDD 역점수 | 최근 1년 최대낙폭이 작을수록 높은 점수 | 낙폭이 작을수록 좋음 |
| 하방 변동성 역점수 | 하락 구간 변동성이 낮을수록 높은 점수 | 낮을수록 좋음 |
| 평균 거래대금 점수 | 거래 유동성이 충분한지 | 높을수록 좋음 |

#### 화면 설명 예시

```text
위험 65점

구성:
1년 MDD 역점수: 62점
하방 변동성 역점수: 58점
평균 거래대금 점수: 82점

계산:
62 × 40% = 24.8
58 × 35% = 20.3
82 × 25% = 20.5

합계 = 65.6점 → 66점

해석:
거래대금은 충분하지만,
최근 1년 최대낙폭과 하방 변동성은 아주 안정적인 수준은 아닙니다.
최소 위험 기준은 통과했지만 포지션 확대에는 주의가 필요합니다.
```

---

### 9.4 밸류에이션 점수

#### 정의

밸류에이션 점수는 다음 질문에 답한다.

```text
좋은 회사를 너무 비싸게 사는 것은 아닌가?
산업 평균 및 경쟁사 대비 가격 부담은 어느 정도인가?
현금흐름 대비 가격이 합리적인가?
성장주라면 매출 대비 가격 부담은 어떤가?
```

#### 산식

```text
밸류에이션 점수 =
FCF Yield 25%
+ EV/EBITDA 20%
+ 섹터 상대 밸류에이션 20%
+ PER 상대점수 20%
+ PSR 상대점수 15%
```

#### 구성요소

| 구성요소 | 의미 | 점수 방향 |
|---|---|---|
| FCF Yield | 시가총액 대비 잉여현금흐름 | 높을수록 좋음 |
| EV/EBITDA | 기업가치 대비 영업현금창출력 | 낮을수록 좋음 |
| 섹터 상대 밸류에이션 | 같은 산업/섹터 대비 비싼지 | 저렴할수록 좋음 |
| PER 상대점수 | 산업 평균 및 경쟁사 대비 이익 대비 가격 | 낮을수록 좋음 |
| PSR 상대점수 | 산업 평균 및 경쟁사 대비 매출 대비 가격 | 낮을수록 좋음 |

#### 화면 설명 예시

```text
밸류에이션 76점

구성:
FCF Yield: 82점
EV/EBITDA: 74점
섹터 상대 밸류에이션: 78점
PER 상대점수: 72점
PSR 상대점수: 73점

계산:
82 × 25% = 20.5
74 × 20% = 14.8
78 × 20% = 15.6
72 × 20% = 14.4
73 × 15% = 11.0

합계 = 76.3점 → 76점

해석:
FCF Yield가 양호하고,
EV/EBITDA와 PER, PSR도 경쟁사 대비 과도하게 비싼 수준은 아닙니다.
다만 압도적으로 저평가된 상태라고 보기는 어렵습니다.
```

#### 보호장치

싸다고 무조건 좋은 종목으로 처리하지 않는다.

```text
퀄리티 점수 < 50:
밸류에이션 점수 최대 60점 제한

위험 점수 < 40:
밸류에이션이 좋아도 후보 불가

FCF가 지속적으로 음수:
FCF Yield는 N/A 또는 낮은 점수 처리

적자 기업:
PER은 N/A 처리
```

---

## 10. 지표별 점수 변환 방식

### 10.1 백분위 기반 상대평가

모든 지표는 원값을 그대로 쓰지 않고 0~100점으로 변환한다.

비교집단:

```text
1. 전체 시장
2. 동일 산업/섹터
3. 동일 Value-chain 노드 또는 직접 경쟁사 그룹
```

기본 산식:

```text
지표 점수 =
산업/섹터 내 백분위 점수 50%
+ 전체 시장 내 백분위 점수 30%
+ Value-chain/직접 경쟁사 내 백분위 점수 20%
```

예시:

```text
ROIC
산업 내 백분위: 82점
전체 시장 내 백분위: 76점
Value-chain 경쟁사 내 백분위: 80점

ROIC 점수:
82 × 50% = 41.0
76 × 30% = 22.8
80 × 20% = 16.0

합계 = 79.8 → 80점
```

### 10.2 낮을수록 좋은 지표

낮을수록 좋은 지표는 백분위 점수를 반대로 계산한다.

```text
1년 MDD
하방 변동성
PER
PSR
EV/EBITDA
```

---

## 11. 점수 산출 로그

### 11.1 목적

사용자가 묻기 전에 앱이 먼저 설명해야 한다.

```text
왜 이 종목은 77점인가?
왜 이 종목은 45점인가?
왜 종합점수는 높은데 후보가 아닌가?
```

### 11.2 종목 상세 화면 기본 표시

```text
종합 투자점수: 77점
퀄리티: 82점 | 추세: 80점 | 위험: 65점 | 밸류에이션: 76점
점수 신뢰도: 92%
Strategic Fit Score: 88
최종 상태: 후보 가능
```

### 11.3 점수 산출 로그 예시

```text
[종합 투자점수 계산]

퀄리티 82 × 30% = 24.6
추세 80 × 25% = 20.0
위험 65 × 15% = 9.75
밸류에이션 76 × 30% = 22.8

합계 = 77.15
반올림 = 77점
```

### 11.4 주요 플러스/마이너스 요인

```text
[주요 플러스 요인]
1. ROIC: 동일 산업 상위권
2. 12개월-1개월 모멘텀: 벤치마크 대비 우수
3. FCF Yield: 경쟁사 대비 양호
4. 평균 거래대금: 기준 충족

[주요 마이너스 요인]
1. 위험 점수는 최소 기준을 통과했지만 높지는 않음
2. PER은 경쟁사 대비 중간 수준
3. 최근 거래대금 증가가 과열 신호인지 추가 확인 필요
```

### 11.5 룰 엔진 결과

```text
[룰 엔진]
급등주 추격 방지: 통과
-10% 손실 알림: 해당 없음
데이터 충분성: 통과
점수 신뢰도: 92%

[최종 판정]
후보 가능
```

---

## 12. 점수 신뢰도

### 12.1 정의

점수 신뢰도는 종합 투자점수와 별도로 표시한다.

```text
종합 투자점수: 77점
점수 신뢰도: 92%
```

점수 신뢰도는 다음을 반영한다.

```text
필수 데이터가 충분한가?
재무 데이터가 최신인가?
비교 대상 기업 수가 충분한가?
N/A 처리된 지표가 너무 많지 않은가?
가격 데이터가 정상적으로 수집되었는가?
공시/재무 데이터와 가격 데이터 기준일이 과도하게 어긋나지 않는가?
```

### 12.2 판정 예시

```text
종합 점수: 77
점수 신뢰도: 94%
상태: 후보 가능
```

```text
종합 점수: 77
점수 신뢰도: 58%
상태: 관망
사유: 재무 데이터 부족, 경쟁사 표본 부족
```

---

## 13. 후보 판정 로직

### 13.1 후보 판정은 점수만으로 하지 않는다

최종 후보 상태는 세 단계를 거친다.

```text
1단계: 하드 필터
2단계: 점수 기준
3단계: 룰 엔진
```

### 13.2 하드 필터

```text
데이터가 충분한가?
거래대금이 너무 적지 않은가?
최근 급등주 추격 금지 조건에 걸리지 않는가?
핵심 재무 데이터가 비어 있지 않은가?
점수 신뢰도가 지나치게 낮지 않은가?
```

### 13.3 점수 기준

v0.1 기본 후보 가능 기준:

```text
종합 투자점수 ≥ 75
퀄리티 점수 ≥ 65
추세 점수 ≥ 65
위험 점수 ≥ 60
밸류에이션 점수 ≥ 40
점수 신뢰도 ≥ 70%
```

이 기준은 백테스트 결과에 따라 조정할 수 있다.

### 13.4 최종 상태

```text
후보 가능
관망
제외
```

후보 가능:

```text
하드 필터 통과
점수 기준 통과
급등주 추격 방지 룰 통과
데이터 신뢰도 통과
```

관망:

```text
전략적으로 흥미롭지만 일부 점수 미달
점수 신뢰도가 낮음
위험 또는 밸류에이션 부담 존재
Strategic Fit Score는 높지만 Quant 점수 미달
```

제외:

```text
위험 점수 심각한 미달
거래대금 부족
핵심 데이터 부족
최근 급등 금지 조건 해당
손실 제한 규칙 위반
밸류에이션 과열
```

---

## 14. 급등주 추격 방지 룰

확정 규칙:

```text
1. 최근 5거래일 +25% 이상 상승:
   신규매수 후보 제외

2. 최근 20거래일 +50% 이상 상승:
   신규매수 후보 제외

3. 당일 또는 최근 수집 기준 +10% 이상 급등:
   당일 신규매수 후보 제외

4. 한국 주식 상한가/하한가 직후 5거래일:
   신규매수 후보 제외

5. 미국 주식 하루 ±15% 이상 급변:
   3거래일 관망
```

룰 발동 시 상태:

```text
관심종목 등록: 가능
분석: 가능
뉴스 확인: 가능
투자일지 작성: 가능
신규매수 후보 편입: 불가
```

화면 문구:

```text
이 종목은 관심종목으로 등록할 수 있습니다.
하지만 최근 급등 조건에 해당하므로 신규매수 후보에서는 제외됩니다.
```

---

## 15. 손절 및 추가매수 룰

확정 규칙:

```text
A. -10% 도달 시 매도 검토 알림
D. 손실 중 추가매수는 투자일지 재작성 필수
```

v0.1 구현:

```text
1. 매수가 대비 -10% 도달 시 강한 매도 검토 알림
2. -10% 도달 종목은 위험 상태로 표시
3. 손실 중 추가매수 버튼 클릭 시 투자일지 재작성 필수
4. 추가매수 이유, 기존 투자 가설 유지 여부, 손절 기준 재확인 필요
5. 최초 투자 가설 기준 손실률도 별도 추적
```

중요 원칙:

```text
물타기로 평균단가가 낮아져도 최초 투자 가설의 실패 여부를 가리지 않는다.
```

---

## 16. 향후 활성화할 룰 구조

분산, 시간대 제한, 복구심리 방지 룰은 v0.1에서는 비활성화하되, 구조만 만들어 둔다.

### 16.1 분산 룰

```yaml
active: false
future_rules:
  - max_single_stock_weight
  - max_single_etf_weight
  - max_industry_weight
  - max_value_chain_node_weight
  - max_top3_position_weight
  - minimum_cash_weight
```

### 16.2 시간대 제한 룰

```yaml
active: false
future_rules:
  - no_buy_us_market_open_first_30m
  - no_buy_us_market_close_last_30m
  - no_buy_premarket_aftermarket
  - no_buy_korea_late_night
```

### 16.3 복구심리 방지 룰

```yaml
active: false
future_rules:
  - block_buy_if_daily_portfolio_loss_lte_minus_2_percent
  - block_buy_if_weekly_portfolio_loss_lte_minus_5_percent
  - block_buy_if_monthly_portfolio_loss_lte_minus_8_percent
  - block_new_buy_on_stop_loss_day
```

---

## 17. Rule Engine 구조

규칙은 하드코딩하지 않고 설정형으로 둔다.

```yaml
rules:
  momentum_chase_guard:
    active: true
    conditions:
      five_day_return_gte: 0.25
      twenty_day_return_gte: 0.50
      intraday_return_gte: 0.10
      us_one_day_abs_return_gte: 0.15
    action: block_new_buy_candidate
    severity: high

  stop_loss_alert:
    active: true
    conditions:
      unrealized_return_lte: -0.10
    action: require_sell_review
    severity: high

  averaging_down_journal:
    active: true
    conditions:
      position_return_lt: 0
      action_type: add_buy
    action: require_journal_rewrite
    severity: medium

  diversification_limit:
    active: false
    conditions:
      max_single_stock_weight: 0.15
      max_industry_weight: 0.40
    action: block_position_increase
    severity: medium

  time_guard:
    active: false
    conditions:
      no_buy_time_windows:
        - market_open_first_30m
        - market_close_last_30m
    action: block_new_buy_candidate
    severity: medium

  revenge_trade_guard:
    active: false
    conditions:
      daily_portfolio_loss_lte: -0.02
    action: block_new_buy_candidate
    severity: high
```

---

## 18. 화면 설계

### 18.1 홈 화면

```text
상단:
우주 / AI / 반도체 / 의학·바이오 / 로봇 메뉴

중앙:
산업 Value-chain 맵

우측:
시장 관심도 상승 기업
급등주 추격 방지 룰 발동 기업
관심종목 상태 변화

하단:
후보 가능 / 관망 / 제외 요약
```

### 18.2 산업맵 화면

디자인 방향:

```text
검은색 배경
SF 스타일
형광 파이프라인 느낌
Value-chain 노드 중심
기업이 가지처럼 연결
```

기능:

```text
확대/축소
노드 클릭
기업 hover 카드
기업 클릭 상세 패널
색상 기준 토글
```

색상 토글 기준:

```text
당일/최근 수집 기준 등락률
최근 5일 등락률
최근 20일 등락률
종합 투자점수
시장 관심도 점수
과열/위험 상태
수직계열화 점수
Strategic Fit Score
```

### 18.3 기업 Hover 카드

```text
기업명
티커
시장
조회 기준일
최근 종가
종가 기준 등락률
시가총액
거래대금 변화
시장 관심도 점수
종합 투자점수
최종 상태
```

무료 데이터 중심이므로 “실시간” 표현은 조심한다.

권장 문구:

```text
조회 기준: 최근 수집 데이터
가격 기준: 종가 또는 제공 API 기준 현재가
```

### 18.4 종목 상세 화면

필수 구성:

```text
1. 기업 개요
2. 주가 차트
3. 종합 투자점수
4. 퀄리티/추세/위험/밸류에이션 하위 점수
5. 각 하위 점수 구성요소
6. 점수 산출 로그
7. 점수 신뢰도
8. Strategic Fit Score
9. Value-chain 내 위치
10. 수직계열화 점수
11. 시장 관심도
12. 뉴스 목록
13. 매수 후보 여부
14. 매수 금지 사유
15. 이 기업을 사면 안 되는 이유
16. 투자일지 작성 버튼
```

상단 카드 예시:

```text
┌─────────────────────────────────────┐
│ Rocket Lab                           │
│ 종합 투자점수: 77점                  │
│ 상태: 후보 가능                      │
│                                      │
│ 퀄리티        82                     │
│ 추세          80                     │
│ 위험          65                     │
│ 밸류에이션    76                     │
│                                      │
│ 점수 신뢰도: 92%                     │
│ Strategic Fit Score: 88              │
│                                      │
│ 주요 사유:                           │
│ + ROIC 및 FCF 전환율 양호            │
│ + 밸류에이션 경쟁사 대비 양호        │
│ - 위험 점수는 높지 않음              │
└─────────────────────────────────────┘
```

---

## 19. 관심종목 기능

### 19.1 목적

관심종목은 사용자가 주관적으로 흥미를 가진 종목을 객관적으로 진단하기 위한 기능이다.

```text
관심종목은 예외 매수 리스트가 아니다.
```

프로세스:

```text
관심종목 추가
→ 산업/Value-chain 매핑
→ 객관 지표 계산
→ 후보 가능/관망/제외 판정
→ 매수 금지 사유 표시
```

### 19.2 예시

```text
Rocket Lab

상태: 관망

좋은 점:
- 우주 Value-chain 여러 노드에 걸쳐 있음
- 수직계열화 점수 높음
- Strategic Fit Score 높음
- 시장 관심도 상승

주의점:
- 위험 점수 기준 미달
- 밸류에이션 부담
- 최근 급등 조건 확인 필요

판정:
관심종목 유지 가능.
단, 현재 기준 신규매수 후보는 아님.
```

---

## 20. 백테스트 설계

### 20.1 목적

백테스트는 수익률만 확인하기 위한 기능이 아니다.

주요 질문:

```text
이 전략은 벤치마크보다 덜 잃었는가?
MDD가 낮았는가?
하락장에서 방어력이 있었는가?
그냥 SPY+QQQ 또는 KODEX 200/코스닥150을 사는 것보다 나았는가?
```

### 20.2 기본 조건

```text
스크리닝 주기: 매주
리밸런싱 주기: 월 1회
보유 기간: 1~3개월 이상
보유 종목 수: 개별주 5~10개 또는 ETF 3~5개
거래비용: 설정 가능
슬리피지: 설정 가능
세금: 설정 가능
```

### 20.3 벤치마크

```text
한국:
KODEX 200
KODEX 코스닥150

미국:
SPY
QQQ

공통:
금 가격
비트코인 가격
```

### 20.4 결과 지표

```text
전략 수익률
벤치마크 수익률
초과수익률
MDD
벤치마크 MDD
하락장 방어율
승률
평균 손익비
월별 손익
최대 연속 손실
리밸런싱별 종목 교체율
규칙 준수 거래 vs 규칙 위반 거래 성과
```

---

## 21. AI 에이전트 구조

### 21.1 전체 구조

```text
Human User
   ↓
Discord / Web App
   ↓
Stock Orchestrator
   ↓
Sub Agents / Workers
   ↓
Database
   ↓
Web App / Discord 결과 표시
```

### 21.2 Sub-Agent 목록

```text
1. Market Data Agent
2. Fundamental Agent
3. Scoring Agent
4. Rule Guard Agent
5. Value-chain Agent
6. Market Interest Agent
7. Explanation Agent
8. Journal Review Agent
9. Backtest Agent
10. Report/Notification Agent
```

#### Market Data Agent

```text
가격 데이터 수집
거래대금 수집
금 가격 수집
비트코인 가격 수집
벤치마크 가격 수집
```

#### Fundamental Agent

```text
재무제표 수집
ROIC 계산
FCF 전환율 계산
영업이익률 계산
PER/PSR/EV/EBITDA 계산
```

#### Scoring Agent

```text
지표별 백분위 계산
퀄리티 점수 계산
추세 점수 계산
위험 점수 계산
밸류에이션 점수 계산
종합 투자점수 계산
점수 신뢰도 계산
```

#### Rule Guard Agent

```text
급등주 추격 방지 체크
-10% 손실 알림
손실 중 추가매수 투자일지 요구
후보 가능/관망/제외 판정
rule_events 저장
```

#### Value-chain Agent

```text
우주산업 Value-chain 초안 생성
기업 노드 배치 초안 생성
수직계열화 근거 요약
사람 검수 요청
```

#### Market Interest Agent

```text
거래대금 증가율 계산
뉴스 언급량 계산
검색 트렌드 계산
시장 관심도 점수 계산
```

#### Explanation Agent

```text
점수 산출 로그를 자연어로 설명
후보/관망/제외 사유 설명
이 기업을 사면 안 되는 이유 생성
데이터 부족 항목 표시
```

중요 제약:

```text
Explanation Agent는 숫자를 지어내지 않는다.
scores_daily, calculated_metrics, rule_events에 저장된 데이터만 설명한다.
```

#### Journal Review Agent

```text
매수 이유 구체성 검토
매도 기준 존재 여부 검토
감정적 표현 탐지
외부 콘텐츠 영향 여부 확인
손실 중 추가매수 시 기존 투자 가설 유지 여부 확인
```

#### Backtest Agent

```text
매주 스크리닝
월 1회 리밸런싱
MDD 계산
벤치마크 비교
하락장 방어력 계산
```

---

## 22. Discord 운영 구조

Discord는 에이전트가 사는 곳이 아니라 조종실이다.

```text
Discord = 명령창 / 알림센터
Backend = 오케스트레이터
Workers = 실제 분석 실행자
Database = 기억장치
Web App = 시각화 대시보드
```

### 22.1 Slash Command 예시

```text
/주간스크리닝 시장:미국
/주간스크리닝 시장:한국

/종목진단 티커:RKLB
/관심종목추가 티커:RKLB 메모:우주 수직계열화 관심

/우주맵갱신
/밸류체인초안 산업:우주

/급등룰체크 티커:RKLB
/점수계산 티커:RKLB

/백테스트 전략:퀄리티밸류추세 기간:5년

/투자일지검토 trade_id:123
```

### 22.2 Discord 응답 예시

```text
RKLB 진단 완료

상태: 관망
종합 투자점수: 64
퀄리티: 58
추세: 81
위험: 39
밸류에이션: 34
점수 신뢰도: 88%
Strategic Fit Score: 87

판정:
전략적으로 흥미롭지만 위험 점수 미달.
신규매수 후보 제외.

상세 보기: Web App 링크
```

---

## 23. 데이터베이스 초안

### 23.1 테이블 목록

```text
assets
asset_aliases
industries
value_chain_nodes
asset_value_chain_map
price_daily
fundamentals_periodic
calculated_metrics
scores_daily
score_logs
benchmarks
market_interest_daily
news_articles
watchlists
portfolios
positions
trades
trade_journals
rules
rule_events
backtest_runs
backtest_results
ai_explanations
```

### 23.2 assets

```sql
CREATE TABLE assets (
    id UUID PRIMARY KEY,
    ticker TEXT NOT NULL,
    name TEXT NOT NULL,
    market TEXT NOT NULL,
    country TEXT,
    currency TEXT,
    asset_type TEXT NOT NULL,
    sector TEXT,
    industry TEXT,
    is_etf BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (ticker, market)
);
```

### 23.3 industries

```sql
CREATE TABLE industries (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 23.4 value_chain_nodes

```sql
CREATE TABLE value_chain_nodes (
    id UUID PRIMARY KEY,
    industry_id UUID NOT NULL REFERENCES industries(id),
    parent_node_id UUID REFERENCES value_chain_nodes(id),
    node_name TEXT NOT NULL,
    node_description TEXT,
    node_order INT NOT NULL DEFAULT 0,
    created_by TEXT DEFAULT 'system',
    review_status TEXT DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 23.5 asset_value_chain_map

```sql
CREATE TABLE asset_value_chain_map (
    id UUID PRIMARY KEY,
    asset_id UUID NOT NULL REFERENCES assets(id),
    value_chain_node_id UUID NOT NULL REFERENCES value_chain_nodes(id),
    role_type TEXT NOT NULL,
    revenue_basis_score NUMERIC,
    product_basis_score NUMERIC,
    strategic_role_score NUMERIC,
    mapping_confidence NUMERIC,
    human_reviewed BOOLEAN DEFAULT FALSE,
    evidence_summary TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (asset_id, value_chain_node_id)
);
```

### 23.6 price_daily

```sql
CREATE TABLE price_daily (
    id UUID PRIMARY KEY,
    asset_id UUID NOT NULL REFERENCES assets(id),
    date DATE NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC NOT NULL,
    adj_close NUMERIC,
    volume NUMERIC,
    trading_value NUMERIC,
    data_source TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (asset_id, date)
);
```

### 23.7 fundamentals_periodic

```sql
CREATE TABLE fundamentals_periodic (
    id UUID PRIMARY KEY,
    asset_id UUID NOT NULL REFERENCES assets(id),
    period_end DATE NOT NULL,
    period_type TEXT NOT NULL,
    revenue NUMERIC,
    operating_income NUMERIC,
    net_income NUMERIC,
    total_assets NUMERIC,
    total_equity NUMERIC,
    total_debt NUMERIC,
    operating_cash_flow NUMERIC,
    capex NUMERIC,
    free_cash_flow NUMERIC,
    shares_outstanding NUMERIC,
    data_source TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (asset_id, period_end, period_type)
);
```

### 23.8 calculated_metrics

```sql
CREATE TABLE calculated_metrics (
    id UUID PRIMARY KEY,
    asset_id UUID NOT NULL REFERENCES assets(id),
    date DATE NOT NULL,
    roic NUMERIC,
    fcf_conversion NUMERIC,
    operating_margin NUMERIC,
    earnings_stability NUMERIC,
    six_month_return NUMERIC,
    momentum_12m_ex_1m NUMERIC,
    relative_strength NUMERIC,
    mdd_1y NUMERIC,
    downside_volatility NUMERIC,
    avg_trading_value NUMERIC,
    fcf_yield NUMERIC,
    ev_ebitda NUMERIC,
    per NUMERIC,
    psr NUMERIC,
    sector_relative_valuation NUMERIC,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (asset_id, date)
);
```

### 23.9 scores_daily

```sql
CREATE TABLE scores_daily (
    id UUID PRIMARY KEY,
    asset_id UUID NOT NULL REFERENCES assets(id),
    date DATE NOT NULL,
    quality_score NUMERIC,
    trend_score NUMERIC,
    risk_score NUMERIC,
    valuation_score NUMERIC,
    total_score NUMERIC,
    score_confidence NUMERIC,
    strategic_fit_score NUMERIC,
    vertical_integration_score NUMERIC,
    market_interest_score NUMERIC,
    candidate_status TEXT,
    status_reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (asset_id, date)
);
```

### 23.10 score_logs

```sql
CREATE TABLE score_logs (
    id UUID PRIMARY KEY,
    asset_id UUID NOT NULL REFERENCES assets(id),
    date DATE NOT NULL,
    score_type TEXT NOT NULL,
    input_metrics_json JSONB,
    peer_group_json JSONB,
    percentile_result_json JSONB,
    weighting_json JSONB,
    calculation_log_text TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 23.11 rules

```sql
CREATE TABLE rules (
    id UUID PRIMARY KEY,
    rule_key TEXT NOT NULL UNIQUE,
    rule_name TEXT NOT NULL,
    rule_category TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    severity TEXT NOT NULL,
    conditions_json JSONB NOT NULL,
    action TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 23.12 rule_events

```sql
CREATE TABLE rule_events (
    id UUID PRIMARY KEY,
    asset_id UUID REFERENCES assets(id),
    portfolio_id UUID,
    rule_id UUID NOT NULL REFERENCES rules(id),
    triggered_at TIMESTAMP NOT NULL DEFAULT NOW(),
    trigger_value JSONB,
    action_taken TEXT,
    message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 23.13 trade_journals

```sql
CREATE TABLE trade_journals (
    id UUID PRIMARY KEY,
    trade_id UUID,
    asset_id UUID NOT NULL REFERENCES assets(id),
    journal_type TEXT NOT NULL,
    buy_reason TEXT,
    sell_condition TEXT,
    risk_condition TEXT,
    expected_holding_period TEXT,
    emotion_state TEXT,
    external_source_influence TEXT,
    rule_check_snapshot JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

---

## 24. API 구조 초안

```text
GET    /health

GET    /industries
GET    /industries/{industry_id}/value-chain

GET    /assets/{ticker}
GET    /assets/{ticker}/scores
GET    /assets/{ticker}/score-log
GET    /assets/{ticker}/market-interest
GET    /assets/{ticker}/value-chain-position

POST   /watchlist
GET    /watchlist
DELETE /watchlist/{watchlist_item_id}

POST   /screening/run
GET    /screening/results

POST   /rules/evaluate
GET    /rules/events

POST   /journals
GET    /journals

POST   /backtests/run
GET    /backtests/{id}

POST   /ai/explain-asset
POST   /ai/generate-value-chain-draft
POST   /admin/review-value-chain
```

핵심 API:

```text
POST /rules/evaluate
```

이 API는 매수 후보 표시 전에 항상 실행된다.

```text
점수 계산
→ 데이터 신뢰도 확인
→ 금지 규칙 확인
→ 후보 가능/관망/제외 판정
→ 사유 저장
```

---

## 25. 기술 스택 초안

```text
Frontend:
Next.js + TypeScript

Graph UI:
React Flow 또는 Cytoscape.js

Backend:
FastAPI + Python

Database:
PostgreSQL

Batch/Queue:
Celery, RQ, 또는 Temporal

Data Processing:
Python Pandas

AI/Agent Layer:
LLM Provider 교체 가능 구조

Deployment:
Docker 기반
```

---

## 26. 권장 레포 구조

```text
ovsa/
  README.md
  AGENTS.md
  CLAUDE.md
  docker-compose.yml
  .env.example

  apps/
    web/
      package.json
      src/
        app/
        components/
        features/
        lib/
        styles/

    api/
      pyproject.toml
      app/
        main.py
        core/
        db/
        models/
        schemas/
        api/
        services/
        scoring/
        rules/
        agents/
        backtesting/
        data_providers/
        tests/

  packages/
    shared-types/

  docs/
    OVSA_Codex_ClaudeCode_Project_Spec_v0.1.md
    api_contract.md
    scoring_methodology.md
    rule_engine.md

  scripts/
    seed_space_industry.py
    run_scoring_job.py
    run_backtest.py

  data/
    sample/
      assets.csv
      price_daily_sample.csv
      fundamentals_sample.csv
```

---

## 27. Codex / Claude Code 작업 지침

### 27.1 공통 지침

```text
1. 이 문서를 단일 진실 공급원으로 사용한다.
2. 투자 판단 문구를 만들지 않는다.
3. 모든 수치 계산은 Python 코드로 구현한다.
4. LLM 설명은 계산 결과 JSON을 입력으로 받아 생성한다.
5. 점수 산출 로그를 반드시 저장한다.
6. 룰 엔진은 하드코딩하지 않고 설정형으로 만든다.
7. DB 스키마와 API는 변경 시 docs/api_contract.md에 반영한다.
8. 테스트 없이 scoring/rules 로직을 완료 처리하지 않는다.
```

### 27.2 Claude Code에 적합한 작업

```text
아키텍처 검토
복잡한 요구사항 정리
도메인 로직 리뷰
에이전트별 책임 분리
설명 문구 품질 개선
테스트 케이스 설계
후보/관망/제외 판정 로직 검수
```

### 27.3 Codex에 적합한 작업

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

## 28. v0.1 개발 단계

### Phase 1. 프로젝트 골격

목표:

```text
Next.js frontend
FastAPI backend
PostgreSQL schema
Docker compose
환경변수 구조
기본 API health check
```

완료 기준:

```text
localhost에서 web/api/db 실행 가능
GET /health 정상 응답
DB migration 실행 가능
README에 실행 방법 작성
```

### Phase 2. 데이터 모델

목표:

```text
assets
industries
value_chain_nodes
asset_value_chain_map
price_daily
fundamentals_periodic
calculated_metrics
scores_daily
score_logs
rules
rule_events
```

완료 기준:

```text
모든 테이블 migration 생성
seed_space_industry.py로 우주산업 기본 노드 생성
sample assets 로딩 가능
```

### Phase 3. 점수 계산 엔진

목표:

```text
지표별 백분위 계산
퀄리티 점수
추세 점수
위험 점수
밸류에이션 점수
종합 투자점수
점수 신뢰도
점수 산출 로그
```

완료 기준:

```text
샘플 데이터 기준 점수 계산 가능
점수 계산 로그 저장
단위 테스트 통과
```

### Phase 4. Rule Engine

목표:

```text
급등주 추격 방지
-10% 손실 알림
손실 중 추가매수 투자일지 필수
비활성화 규칙 구조
rule_events 저장
```

완료 기준:

```text
최근 5거래일 +25% 이상 상승 종목 후보 제외
최근 20거래일 +50% 이상 상승 종목 후보 제외
미국 주식 하루 ±15% 이상 급변 시 3거래일 관망
-10% 손실 알림 이벤트 생성
```

### Phase 5. 우주 산업맵 UI

목표:

```text
우주산업 메뉴
Value-chain 노드
기업 노드
hover 카드
click 상세 패널
색상 토글
Strategic Fit Score 표시
```

완료 기준:

```text
우주 Value-chain 노드 렌더링
기업 노드 렌더링
hover 시 가격/점수 요약 표시
click 시 종목 상세 패널 표시
```

### Phase 6. 관심종목/투자일지

목표:

```text
관심종목 추가
관심종목 진단
투자일지 작성
추가매수 시 일지 재작성 요구
```

완료 기준:

```text
관심종목 추가/삭제 가능
관심종목별 후보/관망/제외 상태 표시
투자일지 저장 가능
손실 중 추가매수 시 일지 요구
```

### Phase 7. 백테스트

목표:

```text
매주 스크리닝
월 1회 리밸런싱
MDD 계산
벤치마크 비교
하락장 방어력 계산
```

완료 기준:

```text
샘플 데이터로 백테스트 실행 가능
전략 수익률 / MDD / 벤치마크 비교 출력
```

### Phase 8. Discord 운영

목표:

```text
Discord Bot
Slash Command
주간 스크리닝 알림
종목 진단 명령
백테스트 명령
Web App 상세 링크 연결
```

완료 기준:

```text
/종목진단 티커:RKLB 명령 처리
/주간스크리닝 명령 처리
결과 요약 + Web App 상세 링크 출력
```

---

## 29. 테스트 요구사항

### 29.1 점수 계산 테스트

필수 테스트:

```text
1. 종합 투자점수 가중치 계산 정확성
2. 낮을수록 좋은 지표 역점수 처리
3. N/A 지표 처리
4. 퀄리티 점수 < 50일 때 밸류에이션 점수 cap 적용
5. 위험 점수 < 60일 때 후보 불가 처리
6. 점수 신뢰도 낮을 때 관망 처리
```

### 29.2 Rule Engine 테스트

필수 테스트:

```text
1. 최근 5거래일 +25% 이상 상승 시 신규매수 후보 제외
2. 최근 20거래일 +50% 이상 상승 시 신규매수 후보 제외
3. 당일 +10% 이상 급등 시 당일 신규매수 후보 제외
4. 미국 주식 하루 ±15% 이상 급변 시 3거래일 관망
5. -10% 손실 시 매도 검토 알림 생성
6. 손실 중 추가매수 시 투자일지 재작성 요구
```

### 29.3 UI 테스트

필수 확인:

```text
1. 종합점수와 하위 점수 4개가 항상 함께 표시되는가?
2. 하위 점수 클릭 시 구성요소와 계산 로그가 표시되는가?
3. Strategic Fit Score가 종합 투자점수와 분리되어 표시되는가?
4. 후보/관망/제외 상태와 사유가 표시되는가?
5. 급등주 추격 방지 룰 발동 사유가 표시되는가?
```

---

## 30. 샘플 데이터 요구사항

v0.1 개발 초기에는 실제 API 연동 전 샘플 데이터로 시작한다.

필수 샘플:

```text
assets.csv
- RKLB
- LMT
- NOC
- BA
- SPY
- QQQ
- KODEX 200
- KODEX 코스닥150
- GOLD_PROXY
- BTC_PROXY

price_daily_sample.csv
- 최소 260거래일
- close, volume, trading_value 포함

fundamentals_sample.csv
- revenue
- operating_income
- net_income
- operating_cash_flow
- capex
- free_cash_flow
- total_debt
- total_equity
- shares_outstanding
```

---

## 31. 데이터 Provider 구조

무료/저비용 데이터 우선, 유료 API 확장 가능 구조를 만든다.

```text
DataProvider
├── KoreaMarketDataProvider
├── KoreaFundamentalProvider
├── USMarketDataProvider
├── USFundamentalProvider
├── NewsProvider
├── SearchTrendProvider
├── CryptoProvider
├── CommodityProvider
└── PaidProviderAdapter
```

v0.1에서는 Provider Interface와 Mock/Sample Provider를 먼저 구현한다.

```python
class MarketDataProvider:
    def get_daily_prices(self, ticker: str, start_date: str, end_date: str):
        raise NotImplementedError

class FundamentalDataProvider:
    def get_fundamentals(self, ticker: str):
        raise NotImplementedError
```

---

## 32. 구현 시 반드시 피할 것

```text
LLM이 점수를 직접 만들기
LLM이 원천 가격/재무 데이터를 임의로 추정하기
종합점수만 보여주고 하위 점수 숨기기
Strategic Fit Score를 종합 투자점수에 섞기
위험 점수 미달을 종합점수로 우회하기
급등주 추격 방지 룰을 관심종목에는 적용하지 않는 실수
투자 추천/매수 지시처럼 보이는 문구 사용
자동 주문 실행 기능 구현
```

---

## 33. 개발 에이전트용 첫 작업 프롬프트

Codex 또는 Claude Code에게 처음 줄 수 있는 프롬프트:

```text
You are working on Objective Value-chain Stock Agent (OVSA) v0.1.
Read docs/OVSA_Codex_ClaudeCode_Project_Spec_v0.1.md first.

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

Phase 2 프롬프트:

```text
Proceed to Phase 2.
Implement the database schema defined in docs/OVSA_Codex_ClaudeCode_Project_Spec_v0.1.md.
Use PostgreSQL and migration tooling.
Create models for assets, industries, value_chain_nodes, asset_value_chain_map, price_daily, fundamentals_periodic, calculated_metrics, scores_daily, score_logs, rules, and rule_events.
Add seed script for the Space industry value-chain nodes.
Do not implement scoring yet.
```

Phase 3 프롬프트:

```text
Proceed to Phase 3.
Implement the scoring engine.
The total investment score must be:
quality_score * 0.30 + trend_score * 0.25 + risk_score * 0.15 + valuation_score * 0.30.
Implement quality, trend, risk, and valuation sub-scores exactly as specified.
Store score logs.
Add unit tests for all scoring formulas and edge cases.
Do not allow LLM-generated scores.
```

---

## 34. v0.1 결론

OVSA v0.1의 핵심은 다음이다.

```text
1. 우주 산업 Value-chain을 먼저 구현한다.
2. 종합 투자점수는 퀄리티 30%, 추세 25%, 위험 15%, 밸류에이션 30%로 계산한다.
3. 종목 상세 화면에는 종합점수와 4대 하위 점수를 항상 함께 표시한다.
4. 각 하위 점수는 세부 구성요소와 계산 로그를 가진다.
5. Strategic Fit Score는 종합 투자점수에 넣지 않는다.
6. 위험 점수는 가중치 15%지만 후보 판정에서는 최소 기준으로 별도 적용한다.
7. 급등주 추격 방지 룰과 -10% 손실 알림은 v0.1에서 활성화한다.
8. Discord는 명령창/알림센터로 사용하고, 실제 계산은 Backend/Worker가 수행한다.
9. LLM은 숫자를 만들지 않고, 계산된 숫자와 룰 엔진 결과를 설명한다.
```

