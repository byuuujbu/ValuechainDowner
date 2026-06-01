const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function Home() {
  return (
    <main style={{ margin: "0 auto", maxWidth: 920, padding: 32 }}>
      <section
        style={{
          background: "var(--panel)",
          border: "1px solid var(--border)",
          borderRadius: 8,
          padding: 24
        }}
      >
        <p style={{ color: "var(--muted)", margin: "0 0 8px" }}>
          Objective Value-chain Stock Agent
        </p>
        <h1 style={{ fontSize: 32, lineHeight: 1.2, margin: "0 0 16px" }}>
          OVSA Phase 1
        </h1>
        <p style={{ lineHeight: 1.6, margin: "0 0 20px" }}>
          프로젝트 골격 상태입니다. 점수 계산, Rule Engine, 산업맵,
          관심종목, 투자일지, 백테스트, Discord는 아직 구현 범위가 아닙니다.
        </p>
        <dl
          style={{
            display: "grid",
            gap: 12,
            gridTemplateColumns: "140px 1fr",
            margin: 0
          }}
        >
          <dt>API</dt>
          <dd style={{ margin: 0 }}>{apiBaseUrl}</dd>
          <dt>Health</dt>
          <dd style={{ margin: 0 }}>
            <a href={`${apiBaseUrl}/health`}>{apiBaseUrl}/health</a>
          </dd>
          <dt>원칙</dt>
          <dd style={{ margin: 0 }}>투자 추천이 아닌 리서치 보조 도구</dd>
        </dl>
      </section>
    </main>
  );
}
