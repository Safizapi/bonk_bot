import datetime
from typing import List

from .Settings import session, links
from .Parsers import db_id_to_date
from .Game import Game


class Friend:
    def __init__(self, bot, token: str, user_id: int, username: str, room_id: int | None) -> None:
        self.bot = bot
        self.user_id: int = user_id
        self.username: str = username
        self.room_id: int | None = room_id
        self.__token: str = token

    def unfriend(self) -> None:
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
        return db_id_to_date(self.user_id)

    async def join_game(self) -> Game:
        room = [room for room in self.bot.get_rooms() if room.room_id == self.room_id][0]
        game = room.join()
        await game.connect()

        return game


class FriendRequest:
    def __init__(self, token: str, user_id: int, username: str, date: str) -> None:
        self.user_id: int = user_id
        self.username: str = username
        self.date: str = date
        self.__token: str = token

    def accept(self) -> None:
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
    def __init__(self, bot, token: str, raw_data: dict) -> None:
        self.bot = bot
        self.__token: str = token
        self.__raw_data: dict = raw_data

    def get_friends(self) -> List[Friend]:
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
        return [
            FriendRequest(
                self.__token,
                request["id"],
                request["name"],
                request["date"]
            ) for request in self.__raw_data["requests"]
        ]
