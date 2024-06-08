from bonkBot.Settings import session, links


class OwnMap:
    """
    Class for holding bot's account own maps.

    :param token: account session token.
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
        token: str,
        map_id: int,
        map_data: str,
        name: str,
        creation_date: str,
        is_published: bool,
        votes_up: int,
        votes_down: int
    ) -> None:
        self.map_id: int = map_id
        self.map_data: str = map_data
        self.name: str = name
        self.creation_date: str = creation_date
        self.is_published: bool = is_published
        self.votes_up: int = votes_up
        self.votes_down: int = votes_down
        self.__token: str = token

    def delete(self) -> None:
        """Deletes bot's account own map."""

        response = session.post(
            links["map_delete"],
            {
                "token": self.__token,
                "mapid": self.map_id,
            }
        ).json()

        print(response)


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
        self.map_data: str = map_data
        self.name: str = name
        self.author_name: str = author_name
        self.published_date: str = published_date
        self.votes_up: int = votes_up
        self.votes_down: int = votes_down


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
        self.map_data: str = map_data
        self.name: str = name
        self.author_name: str = author_name
        self.creation_date: str = creation_date
        self.modified_date: str = modified_date
        self.votes_up: int = votes_up
        self.votes_down: int = votes_down
