class Modes:
    class Classic:
        def __init__(self) -> None:
            self.ga = "b"
            self.short_name = "b"

        def __str__(self) -> str:
            return "Classic"

    class Arrows:
        def __init__(self) -> None:
            self.ga = "b"
            self.short_name = "ar"

        def __str__(self) -> str:
            return "Arrows"

    class DeathArrows:
        def __init__(self) -> None:
            self.ga = "b"
            self.short_name = "ard"

        def __str__(self) -> str:
            self.ga = "b"
            return "Death Arrows"

    class Grapple:
        def __init__(self) -> None:
            self.ga = "b"
            self.short_name = "sp"

        def __str__(self) -> str:
            self.ga = "b"
            return "Grapple"

    class VTOL:
        def __init__(self) -> None:
            self.ga = "b"
            self.short_name = "v"

        def __str__(self) -> str:
            return "VTOL"

    class Football:
        def __init__(self) -> None:
            self.ga = "f"
            self.short_name = "f"

        def __str__(self) -> str:
            return "Football"


class Teams:
    class Spectator:
        def __init__(self) -> None:
            self.number = 0

        def __str__(self) -> str:
            return "Spectator"

    class FFA:
        def __init__(self) -> None:
            self.number = 1

        def __str__(self) -> str:
            return "FFA"

    class Red:
        def __init__(self) -> None:
            self.number = 2

        def __str__(self) -> str:
            return "Red"

    class Blue:
        def __init__(self) -> None:
            self.number = 3

        def __str__(self) -> str:
            return "Blue"

    class Green:
        def __init__(self) -> None:
            self.number = 4

        def __str__(self) -> str:
            return "Green"

    class Yellow:
        def __init__(self) -> None:
            self.number = 5

        def __str__(self) -> str:
            return "Yellow"
