from typing import Union, Type


class Teams:
    """Class for holding team types."""

    class Spectator:
        number = 0

    class FFA:
        number = 1

    class Red:
        number = 2

    class Blue:
        number = 3

    class Green:
        number = 4

    class Yellow:
        number = 5


AnyTeam = Union[
    Type[Teams.Spectator], Type[Teams.FFA], Type[Teams.Red], Type[Teams.Blue], Type[Teams.Green], Type[Teams.Yellow]
]

all_teams_list = [Teams.Spectator, Teams.FFA, Teams.Red, Teams.Blue, Teams.Green, Teams.Yellow]
