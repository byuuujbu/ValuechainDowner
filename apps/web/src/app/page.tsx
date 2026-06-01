const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8001";

const screeningRows = [
  {
    ticker: "LMT",
    status: "candidate",
    total: 86.33,
    quality: 95.83,
    trend: 83.33,
    risk: 68.33,
    valuation: 88.33,
    reason: "score and structural rules passed",
  },
  {
    ticker: "NOC",
    status: "watch",
    total: 43.5,
    quality: 54.17,
    trend: 50,
    risk: 58.33,
    valuation: 20,
    reason: "total_score_below_75; risk_score_below_60",
  },
  {
    ticker: "RKLB",
    status: "watch",
    total: 19.42,
    quality: 5.56,
    trend: 50,
    risk: 35,
    valuation: 0,
    reason: "risk_score_below_60; valuation_score_below_40",
  },
  {
    ticker: "BA",
    status: "watch",
    total: 36.25,
    quality: 27.78,
    trend: 16.67,
    risk: 38.33,
    valuation: 60,
    reason: "quality_score_below_65; trend_score_below_65; risk_score_below_60",
  },
];

const industries = ["Space", "AI", "Semiconductor", "Medicine/Bio", "Robotics"];
const chainNodes = [
  "Materials/Parts",
  "Propulsion/Engines",
  "Launch",
  "Satellite Manufacturing",
  "Ground/Communication",
  "Space Data",
  "Applications",
];

const companies = [
  ["RKLB", "Launch + Satellite + Applications", "88"],
  ["LMT", "Satellite + Applications", "82"],
  ["NOC", "Satellite + Ground", "80"],
  ["BA", "Launch + Applications", "65"],
];

export default function Home() {
  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">OVSA Phase MVP</p>
          <h1>ValuechainDowner</h1>
        </div>
        <div className="apiBox">
          <span>API</span>
          <strong>{apiBaseUrl}</strong>
        </div>
      </header>

      <nav className="tabs" aria-label="Main sections">
        <a href="#screening">Screening</a>
        <a href="#map">Industry Map</a>
        <a href="#watchlist">Watchlist</a>
        <a href="#journal">Journal</a>
        <a href="#backtest">Backtest</a>
      </nav>

      <section id="screening" className="section">
        <div className="sectionHead">
          <div>
            <h2>3-Day Screening</h2>
            <p>Common-stock score, rule status, and explanation surface.</p>
          </div>
          <span className="pill">Review every 14 days</span>
        </div>
        <div className="grid three">
          <div className="metric">
            <span>Candidate</span>
            <strong>1</strong>
          </div>
          <div className="metric">
            <span>Watch</span>
            <strong>3</strong>
          </div>
          <div className="metric">
            <span>FX display</span>
            <strong>KRW m</strong>
          </div>
        </div>
        <div className="table" role="table" aria-label="Screening results">
          <div className="row header" role="row">
            <span>Ticker</span>
            <span>Status</span>
            <span>Total</span>
            <span>Score detail</span>
            <span>Reason</span>
          </div>
          {screeningRows.map((row) => (
            <div className="row" role="row" key={row.ticker}>
              <strong>{row.ticker}</strong>
              <span className={`status ${row.status === "candidate" ? "pass" : "watch"}`}>{row.status}</span>
              <span>{row.total}</span>
              <span>
                Q {row.quality} / T {row.trend} / R {row.risk} / V {row.valuation}
              </span>
              <span>{row.reason}</span>
            </div>
          ))}
        </div>
      </section>

      <section id="map" className="section">
        <div className="sectionHead">
          <div>
            <h2>Multi-Industry Map</h2>
            <p>Space is implemented as reviewed seed; other industries are prepared as planned extensions.</p>
          </div>
          <span className="pill">Map-first v0.1</span>
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
              <strong>Strategic fit {fit}</strong>
            </div>
          ))}
        </div>
      </section>

      <section id="watchlist" className="section">
        <div className="sectionHead">
          <div>
            <h2>Watchlist</h2>
            <p>Human review layer for candidates and watch names.</p>
          </div>
        </div>
        <div className="grid two">
          <div className="card">
            <h3>RKLB</h3>
            <p>Track risk score and value-chain fit before candidate status.</p>
          </div>
          <div className="card">
            <h3>LMT</h3>
            <p>Sample benchmark candidate that passes scoring and structural rules.</p>
          </div>
        </div>
      </section>

      <section id="journal" className="section">
        <div className="sectionHead">
          <div>
            <h2>Journal Requirements</h2>
            <p>Averaging-down and post-sale review gates are explicit workflow requirements.</p>
          </div>
        </div>
        <div className="grid two">
          <div className="card">
            <h3>Averaging Down</h3>
            <p>entry_reason, invalidating_condition, risk_factor, current_emotional_state</p>
          </div>
          <div className="card">
            <h3>Post-Sale Review</h3>
            <p>sale_reason, thesis_check, invalidating_condition_triggered, next_action_improvement</p>
          </div>
        </div>
      </section>

      <section id="backtest" className="section">
        <div className="sectionHead">
          <div>
            <h2>Backtest Stub</h2>
            <p>Sample structural check only. Real performance validation needs production-grade data.</p>
          </div>
          <span className="pill">No performance guarantee</span>
        </div>
        <div className="grid three">
          <div className="metric">
            <span>Screening</span>
            <strong>3d</strong>
          </div>
          <div className="metric">
            <span>Review</span>
            <strong>14d</strong>
          </div>
          <div className="metric">
            <span>Sample MDD</span>
            <strong>7.15%</strong>
          </div>
        </div>
      </section>
    </main>
  );
}
