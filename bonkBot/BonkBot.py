import datetime
from typing import List
import socketio
import asyncio

from .Settings import session, PROTOCOL_VERSION, links
from .FriendList import FriendList
from .BonkMap import BonkMap
from .Room import Room
from .Parsers import db_id_to_date
from .Game import Game
from .GameTypes import Modes
from .Parsers import mode_from_short_name


class BonkBot:
    def __init__(self, token: str, user_id: int, username: str, xp: int, avatars: list, legacy_friends: list) -> None:
        self.token: str = token
        self.user_id: int = user_id
        self.username: str = username
        self.xp: int = xp
        self.avatars: list = avatars
        self.legacy_friends: list = legacy_friends
        self.games: List[Game] = []

    async def run(self) -> None:
        tasks = []

        for game in self.games:
            tasks.append(game.wait())

        await asyncio.gather(*tasks)

    def create_game(
        self,
        name="Test room",
        max_players=6,
        is_hidden=False,
        password="",
        min_level=0,
        max_level=999
    ) -> Game:
        return Game(
            self,
            socketio.AsyncClient(ssl_verify=False, logger=True, engineio_logger=True),
            True,
            Modes.Classic(),
            True,
            game_create_params=[name, max_players, is_hidden, password, min_level, max_level]
        )

    # Credits to https://shaunx777.github.io/dbid2date/
    def get_creation_date(self) -> datetime.datetime or str:
        return db_id_to_date(self.user_id)

    def get_level(self) -> int:
        return int((self.xp / 100) ** 0.5 + 1)

    def get_friend_list(self) -> FriendList:
        data = session.post(
            links["friends"],
            {
                "token": self.token,
                "task": "getfriends"
            }
        ).json()

        return FriendList(self, self.token, data)

    def get_b2_maps(self, request: str, by_name=True, by_author=False) -> List[BonkMap]:
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
            BonkMap(
                self.token,
                bonk_map["id"],
                bonk_map["leveldata"],
                bonk_map["authorname"],
                bonk_map["name"],
                bonk_map["publisheddate"],
                True,
                bonk_map["vu"],
                bonk_map["vd"]
            )
            for bonk_map in data["maps"]
        ]

    def get_b1_maps(self, request: str, by_name: bool, by_author: bool) -> List[BonkMap]:
        pass

    def get_own_maps(self) -> List[BonkMap]:
        data = session.post(
            "https://bonk2.io/scripts/map_getown.php",
            {
                "token": self.token,
                "startingfrom": "0"
            }
        ).json()

        return [
            BonkMap(
                self.token,
                bonk_map["id"],
                bonk_map["leveldata"],
                bonk_map["authorname"],
                bonk_map["name"],
                bonk_map["creationdate"],
                bonk_map["published"] == 1,
                bonk_map["vu"],
                bonk_map["vd"]
            )
            for bonk_map in data["maps"]
        ]

    def get_rooms(self) -> List[Room]:
        data = session.post(
            links["rooms"],
            {
                "version": PROTOCOL_VERSION,
                "gl": "n",
                "token": self.token
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


def bonk_login(username: str, password: str) -> BonkBot:
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

    return BonkBot(
        data["token"],
        data["id"],
        data["username"],
        data["xp"],
        [data["avatar1"], data["avatar2"], data["avatar3"], data["avatar4"], data["avatar5"]],
        data["legacyFriends"].split("#")
    )


class BonkLoginError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
