import socketio

from .Game import Game
from .GameTypes import Modes


class Room:
    def __init__(
        self,
        bot,
        room_id: int,
        name: str,
        players: int,
        max_players: int,
        has_password: bool,
        mode: Modes.Classic | Modes.Arrows | Modes.DeathArrows | Modes.Grapple | Modes.VTOL | Modes.Football,
        min_level: int,
        max_level: int
    ) -> None:
        self.bot = bot
        self.room_id: int = room_id
        self.name: str = name
        self.players: int = players
        self.max_players: int = max_players
        self.has_password: bool = has_password
        self.mode: Modes.Classic | Modes.Arrows | Modes.DeathArrows | Modes.Grapple | Modes.VTOL | Modes.Football = mode
        self.min_level: int = min_level
        self.max_level: int = max_level

    def join(self, password="") -> Game:
        return Game(
            self.bot,
            self.name,
            socketio.AsyncClient(ssl_verify=False, logger=True, engineio_logger=True),
            False,
            self.mode,
            False,
            self.bot.event_emitter,
            game_join_params=[self.room_id, password]
        )
