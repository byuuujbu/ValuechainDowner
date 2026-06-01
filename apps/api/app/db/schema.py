from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)


def id_column() -> Column:
    return Column("id", String(36), primary_key=True)


def created_at_column() -> Column:
    return Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now())


def updated_at_column() -> Column:
    return Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


assets = Table(
    "assets",
    metadata,
    id_column(),
    Column("ticker", String(32), nullable=False),
    Column("name", String(255), nullable=False),
    Column("market", String(32), nullable=False),
    Column("country", String(64)),
    Column("currency", String(16)),
    Column("asset_type", String(32), nullable=False),
    Column("sector", String(128)),
    Column("industry", String(128)),
    Column("is_etf", Boolean, nullable=False, server_default="false"),
    created_at_column(),
    updated_at_column(),
    UniqueConstraint("ticker", "market", name="uq_assets_ticker_market"),
)

asset_aliases = Table(
    "asset_aliases",
    metadata,
    id_column(),
    Column("asset_id", String(36), ForeignKey("assets.id"), nullable=False),
    Column("alias", String(255), nullable=False),
    Column("source", String(64)),
    created_at_column(),
    UniqueConstraint("asset_id", "alias", name="uq_asset_aliases_asset_id_alias"),
)

industries = Table(
    "industries",
    metadata,
    id_column(),
    Column("name", String(128), nullable=False, unique=True),
    Column("description", Text),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    created_at_column(),
    updated_at_column(),
)

value_chain_nodes = Table(
    "value_chain_nodes",
    metadata,
    id_column(),
    Column("industry_id", String(36), ForeignKey("industries.id"), nullable=False),
    Column("parent_node_id", String(36), ForeignKey("value_chain_nodes.id")),
    Column("node_name", String(128), nullable=False),
    Column("node_description", Text),
    Column("node_order", Integer, nullable=False, server_default="0"),
    Column("created_by", String(64), nullable=False, server_default="system"),
    Column("review_status", String(32), nullable=False, server_default="draft"),
    created_at_column(),
    updated_at_column(),
    UniqueConstraint("industry_id", "node_name", name="uq_value_chain_nodes_industry_id_node_name"),
    CheckConstraint(
        "review_status in ('draft', 'reviewed', 'rejected')",
        name="review_status_allowed",
    ),
)

asset_value_chain_map = Table(
    "asset_value_chain_map",
    metadata,
    id_column(),
    Column("asset_id", String(36), ForeignKey("assets.id"), nullable=False),
    Column("value_chain_node_id", String(36), ForeignKey("value_chain_nodes.id"), nullable=False),
    Column("role_type", String(32), nullable=False),
    Column("revenue_basis_score", Numeric(10, 4)),
    Column("product_basis_score", Numeric(10, 4)),
    Column("strategic_role_score", Numeric(10, 4)),
    Column("mapping_confidence", Numeric(10, 4)),
    Column("human_reviewed", Boolean, nullable=False, server_default="false"),
    Column("evidence_summary", Text),
    created_at_column(),
    updated_at_column(),
    UniqueConstraint("asset_id", "value_chain_node_id", name="uq_asset_value_chain_map_asset_node"),
    CheckConstraint(
        "role_type in ('primary', 'secondary', 'optional')",
        name="role_type_allowed",
    ),
)

price_daily = Table(
    "price_daily",
    metadata,
    id_column(),
    Column("asset_id", String(36), ForeignKey("assets.id"), nullable=False),
    Column("date", Date, nullable=False),
    Column("open", Numeric(20, 6)),
    Column("high", Numeric(20, 6)),
    Column("low", Numeric(20, 6)),
    Column("close", Numeric(20, 6), nullable=False),
    Column("adj_close", Numeric(20, 6)),
    Column("volume", Numeric(24, 4)),
    Column("trading_value", Numeric(24, 4)),
    Column("data_source", String(64)),
    created_at_column(),
    UniqueConstraint("asset_id", "date", name="uq_price_daily_asset_id_date"),
)

fundamentals_periodic = Table(
    "fundamentals_periodic",
    metadata,
    id_column(),
    Column("asset_id", String(36), ForeignKey("assets.id"), nullable=False),
    Column("period_end", Date, nullable=False),
    Column("period_type", String(16), nullable=False),
    Column("revenue", Numeric(24, 4)),
    Column("operating_income", Numeric(24, 4)),
    Column("net_income", Numeric(24, 4)),
    Column("total_assets", Numeric(24, 4)),
    Column("total_equity", Numeric(24, 4)),
    Column("total_debt", Numeric(24, 4)),
    Column("operating_cash_flow", Numeric(24, 4)),
    Column("capex", Numeric(24, 4)),
    Column("free_cash_flow", Numeric(24, 4)),
    Column("shares_outstanding", Numeric(24, 4)),
    Column("data_source", String(64)),
    created_at_column(),
    UniqueConstraint(
        "asset_id",
        "period_end",
        "period_type",
        name="uq_fundamentals_periodic_asset_period_type",
    ),
)

calculated_metrics = Table(
    "calculated_metrics",
    metadata,
    id_column(),
    Column("asset_id", String(36), ForeignKey("assets.id"), nullable=False),
    Column("date", Date, nullable=False),
    Column("roic", Numeric(12, 6)),
    Column("fcf_conversion", Numeric(12, 6)),
    Column("operating_margin", Numeric(12, 6)),
    Column("earnings_stability", Numeric(12, 6)),
    Column("six_month_return", Numeric(12, 6)),
    Column("momentum_12m_ex_1m", Numeric(12, 6)),
    Column("relative_strength", Numeric(12, 6)),
    Column("mdd_1y", Numeric(12, 6)),
    Column("downside_volatility", Numeric(12, 6)),
    Column("avg_trading_value", Numeric(24, 4)),
    Column("fcf_yield", Numeric(12, 6)),
    Column("ev_ebitda", Numeric(12, 6)),
    Column("per", Numeric(12, 6)),
    Column("psr", Numeric(12, 6)),
    Column("sector_relative_valuation", Numeric(12, 6)),
    created_at_column(),
    updated_at_column(),
    UniqueConstraint("asset_id", "date", name="uq_calculated_metrics_asset_id_date"),
)

scores_daily = Table(
    "scores_daily",
    metadata,
    id_column(),
    Column("asset_id", String(36), ForeignKey("assets.id"), nullable=False),
    Column("date", Date, nullable=False),
    Column("quality_score", Numeric(10, 4)),
    Column("trend_score", Numeric(10, 4)),
    Column("risk_score", Numeric(10, 4)),
    Column("valuation_score", Numeric(10, 4)),
    Column("total_score", Numeric(10, 4)),
    Column("score_confidence", Numeric(10, 4)),
    Column("strategic_fit_score", Numeric(10, 4)),
    Column("vertical_integration_score", Numeric(10, 4)),
    Column("market_interest_score", Numeric(10, 4)),
    Column("candidate_status", String(32)),
    Column("status_reason", Text),
    created_at_column(),
    updated_at_column(),
    UniqueConstraint("asset_id", "date", name="uq_scores_daily_asset_id_date"),
)

score_logs = Table(
    "score_logs",
    metadata,
    id_column(),
    Column("asset_id", String(36), ForeignKey("assets.id"), nullable=False),
    Column("date", Date, nullable=False),
    Column("score_type", String(64), nullable=False),
    Column("input_metrics_json", JSON),
    Column("peer_group_json", JSON),
    Column("percentile_result_json", JSON),
    Column("weighting_json", JSON),
    Column("calculation_log_text", Text),
    created_at_column(),
)

benchmarks = Table(
    "benchmarks",
    metadata,
    id_column(),
    Column("asset_id", String(36), ForeignKey("assets.id"), nullable=False),
    Column("benchmark_key", String(64), nullable=False),
    Column("benchmark_name", String(128), nullable=False),
    Column("market", String(32), nullable=False),
    Column("weight", Numeric(10, 4)),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    created_at_column(),
    UniqueConstraint("benchmark_key", "asset_id", name="uq_benchmarks_key_asset"),
)

market_interest_daily = Table(
    "market_interest_daily",
    metadata,
    id_column(),
    Column("asset_id", String(36), ForeignKey("assets.id"), nullable=False),
    Column("date", Date, nullable=False),
    Column("trading_value_increase_score", Numeric(10, 4)),
    Column("news_mentions_score", Numeric(10, 4)),
    Column("search_trend_score", Numeric(10, 4)),
    Column("market_interest_score", Numeric(10, 4)),
    created_at_column(),
    UniqueConstraint("asset_id", "date", name="uq_market_interest_daily_asset_id_date"),
)

news_articles = Table(
    "news_articles",
    metadata,
    id_column(),
    Column("asset_id", String(36), ForeignKey("assets.id")),
    Column("title", Text, nullable=False),
    Column("url", Text, nullable=False),
    Column("source", String(128)),
    Column("published_at", DateTime(timezone=True)),
    Column("summary", Text),
    created_at_column(),
    UniqueConstraint("url", name="uq_news_articles_url"),
)

watchlists = Table(
    "watchlists",
    metadata,
    id_column(),
    Column("asset_id", String(36), ForeignKey("assets.id"), nullable=False),
    Column("owner_key", String(64), nullable=False, server_default="local"),
    Column("memo", Text),
    Column("status", String(32), nullable=False, server_default="active"),
    created_at_column(),
    updated_at_column(),
    UniqueConstraint("asset_id", "owner_key", name="uq_watchlists_asset_owner"),
)

portfolios = Table(
    "portfolios",
    metadata,
    id_column(),
    Column("owner_key", String(64), nullable=False, server_default="local"),
    Column("name", String(128), nullable=False),
    Column("base_currency", String(16), nullable=False, server_default="USD"),
    created_at_column(),
    updated_at_column(),
    UniqueConstraint("owner_key", "name", name="uq_portfolios_owner_name"),
)

positions = Table(
    "positions",
    metadata,
    id_column(),
    Column("portfolio_id", String(36), ForeignKey("portfolios.id"), nullable=False),
    Column("asset_id", String(36), ForeignKey("assets.id"), nullable=False),
    Column("quantity", Numeric(24, 8), nullable=False),
    Column("average_cost", Numeric(20, 6)),
    Column("opened_at", DateTime(timezone=True)),
    Column("closed_at", DateTime(timezone=True)),
    created_at_column(),
    updated_at_column(),
)

trades = Table(
    "trades",
    metadata,
    id_column(),
    Column("portfolio_id", String(36), ForeignKey("portfolios.id"), nullable=False),
    Column("asset_id", String(36), ForeignKey("assets.id"), nullable=False),
    Column("trade_type", String(32), nullable=False),
    Column("quantity", Numeric(24, 8), nullable=False),
    Column("price", Numeric(20, 6), nullable=False),
    Column("fees", Numeric(20, 6)),
    Column("traded_at", DateTime(timezone=True), nullable=False),
    created_at_column(),
    CheckConstraint("trade_type in ('buy', 'sell')", name="trade_type_allowed"),
)

trade_journals = Table(
    "trade_journals",
    metadata,
    id_column(),
    Column("trade_id", String(36), ForeignKey("trades.id")),
    Column("asset_id", String(36), ForeignKey("assets.id"), nullable=False),
    Column("journal_type", String(32), nullable=False),
    Column("buy_reason", Text),
    Column("sell_condition", Text),
    Column("risk_condition", Text),
    Column("expected_holding_period", String(128)),
    Column("emotion_state", Text),
    Column("external_source_influence", Text),
    Column("post_sale_review", Text),
    Column("rule_check_snapshot", JSON),
    created_at_column(),
)

rules = Table(
    "rules",
    metadata,
    id_column(),
    Column("rule_key", String(128), nullable=False, unique=True),
    Column("rule_name", String(255), nullable=False),
    Column("rule_category", String(64), nullable=False),
    Column("active", Boolean, nullable=False, server_default="true"),
    Column("severity", String(32), nullable=False),
    Column("conditions_json", JSON, nullable=False),
    Column("action", String(64), nullable=False),
    created_at_column(),
    updated_at_column(),
)

rule_events = Table(
    "rule_events",
    metadata,
    id_column(),
    Column("asset_id", String(36), ForeignKey("assets.id")),
    Column("portfolio_id", String(36), ForeignKey("portfolios.id")),
    Column("rule_id", String(36), ForeignKey("rules.id"), nullable=False),
    Column("triggered_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("trigger_value", JSON),
    Column("action_taken", String(64)),
    Column("message", Text),
    created_at_column(),
)

backtest_runs = Table(
    "backtest_runs",
    metadata,
    id_column(),
    Column("strategy_name", String(128), nullable=False),
    Column("screening_cadence_days", Integer, nullable=False, server_default="3"),
    Column("rebalancing_review_cadence_days", Integer, nullable=False, server_default="14"),
    Column("start_date", Date, nullable=False),
    Column("end_date", Date, nullable=False),
    Column("assumptions_json", JSON),
    created_at_column(),
)

backtest_results = Table(
    "backtest_results",
    metadata,
    id_column(),
    Column("backtest_run_id", String(36), ForeignKey("backtest_runs.id"), nullable=False),
    Column("strategy_return", Numeric(12, 6)),
    Column("mdd", Numeric(12, 6)),
    Column("benchmark_comparison_json", JSON),
    Column("downside_defense_json", JSON),
    created_at_column(),
)

ai_explanations = Table(
    "ai_explanations",
    metadata,
    id_column(),
    Column("asset_id", String(36), ForeignKey("assets.id")),
    Column("explanation_type", String(64), nullable=False),
    Column("input_snapshot_json", JSON, nullable=False),
    Column("explanation_text", Text, nullable=False),
    created_at_column(),
)
