from __future__ import annotations


def percentile_score(value: float | None, peer_values: list[float | None], *, reverse: bool = False) -> float | None:
    values = sorted(v for v in peer_values if v is not None)
    if value is None or not values:
        return None
    if len(values) == 1:
        return 50.0

    less = sum(1 for item in values if item < value)
    equal = sum(1 for item in values if item == value)
    percentile = (less + (equal - 1) / 2) / (len(values) - 1) * 100
    score = 100 - percentile if reverse else percentile
    return round(score, 4)


def weighted_average(components: dict[str, float | None], weights: dict[str, float]) -> float:
    used_weight = sum(weights[key] for key, value in components.items() if value is not None)
    if used_weight == 0:
        return 0.0
    weighted = sum((value or 0.0) * weights[key] for key, value in components.items())
    return round(weighted / used_weight, 4)
