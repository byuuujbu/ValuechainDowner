from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_screening_results_endpoint_returns_rule_statuses() -> None:
    response = client.get("/screening/results")

    assert response.status_code == 200
    items = response.json()["items"]
    assert {item["ticker"] for item in items} == {"RKLB", "LMT", "NOC", "BA"}
    assert next(item for item in items if item["ticker"] == "LMT")["status"] == "candidate"


def test_industry_map_endpoint_keeps_space_seed_and_future_industries() -> None:
    industries = client.get("/industries").json()["items"]
    space_map = client.get("/industries/space/value-chain").json()

    assert any(industry["key"] == "space" for industry in industries)
    assert any(industry["key"] == "ai" for industry in industries)
    assert space_map["review_status"] == "reviewed_seed"
    assert len(space_map["nodes"]) == 7


def test_watchlist_journal_and_backtest_endpoints() -> None:
    watchlist = client.get("/watchlist").json()["items"]
    journals = client.get("/journals/requirements").json()["items"]
    backtest = client.post("/backtests/run").json()

    assert watchlist[0]["ticker"] == "RKLB"
    assert any(item["type"] == "post_sale_review" for item in journals)
    assert backtest["screening_cadence_days"] == 3
    assert backtest["rebalancing_review_cadence_days"] == 14


def test_asset_backdata_endpoint_exposes_source_inputs() -> None:
    response = client.get("/assets/RKLB/backdata")

    assert response.status_code == 200
    payload = response.json()
    assert payload["asset"]["ticker"] == "RKLB"
    assert payload["score"]["total_score"] == 19.4167
    assert payload["price_summary"]["rows"] == 260
    assert payload["fundamentals"][0]["currency"] == "USD"
    assert payload["source"]["provider"] == "SampleCsvDataProvider"
