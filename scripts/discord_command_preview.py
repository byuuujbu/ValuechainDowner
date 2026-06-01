from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = PROJECT_ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.services.discord import preview_discord_asset_diagnosis  # noqa: E402


def main() -> None:
    print(preview_discord_asset_diagnosis("LMT"))


if __name__ == "__main__":
    main()
