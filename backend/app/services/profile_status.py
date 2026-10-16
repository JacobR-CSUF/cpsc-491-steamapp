from enum import Enum

from app.services import steam_data
from app.services.steam_client import PrivateProfileError


class ProfileStatus(str, Enum):
    public = "public"
    not_found = "not_found"
    profile_private = "profile_private"
    games_private = "games_private"
    playtime_hidden = "playtime_hidden"


STATUS_MESSAGES = {
    ProfileStatus.public: "Profile is public.",
    ProfileStatus.not_found: "No Steam profile matches this ID.",
    ProfileStatus.profile_private: "This Steam profile is private.",
    ProfileStatus.games_private: "This player's game details are private.",
    ProfileStatus.playtime_hidden: "This player's playtime is hidden.",
}


def get_profile_status(steam_id: str) -> ProfileStatus:
    summary = steam_data.get_player_summary(steam_id)
    if summary is None:
        return ProfileStatus.not_found

    if summary.get("communityvisibilitystate") != 3:
        return ProfileStatus.profile_private

    try:
        games = steam_data.get_owned_games(steam_id)
    except PrivateProfileError:
        return ProfileStatus.games_private

    if games and all(game.get("playtime_forever", 0) == 0 for game in games):
        return ProfileStatus.playtime_hidden

    return ProfileStatus.public
