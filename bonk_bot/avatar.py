class Avatar:
    """
    Class for holding Avatar decoded data.

    :param json_data: decoded avatar data.
    """

    def __init__(self, json_data: dict) -> None:
        self.json_data: dict = json_data
