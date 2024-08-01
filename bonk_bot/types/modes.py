from typing import Union, Type


class Modes:
    """Class for holding modes types."""

    class Classic:
        ga = "b"
        short_name = "b"

    class Simple:
        ga = "b"
        short_name = "bs"

    class Arrows:
        ga = "b"
        short_name = "ar"

    class DeathArrows:
        ga = "b"
        short_name = "ard"

    class Grapple:
        ga = "b"
        short_name = "sp"

    class VTOL:
        ga = "b"
        short_name = "v"

    class Football:
        ga = "f"
        short_name = "f"


AnyMode = Union[
    Type[Modes.Classic], Type[Modes.Arrows], Type[Modes.DeathArrows], Type[Modes.Grapple], Type[Modes.VTOL],
    Type[Modes.Football], Type[Modes.Simple]
]

all_modes_list = [Modes.Classic, Modes.Arrows, Modes.DeathArrows, Modes.Grapple, Modes.VTOL, Modes.Simple]
