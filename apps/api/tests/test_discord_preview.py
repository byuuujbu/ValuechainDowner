from app.services.discord import preview_discord_asset_diagnosis


def test_discord_preview_uses_screening_result_without_credentials() -> None:
    message = preview_discord_asset_diagnosis("LMT")

    assert "LMT diagnosis complete" in message
    assert "status: candidate" in message
    assert "Final judgment" in message
