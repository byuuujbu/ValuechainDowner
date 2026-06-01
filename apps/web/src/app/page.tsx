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
    reason: "점수 기준과 구조 규칙을 통과",
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
    reason: "종합점수 75 미만, 위험점수 60 미만",
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
    reason: "위험점수 60 미만, 밸류에이션 점수 40 미만",
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
    reason: "퀄리티, 추세, 위험 기준 미달",
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
  ["RKLB", "발사체 + 위성 + 적용", "88"],
  ["LMT", "위성 + 적용", "82"],
  ["NOC", "위성 + 지상국", "80"],
  ["BA", "발사체 + 적용", "65"],
];

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
              <span>{row.total}</span>
              <span>
                퀄 {row.quality} / 추세 {row.trend} / 위험 {row.risk} / 밸류 {row.valuation}
              </span>
              <span>{row.reason}</span>
            </div>
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
          {companies.map(([ticker, placement, fit]) => (
            <div className="card" key={ticker}>
              <h3>{ticker}</h3>
              <p>{placement}</p>
              <strong>전략 적합도 {fit}</strong>
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
