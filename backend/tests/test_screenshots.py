from pathlib import Path

from app.services.screenshots import parse_profile_page


FIXTURE_PATH = (
    Path(__file__).parent / "fixtures" / "screenshots_page.html"
)


def test_parse_profile_page_returns_urls():
    html = FIXTURE_PATH.read_text(encoding="utf-8")

    urls = parse_profile_page(html, app_id=730)

    assert len(urls) >= 5
    assert urls[:2] == [
        "https://images.steamusercontent.com/ugc/"
        "16673077223190541863/"
        "6831F5BF2E08F4BAFCD6FB4545F52346F73A5687/",
        "https://images.steamusercontent.com/ugc/"
        "13674896552391034869/"
        "30BA0C1AE6314AABA7BB8596D3DBE8AF4BEAE0F9/",
    ]
    assert all(
        url.startswith("https://images.steamusercontent.com/ugc/")
        for url in urls
    )
    assert len(urls) == len(set(urls))


def test_parse_profile_page_excludes_other_games():
    html = FIXTURE_PATH.read_text(encoding="utf-8")

    assert parse_profile_page(html, app_id=440) == []