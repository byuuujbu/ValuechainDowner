INDUSTRIES = [
    {"key": "space", "name": "Space", "status": "reviewed_seed"},
    {"key": "ai", "name": "AI", "status": "planned"},
    {"key": "semiconductor", "name": "Semiconductor", "status": "planned"},
    {"key": "medicine-bio", "name": "Medicine/Bio", "status": "planned"},
    {"key": "robotics", "name": "Robotics", "status": "planned"},
]

SPACE_MAP = {
    "industry": "Space",
    "review_status": "reviewed_seed",
    "nodes": [
        {"id": "materials", "name": "Materials/Parts", "order": 1},
        {"id": "propulsion", "name": "Propulsion/Engines", "order": 2},
        {"id": "launch", "name": "Launch", "order": 3},
        {"id": "satellite", "name": "Satellite Manufacturing", "order": 4},
        {"id": "ground", "name": "Ground/Communication", "order": 5},
        {"id": "data", "name": "Space Data", "order": 6},
        {"id": "applications", "name": "Government/Commercial Applications", "order": 7},
    ],
    "companies": [
        {
            "ticker": "RKLB",
            "name": "Rocket Lab",
            "strategic_fit_score": 88,
            "placements": [
                {"node_id": "launch", "role": "primary"},
                {"node_id": "satellite", "role": "secondary"},
                {"node_id": "applications", "role": "optional"},
            ],
        },
        {
            "ticker": "LMT",
            "name": "Lockheed Martin",
            "strategic_fit_score": 82,
            "placements": [
                {"node_id": "satellite", "role": "primary"},
                {"node_id": "applications", "role": "primary"},
            ],
        },
        {
            "ticker": "NOC",
            "name": "Northrop Grumman",
            "strategic_fit_score": 80,
            "placements": [
                {"node_id": "satellite", "role": "primary"},
                {"node_id": "ground", "role": "secondary"},
            ],
        },
        {
            "ticker": "BA",
            "name": "Boeing",
            "strategic_fit_score": 65,
            "placements": [
                {"node_id": "launch", "role": "secondary"},
                {"node_id": "applications", "role": "secondary"},
            ],
        },
    ],
}
