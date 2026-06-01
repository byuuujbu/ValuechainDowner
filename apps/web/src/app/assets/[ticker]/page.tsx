"use client";

import { useEffect, useMemo, useState } from "react";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8001";

type Component = {
  key: string;
  label: string;
  score: number | null;
  weight: number;
};

type Dimension = {
  key: string;
  label: string;
  score: number;
  components: Component[];
};

type Fundamental = {
  period_end: string;
  period_type: string;
  currency: string;
  revenue: number;
  operating_income: number;
  net_income: number;
  total_assets: number;
  total_equity: number;
  total_debt: number;
  operating_cash_flow: number;
  capex: number;
  free_cash_flow: number;
  shares_outstanding: number;
  data_source: string;
};

type Backdata = {
  asset: {
    ticker: string;
    name: string;
    market: string;
    currency: string;
    sector: string;
    industry: string;
  };
  decision: {
    status: string;
    reason: string;
  };
  score: {
    as_of: string;
    total_score: number;
    score_confidence: number;
    dimensions: Dimension[];
    raw_metrics: { key: string; label: string; value: number | null }[];
  };
  price_summary: {
    rows: number;
    start_date: string;
    end_date: string;
    latest_close: number;
    year_high_close: number;
    year_low_close: number;
    latest_volume: number;
    latest_trading_value: number;
    sample_rows: {
      date: string;
      open: number;
      high: number;
      low: number;
      close: number;
      volume: number;
    }[];
  };
  fundamentals: Fundamental[];
  source: {
    provider: string;
    price_file: string;
    fundamentals_file: string;
    assets_file: string;
    notice: string;
  };
};

const statusLabels: Record<string, string> = {
  candidate: "후보",
  watch: "관망",
  exclude: "제외",
};

export default function AssetBackdataPage({ params }: { params: Promise<{ ticker: string }> }) {
  const [ticker, setTicker] = useState("");
  const [data, setData] = useState<Backdata | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    params.then((resolved) => setTicker(resolved.ticker.toUpperCase()));
  }, [params]);

  useEffect(() => {
    if (!ticker) return;
    fetch(`${apiBaseUrl}/assets/${ticker}/backdata`)
      .then((response) => {
        if (!response.ok) throw new Error(`API 응답 실패: ${response.status}`);
        return response.json();
      })
      .then((payload: Backdata) => setData(payload))
      .catch((fetchError: Error) => setError(fetchError.message));
  }, [ticker]);

  if (error) {
    return (
      <main className="shell">
        <a className="textLink" href="/">
          스크리닝으로 돌아가기
        </a>
        <section className="section">
          <h1>데이터를 불러오지 못했습니다</h1>
          <p>{error}</p>
        </section>
      </main>
    );
  }

  if (!data) {
    return (
      <main className="shell">
        <section className="section">
          <h1>종목 상세 데이터를 불러오는 중입니다</h1>
          <p>{ticker || "티커"} 원천 데이터를 API에서 조회하고 있습니다.</p>
        </section>
      </main>
    );
  }

  return <AssetBackdata data={data} />;
}

function AssetBackdata({ data }: { data: Backdata }) {
  const latestFundamental = data.fundamentals[0];
  const fiscalMeta = useMemo(() => formatFiscalMeta(latestFundamental), [latestFundamental]);

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <a className="textLink" href="/">
            스크리닝으로 돌아가기
          </a>
          <p className="eyebrow">원천 backdata 상세</p>
          <h1>
            {data.asset.ticker} <span className="mutedTitle">{data.asset.name}</span>
          </h1>
        </div>
        <div className="apiBox">
          <span>API</span>
          <strong>{apiBaseUrl}</strong>
        </div>
      </header>

      <section className="section">
        <div className="sectionHead">
          <div>
            <h2>자산 기본정보</h2>
            <p>
              {data.asset.market} / {data.asset.sector} / {data.asset.industry} / 기준통화{" "}
              {data.asset.currency}
            </p>
          </div>
          <span className={`status ${data.decision.status === "candidate" ? "pass" : "watch"}`}>
            {statusLabels[data.decision.status]}
          </span>
        </div>
        <div className="grid three">
          <div className="metric">
            <span>종합점수</span>
            <strong>{data.score.total_score}</strong>
          </div>
          <div className="metric">
            <span>신뢰도</span>
            <strong>{data.score.score_confidence}%</strong>
          </div>
          <div className="metric">
            <span>점수 기준일</span>
            <strong>{data.score.as_of}</strong>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="sectionHead">
          <div>
            <h2>최종 판정</h2>
            <p>{data.decision.reason}</p>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="sectionHead">
          <div>
            <h2>점수 산정 구조</h2>
            <p>각 요소 점수는 샘플 유니버스 내 백분위와 가중치를 기준으로 계산됩니다.</p>
          </div>
        </div>
        <div className="grid two">
          {data.score.dimensions.map((dimension) => (
            <article className="card" key={dimension.key}>
              <div className="cardTitle">
                <h3>{dimension.label}</h3>
                <strong>{dimension.score}</strong>
              </div>
              <div className="componentList">
                {dimension.components.map((component) => (
                  <div key={component.key}>
                    <span>{component.label}</span>
                    <strong>{component.score ?? "데이터 없음"}</strong>
                    <small>가중치 {(component.weight * 100).toFixed(0)}%</small>
                  </div>
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="sectionHead">
          <div>
            <h2>가격 backdata</h2>
            <p>
              {data.price_summary.start_date}부터 {data.price_summary.end_date}까지 샘플 가격{" "}
              {data.price_summary.rows}개 행을 사용했습니다.
            </p>
          </div>
        </div>
        <div className="grid three">
          <div className="metric">
            <span>최근 종가</span>
            <strong>{formatNumber(data.price_summary.latest_close)}</strong>
          </div>
          <div className="metric">
            <span>1년 고가 종가</span>
            <strong>{formatNumber(data.price_summary.year_high_close)}</strong>
          </div>
          <div className="metric">
            <span>1년 저가 종가</span>
            <strong>{formatNumber(data.price_summary.year_low_close)}</strong>
          </div>
        </div>
        <div className="compactTable">
          <div className="compactRow header">
            <span>일자</span>
            <span>시가</span>
            <span>고가</span>
            <span>저가</span>
            <span>종가</span>
            <span>거래량</span>
          </div>
          {data.price_summary.sample_rows.map((row) => (
            <div className="compactRow" key={row.date}>
              <span>{row.date}</span>
              <span>{formatNumber(row.open)}</span>
              <span>{formatNumber(row.high)}</span>
              <span>{formatNumber(row.low)}</span>
              <span>{formatNumber(row.close)}</span>
              <span>{formatNumber(row.volume)}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="sectionHead">
          <div>
            <h2>재무 backdata</h2>
            <p>
              아래 재무 수치는 모두 {fiscalMeta} 기준입니다. 원화 백만원 환산은 별도 FX provider 연결 후 확정합니다.
            </p>
          </div>
        </div>
        <div className="sourceBanner">
          <strong>기준 재무제표</strong>
          <span>기준일 {latestFundamental.period_end}</span>
          <span>기간 {periodTypeLabel(latestFundamental.period_type)}</span>
          <span>통화 {latestFundamental.currency}</span>
          <span>출처 {latestFundamental.data_source}</span>
        </div>
        <div className="grid three">
          <FinancialMetric
            label="매출"
            value={latestFundamental.revenue}
            source={fiscalMeta}
          />
          <FinancialMetric
            label="영업이익"
            value={latestFundamental.operating_income}
            source={fiscalMeta}
          />
          <FinancialMetric
            label="잉여현금흐름"
            value={latestFundamental.free_cash_flow}
            source={fiscalMeta}
          />
        </div>
        <div className="rawMetricGrid">
          {data.score.raw_metrics.map((metric) => (
            <div key={metric.key}>
              <span>
                {metric.label}
                <small>{metricSourceLabel(metric.key, fiscalMeta, data.score.as_of)}</small>
              </span>
              <strong>{metric.value === null ? "데이터 없음" : formatNumber(metric.value)}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <h2>데이터 출처</h2>
        <p>{data.source.notice}</p>
        <div className="evidenceList">
          <span>{data.source.provider}</span>
          <span>{data.source.assets_file}</span>
          <span>{data.source.price_file}</span>
          <span>{data.source.fundamentals_file}</span>
        </div>
      </section>
    </main>
  );
}

function FinancialMetric({
  label,
  value,
  source,
}: {
  label: string;
  value: number;
  source: string;
}) {
  return (
    <div className="metric financialMetric">
      <span>{label}</span>
      <strong>{formatCompact(value)}</strong>
      <small>{source}</small>
    </div>
  );
}

function formatFiscalMeta(fundamental: Fundamental) {
  return `${fundamental.period_end} ${periodTypeLabel(fundamental.period_type)} / ${fundamental.currency} / ${fundamental.data_source}`;
}

function periodTypeLabel(periodType: string) {
  if (periodType === "annual") return "연간";
  if (periodType === "quarter") return "분기";
  return periodType;
}

function metricSourceLabel(metricKey: string, fiscalMeta: string, priceAsOf: string) {
  const priceMetrics = new Set([
    "six_month_return",
    "momentum_12m_ex_1m",
    "mdd_1y",
    "downside_volatility",
    "avg_trading_value",
  ]);
  if (priceMetrics.has(metricKey)) return `가격 기준일 ${priceAsOf}`;
  return `재무 기준 ${fiscalMeta}`;
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("ko-KR", { maximumFractionDigits: 4 }).format(value);
}

function formatCompact(value: number) {
  return new Intl.NumberFormat("ko-KR", {
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(value);
}
