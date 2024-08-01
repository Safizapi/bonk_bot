from typing import Union, Type


class GameInputs:
    """Class for holding basic movement directions."""

    class NoneInput:
        bits = 0

    class Left:
        bits = 1

    class Right:
        bits = 2

    class Up:
        bits = 4

    class Down:
        bits = 8

    class Heavy:
        bits = 16

    class Special:
        bits = 32


AnyGameInput = Union[
    Type[GameInputs.NoneInput], Type[GameInputs.Left], Type[GameInputs.Right], Type[GameInputs.Up],
    Type[GameInputs.Down], Type[GameInputs.Heavy], Type[GameInputs.Special]
]

all_game_inputs = [
    GameInputs.Left, GameInputs.Right, GameInputs.Up, GameInputs.Down, GameInputs.Heavy,
    GameInputs.Special
]
