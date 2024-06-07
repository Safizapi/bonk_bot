import asyncio
from random import shuffle
from string import ascii_lowercase
import socketio
from typing import List

from .BonkMap import BonkMap
from .Settings import PROTOCOL_VERSION, session, links
from .GameTypes import Modes, Teams
from .Parsers import team_from_number, mode_from_short_name


class Game:
    def __init__(
        self,
        bot,
        socket_client: socketio.AsyncClient,
        is_host: bool,
        mode: Modes.Classic | Modes.Arrows | Modes.DeathArrows | Modes.Grapple | Modes.VTOL | Modes.Football,
        is_created_by_bot: bool,
        game_create_params: list | None = None,
        game_join_params: list | None = None,
        is_connected: bool = False,
    ) -> None:
        self.bot = bot
        self.players: List[Player] = []
        self.messages: List[Message] = []
        self.is_host: bool = is_host
        self.is_bot_ready: bool = False
        self.mode: Modes.Classic | Modes.Arrows | Modes.DeathArrows | Modes.Grapple | Modes.VTOL | Modes.Football = mode
        self.teams_toggle: bool = False
        self.teams_lock_toggle: bool = False
        self.rounds: int = 3
        self.bonk_map: BonkMap | None = None
        self.__initial_state: str = ""
        self.__socket_client: socketio.AsyncClient = socket_client
        self.__is_created_by_bot: bool = is_created_by_bot
        self.__game_create_params: list | None = game_create_params
        self.__game_join_params: list | None = game_join_params
        self.__is_connected: bool = is_connected

    async def connect(self) -> None:
        self.bot.games.append(self)

        if self.__is_created_by_bot:
            await self.__create(*self.__game_create_params)
        else:
            await self.__join(*self.__game_join_params)

    @staticmethod
    def __get_peer_id() -> str:
        alph = list(ascii_lowercase + "0123456789")
        shuffle(alph)
        return "".join(alph[:10]) + "000000"

    async def play(self) -> None:
        pass
        # if not self.is_host:
        #     raise Exception("Can't start a game: bot is not a host")
        #
        # await self.__socket_client.emit(
        #     5,
        #     {
        #
        #     }
        # )

    async def change_bot_team(
        self,
        team: Teams.Spectator | Teams.FFA | Teams.Red | Teams.Blue | Teams.Green | Teams.Yellow
    ) -> None:
        if not (
            isinstance(team, Teams.Spectator) or
            isinstance(team, Teams.FFA) or
            isinstance(team, Teams.Red) or
            isinstance(team, Teams.Blue) or
            isinstance(team, Teams.Green) or
            isinstance(team, Teams.Yellow)
        ):
            raise ValueError("Can't move player: team param is not a valid team")

        await self.__socket_client.emit(
            6,
            {
                "targetTeam": team.number
            }
        )

    async def toggle_team_lock(self, flag: bool) -> None:
        if not self.is_host:
            raise BotIsNotAHostError("Cannot lock teams due the lack of bot permissions")

        await self.__socket_client.emit(
            7,
            {
                "teamLock": flag
            }
        )
        self.teams_lock_toggle = True

    async def send_message(self, message: str) -> None:
        if self.__is_connected:
            await self.__socket_client.emit(
                10,
                {
                    "message": message
                }
            )

    async def toggle_bot_ready(self, flag: bool) -> None:
        await self.__socket_client.emit(
            16,
            {
                "ready": flag
            }
        )
        self.is_bot_ready = flag

    async def set_mode(
        self,
        mode: Modes.Classic | Modes.Arrows | Modes.DeathArrows | Modes.Grapple | Modes.VTOL | Modes.Football
    ) -> None:
        if not self.is_host:
            raise BotIsNotAHostError("Cannot set mode due the lack of bot permissions")
        if not (
            isinstance(mode, Modes.Classic) or
            isinstance(mode, Modes.Arrows) or
            isinstance(mode, Modes.DeathArrows) or
            isinstance(mode, Modes.Grapple) or
            isinstance(mode, Modes.VTOL) or
            isinstance(mode, Modes.Football)
        ):
            raise ValueError("Can't move player: team param is not a valid team")

        await self.__socket_client.emit(
            20,
            {
                "ga": mode.ga,
                "mo": mode.short_name
            }
        )
        self.mode = mode

    async def set_rounds(self, rounds: int) -> None:
        if not self.is_host:
            raise BotIsNotAHostError("Cannot set rounds due the lack of bot permissions")

        await self.__socket_client.emit(
            21,
            {
                "w": rounds
            }
        )
        self.rounds = rounds

    async def set_map(self, bonk_map: BonkMap) -> None:
        if not self.is_host:
            raise BotIsNotAHostError("Cannot change map due the lack of bot permissions")

        await self.__socket_client.emit(
            23,
            {
                "m": bonk_map.level_data
            }
        )
        self.bonk_map = bonk_map

    async def toggle_teams(self, flag: bool) -> None:
        if not self.is_host:
            raise BotIsNotAHostError("Cannot toggle teams due the lack of bot permissions")

        await self.__socket_client.emit(
            32,
            {
                "t": flag
            }
        )
        self.teams_toggle = flag

    async def record(self) -> None:
        await self.__socket_client.emit(33)

    async def leave(self) -> None:
        await self.__socket_client.disconnect()
        self.__is_connected = False
        self.players = []
        self.messages = []

    async def close(self) -> None:
        if not self.is_host:
            raise BotIsNotAHostError("Cannot close game due the lack of bot permissions")

        await self.__socket_client.emit(50)
        await self.leave()

    async def wait(self):
        await self.__socket_client.wait()

    async def __create(
        self,
        name="Test room",
        max_players=6,
        is_hidden=False,
        password="",
        min_level=0,
        max_level=999
    ) -> None:
        socket_address = f"https://b2stockholm1.bonk.io/socket.io"

        @self.__socket_client.event
        async def connect():
            print('connection established')
            self.__is_connected = True
            self.is_host = True
            new_peer_id = self.__get_peer_id()

            await self.__socket_client.emit(
                12,
                {
                    "peerID": new_peer_id,
                    "roomName": name,
                    "maxPlayers": max_players,
                    "password": password,
                    "dbid": self.bot.user_id,
                    "guest": False,
                    "minLevel": min_level,
                    "maxLevel": max_level,
                    "latitude": 57.7686,
                    "longitude": 40.9252,
                    "country": "RU",
                    "version": PROTOCOL_VERSION,
                    "hidden": int(is_hidden),
                    "quick": False,
                    "mode": "custom",
                    "token": self.bot.token,
                    "avatar": {
                        "layers": [],
                        "bc": 4492031
                    }
                }
            )

            self.players.append(
                Player(
                    self.bot,
                    self,
                    self.__socket_client,
                    True,
                    new_peer_id,
                    self.bot.username,
                    False,
                    self.bot.get_level(),
                    False,
                    False,
                    Teams.FFA(),
                    0,
                    {
                        "layers": [],
                        "bc": 0
                    }
                )
            )

        await self.__socket_events()

        await self.__socket_client.connect(socket_address)
        await self.__keep_alive()

        while not self.__is_connected:
            await asyncio.sleep(1)

    async def __join(self, room_id: int, password="") -> None:
        room_data = session.post(
            links["get_room_address"],
            {
                "id": room_id
            }
        ).json()

        if room_data.get("e") == "ratelimited":
            raise ConnectionRateLimitedError("Cannot connect to server, sent to many requests")

        @self.__socket_client.event
        async def connect():
            print('connection established')
            await self.__socket_client.emit(
                13,
                {
                    "joinID": room_data["address"],
                    "roomPassword": password,
                    "guest": False,
                    "dbid": 2,
                    "version": PROTOCOL_VERSION,
                    "peerID": self.__get_peer_id(),
                    "bypass": "",
                    "token": self.bot.token,
                    "avatar": {
                        "layers": [],
                        "bc": 4492031
                    }
                }
            )

            self.__is_connected = True

        await self.__socket_events()

        await self.__socket_client.connect(f"https://{room_data['server']}.bonk.io/socket.io")
        await self.__keep_alive()

        while not self.__is_connected:
            await asyncio.sleep(1)

    async def __keep_alive(self) -> None:
        while self.__is_connected:
            await self.__socket_client.emit(
                18,
                {
                    "jsonrpc": "2.0",
                    "id": "9",
                    "method": "timesync",
                }
            )
            await asyncio.sleep(5)

    async def __socket_events(self) -> None:
        @self.__socket_client.on(3)
        async def players_on_bot_join(w1, w2, players: list, w3, w4, w5, w6, w7):
            [
                self.players.append(
                    Player(
                        self.bot,
                        self,
                        self.__socket_client,
                        False,
                        player["peerID"],
                        player["userName"],
                        player["guest"],
                        player["level"],
                        player["ready"],
                        player["tabbed"],
                        team_from_number(player["team"]),
                        players.index(player),
                        player["avatar"]
                    )
                ) for player in players if player is not None
            ]

            bot = [player for player in self.players if player.username == self.bot.username and not player.is_guest][0]
            self.players[self.players.index(bot)].is_bot = True

            for x in self.players:
                if x.team.number > 1:
                    self.teams_toggle = True

        @self.__socket_client.on(4)
        async def on_player_join(short_id: int, peer_id: str, username: str, is_guest: bool, level: int, w, avatar: dict):
            self.players.append(
                Player(
                    self.bot,
                    self,
                    self.__socket_client,
                    False,
                    peer_id,
                    username,
                    is_guest,
                    level,
                    False,
                    False,
                    Teams.FFA(),
                    short_id,
                    avatar
                )
            )

            await self.__socket_client.emit(
                11,
                {
                    "sid": short_id,
                    "gs": {
                        "map": {
                            "v": 13,
                            "s": {
                                "re": False,
                                "nc": False,
                                "pq": 1,
                                "gd": 25,
                                "fl": False
                            },
                            "physics": {
                                "shapes": [],
                                "fixtures": [],
                                "bodies": [],
                                "bro": [],
                                "joints": [],
                                "ppm": 12
                            },
                            "spawns": [],
                            "capZones": [],
                            "m": {
                                "a": "💀",
                                "n": "Test map",
                                "dbv": 2,
                                "dbid": 1157352,
                                "authid": -1,
                                "date": "2024-06-04 06:03:34",
                                "rxid": 0,
                                "rxn": "",
                                "rxa": "",
                                "rxdb": 1,
                                "cr": [
                                    "💀"
                                ],
                                "pub": True,
                                "mo": "",
                                "vu": 0,
                                "vd": 0
                            }
                        },
                        "gt": 2,
                        "wl": "pog",
                        "q": False,
                        "tl": False,
                        "tea": False,
                        "ga": "b",
                        "mo": "b",
                        "bal": [],
                        "GMMode": ""
                    }
                }
            )

        @self.__socket_client.on(5)
        async def on_player_left(short_id: int, w) -> None:
            left_player = [player for player in self.players if player.short_id == short_id][0]
            self.players.remove(left_player)

        @self.__socket_client.on(8)
        async def on_player_ready(short_id: int, flag: bool) -> None:
            player = [player for player in self.players if player.short_id == short_id][0]
            player.is_ready = flag

        @self.__socket_client.on(16)
        async def on_error(error):
            print(error)

        @self.__socket_client.on(18)
        async def on_player_team_change(short_id: int, team_number: int) -> None:
            player = [player for player in self.players if player.short_id == short_id][0]
            player.team = team_from_number(team_number)

        @self.__socket_client.on(19)
        async def on_team_lock(flag: bool) -> None:
            self.teams_lock_toggle = flag

        @self.__socket_client.on(20)
        async def on_message(short_id: int, message: str) -> None:
            author = [player for player in self.players if player.short_id == short_id][0]
            self.messages.append(Message(message, author, self))

        @self.__socket_client.on(21)
        async def on_lobby_load(data: dict) -> None:
            self.mode = mode_from_short_name(data["mo"])
            self.teams_lock_toggle = data["tl"]
            self.rounds = data["wl"]

        @self.__socket_client.on(24)
        async def on_player_kick(short_id: int, kick_only: bool) -> None:
            player = [player for player in self.players if player.short_id == short_id][0]
            self.players.remove(player)

            if player.is_bot:
                await self.leave()

        @self.__socket_client.on(26)
        async def on_mode_change(ga, mode_short_name: str) -> None:
            self.mode = mode_from_short_name(mode_short_name)

        @self.__socket_client.on(29)
        async def on_map_change(initial_state: str) -> None:
            pass

        @self.__socket_client.on(36)
        async def on_player_balance(short_id: int, percents: int) -> None:
            player = [player for player in self.players if player.short_id == short_id][0]
            player.balanced_by = percents

        @self.__socket_client.on(39)
        async def on_teams_toggle(flag: bool) -> None:
            self.teams_toggle = flag

        @self.__socket_client.on(41)
        async def on_host_change(data: dict) -> None:
            old_host = [player for player in self.players if player.short_id == data["oldHost"]][0]
            new_host = [player for player in self.players if player.short_id == data["newHost"]][0]

            if old_host.is_bot and not new_host.is_bot:
                self.is_host = False

        @self.__socket_client.event
        async def disconnect():
            print("disconnected")


class Player:
    def __init__(
        self,
        bot,
        game: Game,
        socket_client: socketio.AsyncClient,
        is_bot: bool,
        peer_id: str,
        username: str,
        is_guest: bool,
        level: int,
        is_ready: bool,
        is_tabbed: bool,
        team: Teams.Spectator | Teams.FFA | Teams.Red | Teams.Blue | Teams.Green | Teams.Yellow,
        short_id: int,
        avatar: dict
    ) -> None:
        self.bot = bot
        self.is_bot: bool = is_bot
        self.game: Game = game
        self.username: str = username
        self.is_guest: bool = is_guest
        self.level: int = level
        self.is_ready: bool = is_ready
        self.is_tabbed: bool = is_tabbed
        self.team: Teams.Spectator | Teams.FFA | Teams.Red | Teams.Blue | Teams.Green | Teams.Yellow = team
        self.balanced_by: int = 0
        self.short_id: int = short_id
        self.avatar: dict = avatar
        self.__socket_client: socketio.AsyncClient = socket_client
        self.__peer_id: str = peer_id

    async def send_friend_request(self) -> None:
        await self.__socket_client.emit(
            35,
            {
                "id": self.short_id
            }
        )

    async def give_host(self) -> None:
        if not self.game.is_host:
            raise BotIsNotAHostError("Cannot give host due the lack of bot permissions")

        await self.__socket_client.emit(
            34,
            {
                "id": self.short_id
            }
        )
        self.game.is_host = False

    async def kick(self) -> None:
        if not self.game.is_host:
            raise BotIsNotAHostError("Cannot kick player due the lack of bot permissions")

        await self.__socket_client.emit(
            9,
            {
                "banshortid": self.short_id,
                "kickonly": True
            }
        )

    async def ban(self) -> None:
        if not self.game.is_host:
            raise BotIsNotAHostError("Cannot ban player due the lack of bot permissions")

        await self.__socket_client.emit(
            9,
            {
                "banshortid": self.short_id,
                "kickonly": False
            }
        )

    async def move_to_team(
        self,
        team: Teams.Spectator | Teams.FFA | Teams.Red | Teams.Blue | Teams.Green | Teams.Yellow
    ) -> None:
        if not self.game.is_host:
            raise BotIsNotAHostError("Cannot move player due the lack of bot permissions")
        if not (
            isinstance(team, Teams.Spectator) or
            isinstance(team, Teams.FFA) or
            isinstance(team, Teams.Red) or
            isinstance(team, Teams.Blue) or
            isinstance(team, Teams.Green) or
            isinstance(team, Teams.Yellow)
        ):
            raise ValueError("Can't move player: team param is not a valid team")

        await self.__socket_client.emit(
            26,
            {
                "targetID": self.short_id,
                "targetTeam": team.number
            }
        )
        self.team = team

    async def balance(self, percents: int) -> None:
        if not self.game.is_host:
            raise BotIsNotAHostError("Cannot balance player due the lack of bot permissions")
        if not (percents in range(-100, 101)):
            raise ValueError("Can't balance player: percents param is not in range [-100, 100]")

        await self.__socket_client.emit(
            29,
            {
                "sid": self.short_id,
                "bal": percents
            }
        )
        self.balanced_by = percents


class Message:
    def __init__(self, content: str, author: Player, game: Game) -> None:
        self.content: str = content
        self.author: Player = author
        self.game: Game = game


class ConnectionRateLimitedError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class BotIsNotAHostError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
