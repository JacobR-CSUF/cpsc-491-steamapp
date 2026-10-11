# Cached versions of the Steam client calls (KAN-30).

# Same function names and arguments as the client (KAN-29), so callers can
# import from here instead of the client and get Redis caching for free.


from app.core.cache import cached
from app.services import steam_client

ONE_HOUR = 60 * 60
THIRTY_MINUTES = 30 * 60
ONE_DAY = 24 * 60 * 60


def get_player_summary(steam_id): # returns a dictionary with the player's summary information, such as their name, avatar, and online status
    return cached(
        f"steam:summary:{steam_id}", # the key used to store the cached value in Redis, which includes the player's Steam ID
        ONE_HOUR,
        lambda: steam_client.get_player_summary(steam_id), # fetches the player's summary information from the Steam API if it's not in the cache
    )


def get_owned_games(steam_id): # returns a dictionary with the player's owned games, including the app IDs and playtime for each game
    return cached(
        f"steam:games:{steam_id}", # the key used to store the cached value in Redis, which includes the player's Steam ID
        ONE_HOUR,
        lambda: steam_client.get_owned_games(steam_id),
    )


def get_player_achievements(steam_id, app_id): # returns a dictionary with the player's achievements for a specific game, including which achievements they have unlocked and their progress towards each achievement
    return cached(
        f"steam:achievements:{steam_id}:{app_id}", # the key used to store the cached value in Redis, which includes the player's Steam ID and the app ID of the game
        THIRTY_MINUTES,
        lambda: steam_client.get_player_achievements(steam_id, app_id), # fetches the player's achievements for the specified game from the Steam API if it's not in the cache
    )


def get_game_schema(app_id): # returns a dictionary with the game's schema, including the list of achievements and their descriptions, as well as any other relevant information about the game
    return cached(
        f"steam:schema:{app_id}",
        ONE_DAY,
        lambda: steam_client.get_game_schema(app_id), # fetches the game's schema from the Steam API if it's not in the cache
    )
