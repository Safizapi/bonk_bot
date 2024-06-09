import datetime
import json
from typing import Union

from .Types import Teams, Modes


# Credits to https://shaunx777.github.io/dbid2date/
def db_id_to_date(db_id: int) -> Union[datetime.datetime, str]:
    """
    Returns approximate account date creating from account database ID.

    :param db_id: account database ID.
    """

    with open("bonkBot/dbids.json") as file:
        db_ids = json.load(file)
        index = 0

    while index < len(db_ids) and db_ids[index]["number"] < db_id:
        index += 1

    if index == 0:
        return f"Before {db_ids[0]['date']}"
    elif index == len(db_ids):
        return f"After {db_ids[-1]['date']}"

    first_number = db_ids[index - 1]["number"]
    second_number = db_ids[index]["number"]

    first_date = db_ids[index - 1]["date"]
    second_date = db_ids[index]["date"]
    first_timestamp = datetime.datetime.strptime(first_date, "%Y-%m-%d").timestamp()
    second_timestamp = datetime.datetime.strptime(second_date, "%Y-%m-%d").timestamp()

    diff = (db_id - first_number) / (second_number - first_number)
    time = first_timestamp + diff * (second_timestamp - first_timestamp)

    return datetime.datetime.fromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S")


def team_from_number(
    number: int
) -> Union[Teams.Spectator, Teams.FFA, Teams.Red, Teams.Blue, Teams.Green, Teams.Yellow]:
    """
    Returns mode class from its number according to bonk.io api.

    :param number: the number of team in bonk.io api.
    """

    teams = {
        0: Teams.Spectator(),
        1: Teams.FFA(),
        2: Teams.Red(),
        3: Teams.Blue(),
        4: Teams.Green(),
        5: Teams.Yellow(),
    }

    return teams[number]


def mode_from_short_name(
    short_name: str
) -> Union[Modes.Classic, Modes.Arrows, Modes.DeathArrows, Modes.Grapple, Modes.VTOL, Modes.Football]:
    """
    Returns mode class from its short name according to bonk.io api.

    :param short_name: mode short name in bonk.io api.
    """

    modes = {
        "b": Modes.Classic(),
        "ar": Modes.Arrows(),
        "ard": Modes.DeathArrows(),
        "sp": Modes.Grapple(),
        "v": Modes.VTOL(),
        "f": Modes.Football(),
    }

    return modes[short_name]
