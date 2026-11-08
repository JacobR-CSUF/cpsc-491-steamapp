# KAN-47: AI achievement suggestions.

# Sends a player's easiest missing achievements (from KAN-46) to the Gemini
# API and returns one short, practical tip for each.
# API reference: https://ai.google.dev/api/generate-content

from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from app.core.cache import cached
from app.core.config import get_settings
from app.services.advanced_stats import missing_achievements
from app.services.game_detail_service import get_owned_game

MODEL = "gemini-flash-latest"
MAX_ACHIEVEMENTS = 10
ONE_DAY = 24 * 60 * 60

SYSTEM_INSTRUCTION = (
    "You are a gaming coach. For each Steam achievement listed, give one short, "
    "practical tip for earning it. Keep each tip to one or two sentences, use the "
    "achievement's name as a label, and do not invent achievements that aren't listed."
)

ALL_UNLOCKED = "Every achievement in this game is already unlocked."


class EmptySuggestionsError(Exception):
    """Raised when Gemini answers with no text."""


def has_api_key() -> bool:
    """Return True when GEMINI_API_KEY is set."""
    return bool(get_settings().gemini_api_key)


def build_prompt(game_name: str, missing: list[dict]) -> str:
    """List up to 10 of the easiest missing achievements for the prompt.

    `missing` comes from missing_achievements(), which is already sorted
    easiest first, so the first 10 are the easiest.
    """
    lines = [f"Game: {game_name}", "Missing achievements, easiest first:"]
    for number, achievement in enumerate(missing[:MAX_ACHIEVEMENTS], start=1):
        percent = achievement.get("global_percent")
        unlocked_by = (
            f"{percent:.1f}% of players have it"
            if percent is not None
            else "global unlock rate unknown"
        )
        description = achievement.get("description") or "No description provided."
        lines.append(
            f"{number}. {achievement['display_name']}: {description} ({unlocked_by})"
        )
    return "\n".join(lines)


def request_suggestions(prompt: str) -> str:
    """Send the prompt to Gemini and return its text. Raises on an empty answer."""
    client = genai.Client(api_key=get_settings().gemini_api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=4096,
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        ),
    )
    text = (response.text or "").strip()
    if not text:
        raise EmptySuggestionsError("Gemini returned an empty response.")
    return text


def get_suggestions(db: Session, steam_id: str, app_id: int) -> dict | None:
    """Return AI tips for the player's easiest missing achievements.

    Returns None when the player doesn't own the game. Answers are cached for
    24 hours under ai:suggestions:{steam_id}:{app_id}.
    """
    owned_game = get_owned_game(db, steam_id, app_id)
    if owned_game is None:
        return None

    _, game = owned_game

    def fetch() -> str:
        missing = missing_achievements(db, steam_id, app_id)
        if not missing:
            return ALL_UNLOCKED  # nothing to ask Gemini about
        return request_suggestions(build_prompt(game.name, missing))

    suggestions = cached(f"ai:suggestions:{steam_id}:{app_id}", ONE_DAY, fetch)
    return {"app_id": game.app_id, "suggestions": suggestions}
