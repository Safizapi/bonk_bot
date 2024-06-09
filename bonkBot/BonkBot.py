import datetime
from typing import List
import socketio
import asyncio
from pymitter import EventEmitter
import nest_asyncio

from .Settings import session, PROTOCOL_VERSION, links
from .FriendList import FriendList
from .BonkMaps import OwnMap, Bonk2Map, Bonk1Map
from .Room import Room
from .Parsers import db_id_to_date
from .Game import Game
from .Types import Servers, Modes
from .Parsers import mode_from_short_name

nest_asyncio.apply()


class BonkBot:
    """
    Base class for AccountBonkBot and GuestBonkBot.

    :param username: bot username.
    :param is_guest: indicates whether the bot is a guest or not.
    :param xp: amount of xp on bot's account.
    """

    def __init__(self, username: str, is_guest: bool, xp: int) -> None:
        self.username: str = username
        self.is_guest: bool = is_guest
        self.xp: int = xp
        self.avatar: dict = {"layers": [], "bc": 0}
        self.games: List[Game] = []
        self.event_emitter = EventEmitter()
        self.on = self.event_emitter.on

    async def run(self) -> None:
        """Prevents room connections from stopping and "starts" the bot."""

        tasks = []

        for game in self.games:
            tasks.append(game.wait())

        await asyncio.gather(*tasks)

    async def stop(self) -> None:
        """Stops the bot."""

        for game in self.games:
            await game.leave()

    async def create_game(
        self,
        name="Test room",
        max_players=6,
        is_hidden=False,
        password="",
        min_level=0,
        max_level=999,
        server=Servers.Warsaw()
    ) -> Game:
        """
        Host a bonk.io game.

        :param name: Name of the room. It can only be a string. The default is "Test room".
        :param max_players: The amount of players that can join the game. The amount should be in range [1, 8] (def=6).
        :param is_hidden: Indicates whether the game is hidden or not. True or False. Default is False.
        :param password: The password that is required from other players to join the game. Default is "" (no password).
        :param min_level: The minimal level that is required from other players to join the game. Default is 0.
        :param max_level: The maximal level that is required from other players to join the game. Default is 999.
        :param server: The server to join the game. Default is Servers.Warsaw().

        Example usage::

            bot = bonk_account_login("name", "pass")

            async def main():
                game = await bot.create_game()
                await bot.run()

            asyncio.run(main())
        """

        if max_players < 1 or max_players > 8:
            raise ValueError("Max players must be between 1 and 8")
        if min_level > self.get_level():
            raise ValueError("Minimal cannot be greater than the account level")
        if max_level < self.get_level():
            raise ValueError("Maximum level cannot be lower than the account level")
        if not (
            isinstance(server, Servers.Stockholm) or
            isinstance(server, Servers.Warsaw) or
            isinstance(server, Servers.Brazil) or
            isinstance(server, Servers.SanFrancisco) or
            isinstance(server, Servers.Atlanta) or
            isinstance(server, Servers.Mississippi) or
            isinstance(server, Servers.Dallas) or
            isinstance(server, Servers.Frankfurt) or
            isinstance(server, Servers.London) or
            isinstance(server, Servers.NewYork) or
            isinstance(server, Servers.Seattle) or
            isinstance(server, Servers.Seoul) or
            isinstance(server, Servers.Sydney)
        ):
            raise ValueError("Server param is not a server")

        game = Game(
            self,
            name,
            socketio.AsyncClient(ssl_verify=False),
            True,
            Modes.Classic(),
            True,
            self.event_emitter,
            game_create_params=[name, max_players, is_hidden, password, min_level, max_level, server]
        )
        await game.connect()

        return game

    def get_level(self) -> int:
        """Returns account level from its XP."""
        if self.is_guest:
            return 0

        return int((self.xp / 100) ** 0.5 + 1)

    @staticmethod
    def get_b2_maps(request: str, by_name=True, by_author=True) -> List[Bonk2Map]:
        """
        Returns list of bonk2 maps.

        :param request: Input string along which the search is performed.
        :param by_name: True if you want to search map by its name. Default is True.
        :param by_author: True if you want to search map by its author. Default is True.
        """

        data = session.post(
            links["map_get_b2"],
            {
                "searchauthor": str(by_author).lower(),
                "searchmapname": str(by_name).lower(),
                "searchsort": "best",
                "searchstring": request,
                "startingfrom": 0
            }
        ).json()

        if data.get("e") == "invalid_options":
            raise ValueError("Invalid options for map searching")

        return [
            Bonk2Map(
                bonk_map["id"],
                bonk_map["leveldata"],
                bonk_map["name"],
                bonk_map["authorname"],
                bonk_map["publisheddate"],
                bonk_map["vu"],
                bonk_map["vd"]
            )
            for bonk_map in data["maps"]
        ]

    # why tf do you store bonk 1 maps data like that, chaz? mapid0=1597734&mapname0=hammer+vs+SUS+ptb+&creationdate...
    # @staticmethod
    # def get_b1_maps(request: str, by_name=True, by_author=True) -> List[Bonk1Map]:
    #     pass

    def get_rooms(self) -> List[Room]:
        """Returns list of rooms in the bonk.io room list."""

        data = session.post(
            links["rooms"],
            {
                "version": PROTOCOL_VERSION,
                "gl": "n",
                "token": ""
            }
        ).json()

        return [
            Room(
                self,
                room["id"],
                room["roomname"],
                room["players"],
                room["maxplayers"],
                room["password"] == 1,
                mode_from_short_name(room["mode_mo"]),
                room["minlevel"],
                room["maxlevel"]
            ) for room in data["rooms"]
        ]


class AccountBonkBot(BonkBot):
    """
    Bot class for bonk.io account.

    :param token: session token that is received when logging into bonk.io account and required for some bonk api calls.
    :param user_id: account database ID.
    :param username: account name.
    :param is_guest: whether account is guest or not (False by default since class is used by bonk.io account).
    :param xp: the amount of xp on account.
    :param legacy_friends: bonk 1 (flash version) friends of the account.
    """

    def __init__(self, token: str, user_id: int, username: str, is_guest: bool, xp: int, legacy_friends: list) -> None:
        super().__init__(username, is_guest, xp)
        self.token = token
        self.user_id = user_id
        self.legacy_friends = legacy_friends

    def get_creation_date(self) -> datetime.datetime or str:
        """Returns account creation date from its DBID."""

        return db_id_to_date(self.user_id)

    def get_own_maps(self) -> List[OwnMap]:
        """Returns list of maps created on the account."""

        data = session.post(
            "https://bonk2.io/scripts/map_getown.php",
            {
                "token": self.token,
                "startingfrom": "0"
            }
        ).json()

        return [
            OwnMap(
                self.token,
                bonk_map["id"],
                bonk_map["leveldata"],
                bonk_map["name"],
                bonk_map["creationdate"],
                bonk_map["published"] == 1,
                bonk_map["vu"],
                bonk_map["vd"]
            )
            for bonk_map in data["maps"]
        ]

    def get_friend_list(self) -> FriendList:
        """Returns account friend list that contains friends and friend requests."""

        data = session.post(
            links["friends"],
            {
                "token": self.token,
                "task": "getfriends"
            }
        ).json()

        return FriendList(self, self.token, data)


class GuestBonkBot(BonkBot):
    """
    Bot class for bonk.io guest account.

    :param username: guest account name.
    :param is_guest: whether account is guest or not (True by default since class is used by bonk.io guest account).
    :param xp: the amount of xp on account (0 by default).
    """

    def __init__(self, username: str, is_guest: bool, xp: int) -> None:
        super().__init__(username, is_guest, xp)


def bonk_account_login(username: str, password: str) -> AccountBonkBot:
    """
    Creates bot on bonk.io account.

    :param username: bonk.io account username.
    :param password: bonk.io account password.

    Example usage::

        bot = bonk_account_login("name", "pass")
        print(bot.username)
    """

    data = session.post(
        links["login"],
        {
            "username": username,
            "password": password,
            "remember": "false"
        }
    ).json()

    if data.get("e") == "username_fail":
        raise BonkLoginError(f"Invalid username {username}")
    elif data.get("e") == "password":
        raise BonkLoginError(f"Invalid password for account {username}")

    return AccountBonkBot(
        data["token"],
        data["id"],
        data["username"],
        False,
        data["xp"],
        data["legacyFriends"].split("#")
    )


def bonk_guest_login(username: str) -> GuestBonkBot:
    """
    Creates bot without bonk.io account (some methods like get_friend_list() are unavailable).
    Note that guest account can change its nickname if someone in the game has the same nickname.

    Example usage::

        bot = bonk_account_login("name")
        print(bot.username)

    :param username: guest username.
    """

    if not (len(username) in range(2, 16)):
        raise BonkLoginError("Username must be between 2 and 16 characters")

    return GuestBonkBot(username, True, 0)


class BonkLoginError(Exception):
    """Raised when bonk login is failed."""

    def __init__(self, message: str) -> None:
        self.message = message
