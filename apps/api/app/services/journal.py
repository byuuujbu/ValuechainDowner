WATCHLIST = [
    {
        "ticker": "RKLB",
        "memo": "Track space value-chain fit; risk score must improve before candidate status.",
        "status": "active",
    },
    {
        "ticker": "LMT",
        "memo": "Sample benchmark candidate that passes scoring and structural rules.",
        "status": "active",
    },
]

JOURNAL_REQUIREMENTS = [
    {
        "type": "averaging_down",
        "required": True,
        "fields": ["entry_reason", "invalidating_condition", "risk_factor", "current_emotional_state"],
    },
    {
        "type": "post_sale_review",
        "required_when": "loss_realized_over_10_percent_or_rule_event_triggered",
        "fields": ["sale_reason", "thesis_check", "invalidating_condition_triggered", "next_action_improvement"],
    },
]
