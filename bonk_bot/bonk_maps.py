from functools import cached_property
from typing import TYPE_CHECKING

from .settings import links
from .parsers import decode_bonk_map

if TYPE_CHECKING:
    from .bot import AccountBonkBot


class OwnMap:
    """
    Class for holding bot's account own maps.

    :param bot: bot class that uses account.
    :param map_id: map database ID.
    :param map_data: encoded info about map.
    :param name: name of the map.
    :param creation_date: date of creation map.
    :param is_published: indicates whether map is published or not.
    :param votes_up: amount of players that liked map.
    :param votes_down: amount of players that disliked map.
    """

    def __init__(
        self,
        bot: "AccountBonkBot",
        map_id: int,
        map_data: str,
        name: str,
        creation_date: str,
        is_published: bool,
        votes_up: int,
        votes_down: int
    ) -> None:
        self._bot: "AccountBonkBot" = bot
        self.map_id: int = map_id
        self._encoded_data: str = map_data
        self.name: str = name
        self.creation_date: str = creation_date
        self.is_published: bool = is_published
        self.votes_up: int = votes_up
        self.votes_down: int = votes_down

    @property
    def bot(self) -> "AccountBonkBot":
        return self._bot

    @property
    def encoded_data(self) -> str:
        return self._encoded_data

    @cached_property
    def decoded_data(self) -> dict:
        """Decodes map data to dict."""

        return decode_bonk_map(self.encoded_data)

    async def delete(self) -> None:
        """Deletes bot's account own map."""

        await self.bot.aiohttp_session.post(
            url=links["map_delete"],
            data={
                "token": self.bot.token,
                "mapid": self.map_id,
            }
        )


class Bonk2Map:
    """
    Class for holding bonk2 maps.

    :param map_id: map database ID.
    :param map_data: encoded info about map.
    :param name: name of the map.
    :param author_name: username of map creator.
    :param published_date: date of publishing map.
    :param votes_up: amount of players that liked map.
    :param votes_down: amount of players that disliked map.
    """

    def __init__(
        self,
        map_id: int,
        map_data: str,
        name: str,
        author_name: str,
        published_date: str,
        votes_up: int,
        votes_down: int
    ):
        self.map_id: int = map_id
        self._encoded_data: str = map_data
        self.name: str = name
        self.author_name: str = author_name
        self.creation_date: str = published_date
        self.votes_up: int = votes_up
        self.votes_down: int = votes_down

    @property
    def encoded_data(self) -> str:
        return self._encoded_data

    @cached_property
    def decoded_data(self) -> dict:
        """Decodes map data to dict."""

        return decode_bonk_map(self.encoded_data)


class Bonk1Map:
    """
    Class for holding bonk1 maps.

    :param map_id: map database ID.
    :param map_data: encoded info about map.
    :param name: name of the map.
    :param author_name: username of map creator.
    :param creation_date: date of publishing map.
    :param modified_date: date of modification map.
    :param votes_up: amount of players that liked map.
    :param votes_down: amount of players that disliked map.
    """

    def __init__(
        self,
        map_id: int,
        map_data: str,
        name: str,
        author_name: str,
        creation_date: str,
        modified_date: str,
        votes_up: int,
        votes_down: int
    ):
        self.map_id: int = map_id
        self._encoded_data: str = map_data
        self.name: str = name
        self.author_name: str = author_name
        self.creation_date: str = creation_date
        self.modified_date: str = modified_date
        self.votes_up: int = votes_up
        self.votes_down: int = votes_down

    @property
    def encoded_data(self) -> str:
        return self._encoded_data
