const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8001";

const screeningRows = [
  {
    ticker: "LMT",
    name: "록히드 마틴",
    status: "candidate",
    total: 86.33,
    quality: 95.83,
    trend: 83.33,
    risk: 68.33,
    valuation: 88.33,
    reason: "재무 안정성, 추세, 밸류에이션이 모두 기준선을 넘었습니다. 현재 샘플 기준에서는 후보로 검토 가능합니다.",
    detail:
      "영업이익률, 자기자본비율, 잉여현금흐름이 우수하게 잡혔고 200일 이동평균 대비 가격 위치도 양호합니다. 다만 방산 대형주 특성상 급격한 성장주는 아니므로 밸류체인 핵심성 중심으로 해석해야 합니다.",
    backdata: ["영업이익률 상위권", "부채 부담 낮음", "FCF 양호", "200일 추세 우호적"],
  },
  {
    ticker: "NOC",
    name: "노스롭 그루먼",
    status: "watch",
    total: 43.5,
    quality: 54.17,
    trend: 50,
    risk: 58.33,
    valuation: 20,
    reason: "기본 체력은 확인되지만 종합점수와 밸류에이션 점수가 낮아 즉시 후보로 보기 어렵습니다.",
    detail:
      "위성·방산 노출도는 높지만 샘플 재무 기준에서 밸류에이션 매력이 부족하고 위험 점수가 기준선에 살짝 못 미칩니다. 가격 또는 실적 개선 근거가 추가될 때까지 관망이 합리적입니다.",
    backdata: ["밸류에이션 점수 낮음", "위험점수 기준 미달", "추세 중립", "전략 적합도는 높음"],
  },
  {
    ticker: "RKLB",
    name: "로켓 랩",
    status: "watch",
    total: 19.42,
    quality: 5.56,
    trend: 50,
    risk: 35,
    valuation: 0,
    reason: "산업 매력은 높지만 손익과 현금흐름 기준에서 아직 후보 편입을 정당화하기 어렵습니다.",
    detail:
      "발사체와 위성 제조 노출도는 명확하지만 샘플 재무에서 적자와 음의 현금흐름이 크게 반영됩니다. 성장 스토리만으로 후보가 되지 않도록 관망으로 둡니다.",
    backdata: ["영업적자", "FCF 음수", "위험점수 낮음", "밸류에이션 산정 불리"],
  },
  {
    ticker: "BA",
    name: "보잉",
    status: "watch",
    total: 36.25,
    quality: 27.78,
    trend: 16.67,
    risk: 38.33,
    valuation: 60,
    reason: "밸류에이션 일부는 괜찮지만 퀄리티, 추세, 위험 점수가 동시에 기준선을 밑돕니다.",
    detail:
      "우주 관련 사업은 있으나 전체 기업 관점에서는 항공기 품질 이슈와 재무 변동성이 더 크게 반영됩니다. 구조적 회복 신호가 확인되기 전까지 관망으로 두는 판단입니다.",
    backdata: ["퀄리티 낮음", "추세 약함", "위험점수 낮음", "우주 순수 노출도 제한"],
  },
];

const statusLabels: Record<string, string> = {
  candidate: "후보",
  watch: "관망",
  exclude: "제외",
};

const industries = ["우주", "AI", "반도체", "의학/바이오", "로보틱스"];
const chainNodes = [
  "소재/부품",
  "추진체/엔진",
  "발사체",
  "위성 제조",
  "지상국/통신",
  "우주 데이터",
  "정부/상업 적용",
];

const companies = [
  {
    ticker: "RKLB",
    placement: "발사체 + 위성 + 적용",
    fit: 88,
    evidence:
      "Rocket Lab의 Electron 발사 서비스, Photon 위성 플랫폼, 우주 시스템 사업 구성을 기준으로 발사체와 위성 제조 노드에 우선 배치했습니다.",
  },
  {
    ticker: "LMT",
    placement: "위성 + 정부 적용",
    fit: 82,
    evidence:
      "Lockheed Martin의 군사·정부 우주 시스템, 위성 제조, 미사일·방산 고객 기반을 기준으로 위성과 정부 적용 노드에 배치했습니다.",
  },
  {
    ticker: "NOC",
    placement: "위성 + 지상국",
    fit: 80,
    evidence:
      "Northrop Grumman의 위성, 우주 방산 시스템, 지상·통신 인프라 관련 사업 노출을 기준으로 위성 및 지상국 노드에 배치했습니다.",
  },
  {
    ticker: "BA",
    placement: "발사체 + 정부 적용",
    fit: 65,
    evidence:
      "Boeing의 우주·방산 사업과 발사체/우주선 참여 이력은 반영했지만, 전체 기업에서 상업 항공 비중이 크므로 적합도는 낮게 두었습니다.",
  },
];

function scoreClass(value: number) {
  if (value >= 75) return "score good";
  if (value >= 50) return "score mid";
  return "score low";
}

export default function Home() {
  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">OVSA 페이즈 MVP</p>
          <h1>ValuechainDowner</h1>
        </div>
        <div className="apiBox">
          <span>API</span>
          <strong>{apiBaseUrl}</strong>
        </div>
      </header>

      <nav className="tabs" aria-label="주요 섹션">
        <a href="#screening">스크리닝</a>
        <a href="#map">산업맵</a>
        <a href="#watchlist">관심종목</a>
        <a href="#journal">투자일지</a>
        <a href="#backtest">백테스트</a>
      </nav>

      <section id="screening" className="section">
        <div className="sectionHead">
          <div>
            <h2>3일 주기 스크리닝</h2>
            <p>보통주 점수, 규칙 상태, 판단 사유를 한 화면에서 확인합니다.</p>
          </div>
          <span className="pill">14일마다 리밸런싱 검토</span>
        </div>
        <div className="grid three">
          <div className="metric">
            <span>후보</span>
            <strong>1</strong>
          </div>
          <div className="metric">
            <span>관망</span>
            <strong>3</strong>
          </div>
          <div className="metric">
            <span>환산 표시</span>
            <strong>원화 백만원</strong>
          </div>
        </div>
        <div className="table" role="table" aria-label="스크리닝 결과">
          <div className="row header" role="row">
            <span>티커</span>
            <span>상태</span>
            <span>종합</span>
            <span>점수 세부</span>
            <span>판단 사유</span>
            <span>근거</span>
          </div>
          {screeningRows.map((row) => (
            <div className="row" role="row" key={row.ticker}>
              <span className="tickerCell">
                <strong>{row.ticker}</strong>
                <small>{row.name}</small>
              </span>
              <span className={`status ${row.status === "candidate" ? "pass" : "watch"}`}>
                {statusLabels[row.status]}
              </span>
              <strong>{row.total}</strong>
              <span className="scoreSet">
                <span className={scoreClass(row.quality)}>퀄 {row.quality}</span>
                <span className={scoreClass(row.trend)}>추세 {row.trend}</span>
                <span className={scoreClass(row.risk)}>위험 {row.risk}</span>
                <span className={scoreClass(row.valuation)}>밸류 {row.valuation}</span>
              </span>
              <span>{row.reason}</span>
              <a className="textLink" href={`#detail-${row.ticker}`}>
                상세
              </a>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="sectionHead">
          <div>
            <h2>점수 산정 근거</h2>
            <p>현재는 샘플 데이터 기반 설명입니다. 실사용 단계에서는 클릭 시 원천 가격·재무·환율 데이터 화면으로 분리합니다.</p>
          </div>
          <span className="pill">상세 화면 예정</span>
        </div>
        <div className="grid two">
          {screeningRows.map((row) => (
            <article className="card detailCard" id={`detail-${row.ticker}`} key={row.ticker}>
              <div className="cardTitle">
                <h3>
                  {row.ticker} <small>{row.name}</small>
                </h3>
                <span className={`status ${row.status === "candidate" ? "pass" : "watch"}`}>
                  {statusLabels[row.status]}
                </span>
              </div>
              <p>{row.detail}</p>
              <div className="evidenceList">
                {row.backdata.map((item) => (
                  <span key={item}>{item}</span>
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section id="map" className="section">
        <div className="sectionHead">
          <div>
            <h2>멀티 산업맵</h2>
            <p>우주는 검토된 초기 맵으로 구현했고, 다른 산업은 확장 가능한 슬롯으로 준비했습니다.</p>
          </div>
          <span className="pill">맵 우선 v0.1</span>
        </div>
        <div className="pills">
          {industries.map((industry, index) => (
            <span className={`pill ${index === 0 ? "active" : ""}`} key={industry}>
              {industry}
            </span>
          ))}
        </div>
        <div className="chain">
          {chainNodes.map((node, index) => (
            <div className="node" key={node}>
              <strong>{index + 1}</strong>
              <span>{node}</span>
            </div>
          ))}
        </div>
        <div className="grid two">
          {companies.map((company) => (
            <div className="card" key={company.ticker}>
              <h3>{company.ticker}</h3>
              <p>{company.placement}</p>
              <strong>전략 적합도 {company.fit}</strong>
              <p className="evidenceText">{company.evidence}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="watchlist" className="section">
        <div className="sectionHead">
          <div>
            <h2>관심종목</h2>
            <p>후보와 관망 종목을 사람이 최종 검토하는 영역입니다.</p>
          </div>
        </div>
        <div className="grid two">
          <div className="card">
            <h3>RKLB</h3>
            <p>후보 편입 전 위험점수와 밸류체인 적합도를 추적합니다.</p>
          </div>
          <div className="card">
            <h3>LMT</h3>
            <p>점수와 구조 규칙을 통과한 샘플 기준 후보입니다.</p>
          </div>
        </div>
      </section>

      <section id="journal" className="section">
        <div className="sectionHead">
          <div>
            <h2>투자일지 요구사항</h2>
            <p>물타기와 매도 후 회고는 반드시 기록해야 하는 워크플로우입니다.</p>
          </div>
        </div>
        <div className="grid two">
          <div className="card">
            <h3>물타기 기록</h3>
            <p>진입 이유, 무효화 조건, 위험 요인, 현재 감정 상태</p>
          </div>
          <div className="card">
            <h3>매도 후 회고</h3>
            <p>매도 이유, 투자 가설 점검, 무효화 조건 작동 여부, 다음 행동 개선점</p>
          </div>
        </div>
      </section>

      <section id="backtest" className="section">
        <div className="sectionHead">
          <div>
            <h2>백테스트 초안</h2>
            <p>현재는 샘플 구조 검증 단계입니다. 실제 성과 검증은 운영급 데이터가 필요합니다.</p>
          </div>
          <span className="pill">성과 보장 아님</span>
        </div>
        <div className="grid three">
          <div className="metric">
            <span>스크리닝</span>
            <strong>3d</strong>
          </div>
          <div className="metric">
            <span>검토</span>
            <strong>14d</strong>
          </div>
          <div className="metric">
            <span>샘플 MDD</span>
            <strong>7.15%</strong>
          </div>
        </div>
      </section>
    </main>
  );
}
