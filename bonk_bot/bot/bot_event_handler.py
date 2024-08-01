import pymitter

from bonk_bot.game import *
from bonk_bot.types import AnyTeam, AnyMode
from bonk_bot.bonk_maps import *


class BotEventHandler:
    """Class for holding event handlers templates."""

    def __init__(self) -> None:
        self._event_emitter = pymitter.EventEmitter()
        self._errors_handled = False

        @self.event_emitter.on("error")
        def on_error(error: Exception):
            if not self._errors_handled:
                raise error

    @property
    def event_emitter(self) -> pymitter.EventEmitter:
        return self._event_emitter

    # Event handle functions templates
    async def _on_player_ping(self, player: Player, ping: int) -> None:
        pass

    async def _on_game_connect(self, game: Game) -> None:
        pass

    async def _on_game_disconnect(self, game: Game) -> None:
        pass

    async def _on_player_join(self, player: Player) -> None:
        pass

    async def _on_player_leave(self, player: Player) -> None:
        pass

    async def _on_host_leave(self, old_host: Player, new_host: Player) -> None:
        pass

    async def _on_game_close(self, game: Game) -> None:
        pass

    async def _on_player_move(self, player_move: PlayerMove) -> None:
        pass

    async def _on_player_ready(self, player: Player) -> None:
        pass

    async def _on_match_abort(self, match: Match) -> None:
        pass

    async def _on_match_start(self, match: Match) -> None:
        pass

    async def _on_error(self, error: Exception) -> None:
        pass

    async def _on_player_team_change(self, player: Player, team: AnyTeam) -> None:
        pass

    async def _on_team_lock(self, game: Game) -> None:
        pass

    async def _on_team_unlock(self, game: Game) -> None:
        pass

    async def _on_message(self, message: Message) -> None:
        pass

    async def _on_player_kick(self, player: Player) -> None:
        pass

    async def _on_player_ban(self, player: Player) -> None:
        pass

    async def _on_bot_kick(self, game: Game) -> None:
        pass

    async def _on_bot_ban(self, game: Game) -> None:
        pass

    async def _on_mode_change(self, game: Game, mode: AnyMode) -> None:
        pass

    async def _on_rounds_change(self, game: Game, rounds: int) -> None:
        pass

    async def _on_map_change(self, game: Game, bonk_map: Union[OwnMap, Bonk2Map, Bonk2Map]) -> None:
        pass

    async def _on_afk_warn(self, game: Game) -> None:
        pass

    async def _on_map_request_host(self, map_request: MapRequestHost) -> None:
        pass

    async def _on_map_request_client(self, map_request: MapRequestClient) -> None:
        pass

    async def _on_player_balance(self, player: Player, balance: int) -> None:
        pass

    async def _on_teams_on(self, game: Game) -> None:
        pass

    async def _on_teams_off(self, game: Game) -> None:
        pass

    async def _on_replay(self, player: Player) -> None:
        pass

    async def _on_host_change(self, old_host: Player, new_host: Player) -> None:
        pass

    async def _on_friend_request(self, friend_request: FriendRequest) -> None:
        pass

    async def _on_match_countdown(self, game: Game, starts_in: int) -> None:
        pass

    async def _on_match_countdown_abort(self, game: Game) -> None:
        pass

    async def _on_player_level_up(self, player: Player, new_level: int) -> None:
        pass

    async def _on_xp_gain(self, game: Game, new_xp: int) -> None:
        pass

    async def _on_player_tab(self, player: Player) -> None:
        pass

    async def _on_player_tab_reset(self, player: Player) -> None:
        pass

    async def _on_new_room_name(self, game: Game, new_room_name: str) -> None:
        pass

    async def _on_new_room_password(self, game: Game) -> None:
        pass

    async def _on_new_room_password_clear(self, game: Game) -> None:
        pass
