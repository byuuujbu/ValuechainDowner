from __future__ import annotations

from decimal import Decimal
from math import sqrt

from app.data_providers.interfaces import DailyPrice, FundamentalsPeriod


def calculate_raw_metrics(
    prices: list[DailyPrice],
    fundamentals: list[FundamentalsPeriod],
) -> dict[str, float | None]:
    latest_fundamental = fundamentals[-1] if fundamentals else None
    latest_close = float(prices[-1].close) if prices else None

    metrics = {
        "roic": None,
        "fcf_conversion": None,
        "operating_margin": None,
        "earnings_stability": None,
        "six_month_return": six_month_return(prices),
        "momentum_12m_ex_1m": momentum_12m_ex_1m(prices),
        "relative_strength": None,
        "mdd_1y": mdd_1y(prices),
        "downside_volatility": downside_volatility(prices),
        "avg_trading_value": avg_trading_value(prices),
        "fcf_yield": None,
        "ev_ebitda": None,
        "per": None,
        "psr": None,
        "sector_relative_valuation": None,
    }

    if latest_fundamental is None or latest_close is None:
        return metrics

    invested_capital = _to_float(latest_fundamental.total_equity) + _to_float(
        latest_fundamental.total_debt
    )
    operating_income = _to_float(latest_fundamental.operating_income)
    net_income = _to_float(latest_fundamental.net_income)
    revenue = _to_float(latest_fundamental.revenue)
    free_cash_flow = _to_float(latest_fundamental.free_cash_flow)
    shares = _to_float(latest_fundamental.shares_outstanding)
    debt = _to_float(latest_fundamental.total_debt)

    metrics["roic"] = safe_div(operating_income, invested_capital)
    metrics["fcf_conversion"] = safe_div(free_cash_flow, net_income) if net_income > 0 else None
    metrics["operating_margin"] = safe_div(operating_income, revenue)
    metrics["earnings_stability"] = 100.0 if net_income > 0 and operating_income > 0 else 25.0

    market_cap = latest_close * shares
    metrics["fcf_yield"] = safe_div(free_cash_flow, market_cap)
    metrics["ev_ebitda"] = safe_div(market_cap + debt, operating_income) if operating_income > 0 else None
    metrics["per"] = safe_div(market_cap, net_income) if net_income > 0 else None
    metrics["psr"] = safe_div(market_cap, revenue)
    metrics["sector_relative_valuation"] = metrics["psr"]

    return metrics


def six_month_return(prices: list[DailyPrice]) -> float | None:
    if len(prices) < 127:
        return None
    return safe_div(float(prices[-1].close), float(prices[-127].close)) - 1


def momentum_12m_ex_1m(prices: list[DailyPrice]) -> float | None:
    if len(prices) < 260:
        return None
    return safe_div(float(prices[-22].close), float(prices[0].close)) - 1


def mdd_1y(prices: list[DailyPrice]) -> float | None:
    if not prices:
        return None
    peak = float(prices[0].close)
    max_drawdown = 0.0
    for price in prices:
        close = float(price.close)
        peak = max(peak, close)
        drawdown = safe_div(close, peak) - 1
        max_drawdown = min(max_drawdown, drawdown)
    return abs(max_drawdown)


def downside_volatility(prices: list[DailyPrice]) -> float | None:
    if len(prices) < 2:
        return None
    downside_returns: list[float] = []
    for previous, current in zip(prices, prices[1:]):
        daily_return = safe_div(float(current.close), float(previous.close)) - 1
        if daily_return < 0:
            downside_returns.append(daily_return)
    if not downside_returns:
        return 0.0
    return sqrt(sum(item * item for item in downside_returns) / len(downside_returns))


def avg_trading_value(prices: list[DailyPrice]) -> float | None:
    values = [float(price.trading_value) for price in prices if price.trading_value is not None]
    if not values:
        return None
    return sum(values) / len(values)


def safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _to_float(value: Decimal | None) -> float:
    return float(value) if value is not None else 0.0
