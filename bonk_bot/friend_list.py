import datetime
from functools import cached_property
from typing import List, Union, TYPE_CHECKING
import socketio

from .settings import links
from .parsers import db_id_to_date
from .game import Game
from .types import Modes

if TYPE_CHECKING:
    from .bot import AccountBonkBot


class Friend:
    """
    Class for holding account's friends.

    :param bot: bot class that uses the account.
    :param user_id: friend's account database ID.
    :param username: friend's account username.
    :param room_id: the room ID where friend is playing.
    """

    def __init__(
        self,
        bot: "AccountBonkBot",
        user_id: int,
        username: str,
        room_id: Union[int, None]
    ) -> None:
        self._bot: "AccountBonkBot" = bot
        self._user_id: int = user_id
        self._username: str = username
        self._room_id: Union[int, None] = room_id

    @property
    def bot(self) -> "AccountBonkBot":
        return self._bot

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def room_id(self) -> int:
        return self._room_id

    async def unfriend(self) -> None:
        """Remove friend from account friend list."""

        await self.bot.aiohttp_session.post(
            url=links["friends"],
            data={
                "token": self.bot.token,
                "task": "unfriend",
                "theirid": self.user_id
            }
        )

    @cached_property
    def account_creation_date(self) -> Union[datetime.datetime, str]:
        """Get friend's account creation date."""

        return db_id_to_date(self.user_id)

    async def join_game(self) -> Game:
        """
        Establish connection with room where friend is playing.

        Example usage::

            bot = bonk_account_login("name", "pass")

            friend_list = bot.get_friend_list()
            friend = [friend for friend in friend_list.get_friends() if friend.username == "test" and friend.room_id][0]

            async def main():
                game = friend.join_game()
                await game.send_message("Hello!")

                await bot.run()

            asyncio.run(main())
        """

        return Game(
            self.bot,
            None,
            "Unknown name",
            socketio.AsyncClient(ssl_verify=False),
            False,
            Modes.Classic,
            False,
            False,
            True,
            game_join_params=[self.room_id]
        )


class FriendRequest:
    """
    Class for holding account's friend requests.

    :param bot: bot class that uses account.
    :param user_id: account database ID.
    :param username: account username.
    :param date: the date of sending friend request.
    """

    def __init__(
        self,
        bot: "AccountBonkBot",
        user_id: int,
        username: str,
        date: str
    ) -> None:
        self._bot: "AccountBonkBot" = bot
        self._user_id: int = user_id
        self._username: str = username
        self._date: str = date

    @property
    def bot(self) -> "AccountBonkBot":
        return self._bot

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def date(self) -> str:
        return self._date

    async def accept(self) -> None:
        """Accept friend request."""

        await self.bot.aiohttp_session.post(
            url=links["friends"],
            data={
                "token": self.bot.token,
                "task": "accept",
                "theirid": self.user_id
            }
        )

    async def delete(self) -> None:
        """Decline friend request."""

        await self.bot.aiohttp_session.post(
            url=links["friends"],
            data={
                "token": self.bot.token,
                "task": "deleterequest",
                "theirid": self.user_id
            }
        )


class LegacyFriend:
    """
    Class for holding bonk1 legacy friends.

    :param bot: bot class that uses account.
    :param username: legacy friend's username.
    """

    def __init__(self, bot: "AccountBonkBot", username: str) -> None:
        self._bot: "AccountBonkBot" = bot
        self._username: str = username

    @property
    def bot(self) -> "AccountBonkBot":
        return self._bot

    @property
    def username(self) -> str:
        return self._username

    async def send_friend_request(self) -> None:
        """Sends friend request to user from legacy friend info."""

        await self.bot.aiohttp_session.post(
            url=links["friends"],
            data={
                "token": self.bot.token,
                "task": "send",
                "theirname": self.username
            }
        )


class FriendList:
    """
    Class for routing Friend and FriendRequest classes. Account's full friend list.

    :param bot: bot class that uses the account.
    :param raw_data: json data about account's friends and friend requests.
    """

    def __init__(self, bot: "AccountBonkBot", raw_data: dict) -> None:
        self._bot: "AccountBonkBot" = bot
        self.__raw_data: dict = raw_data

    @property
    def bot(self) -> "AccountBonkBot":
        return self._bot

    @cached_property
    def friends(self) -> List[Friend]:
        """Get friends from account friend list."""

        return [
            Friend(
                self.bot,
                friend["id"],
                friend["name"],
                friend["roomid"]
            ) for friend in self.__raw_data["friends"]
        ]

    @cached_property
    def friend_requests(self) -> List[FriendRequest]:
        """Get friend requests from account friend list."""

        return [
            FriendRequest(
                self.bot,
                request["id"],
                request["name"],
                request["date"]
            ) for request in self.__raw_data["requests"]
        ]
