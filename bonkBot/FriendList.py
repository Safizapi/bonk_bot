import datetime
from typing import List

from .Settings import session, links
from .Parsers import db_id_to_date
from .Game import Game


class Friend:
    """
    Class for holding account's friends.

    :param bot: bot class that uses the account.
    :param token: bonk.io account session token.
    :param user_id: account database ID.
    :param username: account username.
    :param room_id: the room ID where friend is playing.
    """

    def __init__(self, bot, token: str, user_id: int, username: str, room_id: int | None) -> None:
        self.bot = bot
        self.user_id: int = user_id
        self.username: str = username
        self.room_id: int | None = room_id
        self.__token: str = token

    def unfriend(self) -> None:
        """Remove friend from account friend list."""

        response = session.post(
            links["friends"],
            {
                "token": self.__token,
                "task": "unfriend",
                "theirid": self.user_id
            }
        ).json()

        print(response)

    def get_creation_data(self) -> datetime.datetime | str:
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

        room = [room for room in self.bot.get_rooms() if room.room_id == self.room_id][0]
        game = room.join()
        await game.connect()

        return game


class FriendRequest:
    """
    Class for holding account's friend requests.

    :param token: bonk.io account session token.
    :param user_id: account database ID.
    :param username: account username.
    :param date: the date of sending friend request.
    """

    def __init__(self, token: str, user_id: int, username: str, date: str) -> None:
        self.user_id: int = user_id
        self.username: str = username
        self.date: str = date
        self.__token: str = token

    def accept(self) -> None:
        """Accept friend request."""

        response = session.post(
            links["friends"],
            {
                "token": self.__token,
                "task": "accept",
                "theirid": self.user_id
            }
        ).json()

        print(response)

    def delete(self) -> None:
        """Decline friend request."""

        response = session.post(
            links["friends"],
            {
                "token": self.__token,
                "task": "deleterequest",
                "theirid": self.user_id
            }
        ).json()

        print(response)


class FriendList:
    """
    Class for routing Friend and FriendRequest classes. Account's full friend list.

    :param bot: bot class that uses the account.
    :param token: bonk.io account session token.
    :param raw_data: json data about account's friends and friend requests.
    """

    def __init__(self, bot, token: str, raw_data: dict) -> None:
        self.bot = bot
        self.__token: str = token
        self.__raw_data: dict = raw_data

    def get_friends(self) -> List[Friend]:
        """Get friends from account friend list."""

        return [
            Friend(
                self.bot,
                self.__token,
                friend["id"],
                friend["name"],
                friend["roomid"]
            ) for friend in self.__raw_data["friends"]
        ]

    def get_friend_requests(self) -> List[FriendRequest]:
        """Get friend requests from account friend list."""

        return [
            FriendRequest(
                self.__token,
                request["id"],
                request["name"],
                request["date"]
            ) for request in self.__raw_data["requests"]
        ]
