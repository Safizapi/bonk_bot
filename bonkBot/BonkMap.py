from bonkBot.Settings import session, links


class BonkMap:
    def __init__(
        self,
        token: str,
        map_id: int,
        level_data: str,
        author: str,
        name: str,
        creation_date: str,
        is_published: bool,
        votes_up: int,
        votes_down: int
    ) -> None:
        self.map_id: int = map_id
        self.level_data: str = level_data
        self.name: str = name
        self.author: str = author
        self.creation_date: str = creation_date
        self.is_published: bool = is_published
        self.votes_up: int = votes_up
        self.votes_down: int = votes_down
        self.__token: str = token

    def delete(self) -> None:
        response = session.post(
            links["map_delete"],
            {
                "token": self.__token,
                "mapid": self.map_id,
            }
        ).json()

        print(response)
