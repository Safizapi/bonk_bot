import datetime
import json
from typing import List, Union
from urllib.parse import unquote_plus
import requests
import socketio
import re
import asyncio
import nest_asyncio
import aiohttp
from functools import cached_property

from ..bonk_online import BonkOnline
from ..settings import PROTOCOL_VERSION, links
from ..friend_list import FriendList, LegacyFriend
from ..bonk_maps import OwnMap, Bonk2Map, Bonk1Map
from ..room import Room
from ..parsers import db_id_to_date, decode_avatar
from ..game import Game
from ..types import Servers, AnyServer, all_servers_list, Modes
from ..avatar import Avatar
from ..bot.bot_event_handler import BotEventHandler

nest_asyncio.apply()


class BonkBot(BotEventHandler):
    """
    Base class for AccountBonkBot and GuestBonkBot.

    :param username: bot username.
    :param is_guest: indicates whether the bot is a guest or not.
    :param xp: amount of xp on bot's account.
    """

    def __init__(
        self,
        username: str,
        is_guest: bool,
        xp: int,
        avatars: List[str],
        main_avatar: Avatar
    ) -> None:
        super().__init__()
        self.username: str = username
        self._is_guest: bool = is_guest
        self.xp: int = xp
        self._raw_avatars: List[str] = avatars
        self._main_avatar: Union[Avatar, None] = main_avatar
        self._games: List[Game] = []
        self._aiohttp_session = aiohttp.ClientSession()

    @property
    def is_guest(self) -> bool:
        return self._is_guest

    @property
    def level(self) -> int:
        """Returns account level from its XP."""

        if self.is_guest:
            return 0

        return int((self.xp / 100) ** 0.5 + 1)

    @cached_property
    def avatars(self) -> List[Avatar]:
        """Returns account avatars from encoded base64 strings."""

        avatars = []

        if not (self._raw_avatars is None):
            for raw_avatar in self._raw_avatars:
                avatars.append(decode_avatar(raw_avatar))

            return [decode_avatar(avatar) for avatar in self._raw_avatars]

        return [Avatar({"layers": [], "bc": 4492031})] * 5

    @property
    def main_avatar(self) -> Avatar:
        return self._main_avatar

    @main_avatar.setter
    def main_avatar(self, avatar: Union[Avatar, None]) -> None:
        """
        Changes bot's account session avatar.

        :param avatar: avatar to change (Avatar class instance). None argument sets default bonk.io avatar.
        """

        if not isinstance(avatar, Avatar) and not (avatar is None):
            raise TypeError("Avatar must be of type Avatar")

        if avatar is None:
            self._main_avatar = Avatar({"layers": [], "bc": 4492031})
        else:
            self._main_avatar = avatar

    @property
    def games(self) -> List[Game]:
        return self._games

    @property
    def aiohttp_session(self) -> aiohttp.ClientSession:
        return self._aiohttp_session

    async def run(self) -> None:
        """Prevents room connections from stopping and "starts" the bot."""

        tasks = []

        for game in self.games:
            if isinstance(game, Game):
                tasks.append(game.socket_client.wait())

        await asyncio.gather(*tasks)

        while len(self.games) > 0:
            await asyncio.sleep(0.1)

    async def stop(self) -> None:
        """Stops the bot."""

        for game in self.games:
            if isinstance(game, Game):
                await game.leave()

    def event(self, function) -> None:
        """
        Wrapper for async functions to make them handle bonk events.

        :param function: coroutine function to be called.
        """

        if not asyncio.iscoroutinefunction(function):
            raise TypeError("Event handler function is not a coroutine")

        attribute_name = "_" + function.__name__
        handler = self.__getattribute__(attribute_name)

        func_arg_count = function.__code__.co_argcount
        actual_arg_count = handler.__code__.co_argcount - 1

        if func_arg_count != actual_arg_count:
            raise TypeError(
                f"Handler expected to get {actual_arg_count} arguments, but got {func_arg_count}"
            )

        if attribute_name == "_on_error":
            self._errors_handled = True

        self.event_emitter.on(attribute_name.replace("_on_", ""), function)

    async def join_game_from_link(self, link: str) -> Game:
        """
        Joins a game from join link.

        :param link: link to join game.
        """

        return Game(
            self,
            None,
            "",
            socketio.AsyncClient(ssl_verify=False),
            False,
            Modes.Classic,
            False,
            True,
            False,
            game_join_params=[link]
        )

    async def create_game(
        self,
        name="",
        max_players=6,
        unlisted=False,
        password="",
        min_level=0,
        max_level=999,
        server: AnyServer = Servers.Warsaw
    ) -> Game:
        """
        Host a bonk.io game.

        :param name: Name of the room. It can only be a string. The default is "Test room".
        :param max_players: The amount of players that can join the game. The amount should be in range [1, 8] (def=6).
        :param unlisted: Indicates whether the game is hidden or not. True or False. Default is False.
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
            raise TypeError("Max players must be between 1 and 8")
        elif min_level > self.level:
            raise TypeError("Minimal cannot be greater than the account level")
        elif max_level < self.level:
            raise TypeError("Maximum level cannot be lower than the account level")
        elif not (server in all_servers_list):
            raise TypeError("Server param is not a server")

        return Game(
            self,
            server,
            name,
            socketio.AsyncClient(ssl_verify=False),
            True,
            Modes.Classic,
            True,
            False,
            False,
            game_create_params=[name, max_players, unlisted, password, min_level, max_level, server]
        )

    async def fetch_online(self) -> BonkOnline:
        """Returns current bonk online players."""

        async with self.aiohttp_session.get("https://bonk2.io/scripts/combinedplayercount.txt") as resp:
            data = json.loads(await resp.text())["bonk"]

        return BonkOnline(
            data["quick_classic"],
            data["quick_arrows"],
            data["quick_grapple"],
            data["custom"],
            data["quick_simple"],
            data["total"]
        )

    async def fetch_b2_maps(self, request: str, by_name=True, by_author=True) -> List[Bonk2Map]:
        """
        Returns list of bonk2 maps.

        :param request: Input string along which the search is performed.
        :param by_name: True if you want to search map by its name. Default is True.
        :param by_author: True if you want to search map by its author. Default is True.
        """

        async with self.aiohttp_session.post(
            url=links["map_get_b2"],
            data={
                "searchauthor": str(by_author).lower(),
                "searchmapname": str(by_name).lower(),
                "searchsort": "best",
                "searchstring": request,
                "startingfrom": 0
            }
        ) as resp:
            data = await resp.json()

        if data.get("e") == "invalid_options":
            raise TypeError("Invalid options for map searching")

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

    # why tf do you store bonk 1 maps data like that chaz mapid0=1597734&mapname0=hammer+vs+SUS+ptb+&creationdate...
    async def fetch_b1_maps(self, request: str, by_name=True, by_author=True) -> List[Bonk1Map]:
        """
        Returns list of bonk1 maps.

        :param request: Input string along which the search is performed.
        :param by_name: True if you want to search map by its name. Default is True.
        :param by_author: True if you want to search map by its author. Default is True.
        """

        async with self.aiohttp_session.post(
            url=links["map_get_b1"],
            data={
                "searchsort": "ctr",
                "searchauthor": str(by_author).lower(),
                "searchmapname": str(by_name).lower(),
                "startingfrom": 0,
                "searchstring": request
            }
        ) as resp:
            data = unquote_plus((await resp.json())["maps"])

        pattern = re.compile(r'mapid\d*=(\d*)&mapname\d*=([^-]*)&creationdate\d*=([^&]*)&modifieddate\d*=([^&]*)&thumbsup\d*=(\d*)&thumbsdown\d*=(\d*)&score\d*=\d*&authorname\d*=([^&]*)&leveldata\d*=([^&]*)')
        parsed_data = pattern.findall(data)

        return [
            Bonk1Map(
                int(bonk_map[0]),
                bonk_map[7],
                bonk_map[1],
                bonk_map[6],
                bonk_map[2],
                bonk_map[3],
                int(bonk_map[4]),
                int(bonk_map[5])
            ) for bonk_map in parsed_data
        ]

    async def fetch_rooms(self) -> List[Room]:
        """Returns list of rooms in the bonk.io room list."""

        async with self.aiohttp_session.post(
            url=links["rooms"],
            data={
                "version": PROTOCOL_VERSION,
                "gl": "n",
                "token": ""
            }
        ) as resp:
            data = await resp.json()

        return [
            Room(
                self,
                room["id"],
                room["roomname"],
                room["players"],
                room["maxplayers"],
                room["password"] == 1,
                room["mode_mo"],
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

    def __init__(
        self,
        token: str,
        user_id: int,
        username: str,
        is_guest: bool,
        xp: int,
        avatars: Union[List[str], None],
        main_avatar: Union[Avatar, None],
        legacy_friends: str
    ) -> None:
        super().__init__(username, is_guest, xp, avatars, main_avatar)
        self._token: str = token
        self.user_id: int = user_id
        self._raw_legacy_friends: str = legacy_friends

    @property
    def token(self) -> str:
        return self._token

    @cached_property
    def account_creation_date(self) -> Union[datetime.datetime, str]:
        """Returns account creation date from its DBID."""

        return db_id_to_date(self.user_id)

    @cached_property
    def legacy_friends(self) -> List[LegacyFriend]:
        """Returns list of bonk 1 account friends."""

        return [LegacyFriend(self, friend) for friend in self._raw_legacy_friends.split("#")]

    async def fetch_own_maps(self) -> List[OwnMap]:
        """Returns list of maps created on the account."""

        async with self.aiohttp_session.post(
            url=links["map_get_own"],
            data={
                "token": self.token,
                "startingfrom": "0"
            }
        ) as resp:
            data = await resp.json()

        return [
            OwnMap(
                self,
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

    async def fetch_favorite_maps(self) -> List[Bonk2Map]:
        async with self.aiohttp_session.post(
            url=links["map_get_fav"],
            data={
                "token": self.token,
                "startingfrom": "0"
            }
        ) as response:
            data = await response.json()

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

    async def fetch_friend_list(self) -> FriendList:
        """Returns account friend list that contains friends and friend requests."""

        async with self.aiohttp_session.post(
            url=links["friends"],
            data={
                "token": self.token,
                "task": "getfriends"
            }
        ) as resp:
            data = await resp.json()

        return FriendList(self, data)


class GuestBonkBot(BonkBot):
    """
    Bot class for bonk.io guest account.

    :param username: guest account name.
    :param is_guest: whether account is guest or not (True by default since class is used by bonk.io guest account).
    :param xp: the amount of xp on account (0 by default).
    """

    def __init__(
        self,
        username: str,
        is_guest: bool,
        xp: int,
        avatars: Union[List[str], None],
        main_avatar: Union[Avatar, None]
    ) -> None:
        super().__init__(username, is_guest, xp, avatars, main_avatar)


def bonk_account_login(username: str, password: str) -> AccountBonkBot:
    """
    Creates bot on bonk.io account.

    :param username: bonk.io account username. Be aware that some usernames like "___" or "%_e" aren't supported.
    :param password: bonk.io account password.

    Example usage::

        bot = bonk_account_login("name", "pass")
        print(bot.username)
    """

    data = requests.post(
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

    avatars = [data["avatar1"], data["avatar2"], data["avatar3"], data["avatar4"], data["avatar5"]]

    bot = AccountBonkBot(
        data["token"],
        data["id"],
        data["username"],
        False,
        data["xp"],
        avatars,
        decode_avatar(avatars[data["activeAvatarNumber"] - 1]),
        data["legacyFriends"]
    )

    return bot


def bonk_guest_login(username: str) -> GuestBonkBot:
    """
    Creates bot without bonk.io account (some methods like get_friend_list() are unavailable).
    Note that guest account can change its nickname if someone in the game has the same nickname.

    Example usage::

        bot = bonk_account_login("name")
        print(bot.username)

    :param username: guest username.
    """

    pattern = re.compile(r"""[:;,.`~!@"'?#$%^&*()+=/|><\-]""")

    if not (len(username) in range(2, 16)) or pattern.findall(username) or not username.isascii():
        raise BonkLoginError("Username must be between 2 and 16 characters and contain only numbers, letters and _")

    bot = GuestBonkBot(
        username,
        True,
        0,
        None,
        Avatar({"layers": [], "bc": 4492031})
    )

    return bot


class BonkLoginError(Exception):
    """Raised when bonk login is failed."""

    def __init__(self, message: str) -> None:
        self.message = message
