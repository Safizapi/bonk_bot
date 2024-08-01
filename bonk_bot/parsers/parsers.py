import base64
import datetime
import json
from typing import Union, List
from urllib.parse import unquote

from lzstring import LZString

from bonk_bot.parsers.byte_buffer import ByteBuffer
from bonk_bot.types import Modes, AnyMode, GameInputs, AnyGameInput, Teams, AnyTeam
from bonk_bot.avatar import Avatar


def decode_avatar(avatar: str) -> Avatar:
    """
    Used to decode bonk avatars.

    :param avatar: base64 encoded avatar data.
    """

    def decode_layer(buffer: ByteBuffer) -> Union[dict, None]:
        layer_data = {}

        if buffer.read_byte() == 10:
            if buffer.read_byte() == 7:
                for _ in range(3):
                    buffer.read_byte()

            buffer.read_short()

            layer_data["id"] = buffer.read_short()
            layer_data["scale"] = buffer.read_float()
            layer_data["angle"] = buffer.read_float()
            layer_data["x"] = buffer.read_float()
            layer_data["y"] = buffer.read_float()
            layer_data["flipX"] = buffer.read_boolean()
            layer_data["flipY"] = buffer.read_boolean()
            layer_data["color"] = buffer.read_int()

            return layer_data

        return None

    if avatar == "":
        return Avatar({"layers": [], "bc": 4492031})

    byte_buffer = ByteBuffer(base64.b64decode(unquote(avatar)))
    avatar_data = {"layers": [], "bc": 0}

    byte_buffer.read_padding()

    shapes_count = (int(byte_buffer.read_byte()) - 1) // 2
    wtf_chaz = byte_buffer.read_byte()

    while wtf_chaz != 1:
        if wtf_chaz == 3:
            byte_buffer.read_byte()
        elif wtf_chaz == 5:
            byte_buffer.read_byte()
            byte_buffer.read_byte()

        wtf_chaz = byte_buffer.read_byte()

    for _ in range(shapes_count):
        layer = decode_layer(byte_buffer)

        if layer:
            avatar_data["layers"].append(layer)

    avatar_data["bc"] = byte_buffer.read_int()

    return Avatar(avatar_data)


def decode_bonk_map_metadata(encoded_map: str) -> dict:
    """
    Used to decode bonk maps metadata.

    :param encoded_map: base64 encoded map data.
    """

    map_data = {
        "m": {
            "a": "nob_author",
            "n": "nob_name",
            "dbv": 2,
            "dbid": -1,
            "authid": -1,
            "date": "",
            "rxid": 0,
            "rxn": "",
            "rxa": "",
            "rxdb": 1,
            "cr": [],
            "pub": False,
            "mo": ""
        }
    }
    byte_buffer = ByteBuffer(base64.b64decode(LZString.decompressFromEncodedURIComponent(encoded_map)))

    map_version = byte_buffer.read_short()

    if map_version > 61:
        raise ValueError("Future map version")

    byte_buffer.read_boolean()
    byte_buffer.read_boolean()

    if map_version >= 3:
        byte_buffer.read_short()

    if 4 <= map_version <= 12:
        byte_buffer.read_short()
    elif map_version >= 13:
        byte_buffer.read_float()

    if map_version >= 9:
        byte_buffer.read_boolean()

    map_data["m"]["rxn"] = byte_buffer.read_utf()
    map_data["m"]["rxa"] = byte_buffer.read_utf()
    map_data["m"]["rxid"] = byte_buffer.read_uint()
    map_data["m"]["rxdb"] = byte_buffer.read_short()
    map_data["m"]["n"] = byte_buffer.read_utf()
    map_data["m"]["a"] = byte_buffer.read_utf()

    if map_version >= 10:
        map_data["m"]["vu"] = byte_buffer.read_uint()
        map_data["m"]["vd"] = byte_buffer.read_uint()

    if map_version >= 4:
        cr_len = byte_buffer.read_short()
        map_data["m"]["cr"] = [byte_buffer.read_utf() for _ in range(cr_len)]

    if map_version >= 5:
        map_data["m"]["mo"] = byte_buffer.read_utf()
        map_data["m"]["dbid"] = byte_buffer.read_int()

    if map_version >= 7:
        map_data["m"]["pub"] = byte_buffer.read_boolean()

    if map_version >= 8:
        map_data["m"]["dbv"] = byte_buffer.read_int()

    return map_data


def decode_bonk_map(encoded_map: str) -> dict:
    """
    Used to decode bonk maps.

    :param encoded_map: base64 encoded map data.
    """

    map_data = {
        "v": 1,
        "s": {
            "re": False,
            "nc": False,
            "pq": 1,
            "gd": 25.0,
            "fl": False
        },
        "physics": {
            "shapes": [],
            "fixtures": [],
            "bodies": [],
            "bro": [],
            "joints": [],
            "ppm": 12
        },
        "spawns": [],
        "capZones": [],
        "m": {
            "a": "nob_author",
            "n": "nob_name",
            "dbv": 2,
            "dbid": -1,
            "authid": -1,
            "date": "",
            "rxid": 0,
            "rxn": "",
            "rxa": "",
            "rxdb": 1,
            "cr": [],
            "pub": False,
            "mo": ""
        }
    }
    byte_buffer = ByteBuffer(base64.b64decode(LZString.decompressFromEncodedURIComponent(encoded_map)))

    physics = map_data["physics"]
    map_data["v"] = byte_buffer.read_short()

    if map_data["v"] > 61:
        raise ValueError("Future map version")

    map_data["s"]["re"] = byte_buffer.read_boolean()
    map_data["s"]["nc"] = byte_buffer.read_boolean()

    if map_data["v"] >= 3:
        map_data["s"]["pq"] = byte_buffer.read_short()

    if 4 <= map_data["v"] <= 12:
        map_data["s"]["gd"] = byte_buffer.read_short()
    elif map_data["v"] >= 13:
        map_data["s"]["gd"] = byte_buffer.read_float()

    if map_data["v"] >= 9:
        map_data["s"]["fl"] = byte_buffer.read_boolean()

    map_data["m"]["rxn"] = byte_buffer.read_utf()
    map_data["m"]["rxa"] = byte_buffer.read_utf()
    map_data["m"]["rxid"] = byte_buffer.read_uint()
    map_data["m"]["rxdb"] = byte_buffer.read_short()
    map_data["m"]["n"] = byte_buffer.read_utf()
    map_data["m"]["a"] = byte_buffer.read_utf()

    if map_data["v"] >= 10:
        map_data["m"]["vu"] = byte_buffer.read_uint()
        map_data["m"]["vd"] = byte_buffer.read_uint()

    if map_data["v"] >= 4:
        cr_len = byte_buffer.read_short()
        map_data["m"]["cr"] = [byte_buffer.read_utf() for _ in range(cr_len)]

    if map_data["v"] >= 5:
        map_data["m"]["mo"] = byte_buffer.read_utf()
        map_data["m"]["dbid"] = byte_buffer.read_int()

    if map_data["v"] >= 7:
        map_data["m"]["pub"] = byte_buffer.read_boolean()

    if map_data["v"] >= 8:
        map_data["m"]["dbv"] = byte_buffer.read_int()

    physics["ppm"] = byte_buffer.read_short()
    bro_len = byte_buffer.read_short()
    physics["bro"] = [byte_buffer.read_short() for _ in range(bro_len)]

    shape_len = byte_buffer.read_short()

    for _ in range(shape_len):
        shape_type = byte_buffer.read_short()

        if shape_type == 1:
            physics["shapes"].append(
                {
                    "type": "bx",
                    "w": byte_buffer.read_double(),
                    "h": byte_buffer.read_double(),
                    "c": [byte_buffer.read_double(), byte_buffer.read_double()],
                    "a": byte_buffer.read_double(),
                    "sk": byte_buffer.read_boolean()
                }
            )
        elif shape_type == 2:
            physics["shapes"].append(
                {
                    "type": "ci",
                    "r": byte_buffer.read_double(),
                    "c": [byte_buffer.read_double(), byte_buffer.read_double()],
                    "sk": byte_buffer.read_boolean()
                }
            )
        elif shape_type == 3:
            shape = {
                "type": "po",
                "v": [],
                "s": byte_buffer.read_double(),
                "a": byte_buffer.read_double(),
                "c": [byte_buffer.read_double(), byte_buffer.read_double()],
            }

            vertex_count = byte_buffer.read_short()
            shape["v"] = [[byte_buffer.read_double(), byte_buffer.read_double()] for _ in range(vertex_count)]

            physics["shapes"].append(shape)

    fix_count = byte_buffer.read_short()

    for _ in range(fix_count):
        fixture = {
            "sh": byte_buffer.read_short(),
            "n": byte_buffer.read_utf(),
            "fr": byte_buffer.read_double(),
            "fp": None,
            "re": 0.8,
            "de": 0.3,
            "f": 0x4F7CAC,
            "d": False,
            "np": False,
            "ng": False
        }

        if fixture["fr"] == 1.7976931348623157e+308:
            fixture["fr"] = None

        fp = byte_buffer.read_short()

        if fp == 0:
            fixture["fp"] = None
        elif fp == 1:
            fixture["fp"] = False
        elif fp == 2:
            fixture["fp"] = True

        fixture["re"] = byte_buffer.read_double()
        fixture["de"] = byte_buffer.read_double()

        if fixture["re"] == 1.7976931348623157e+308:
            fixture["re"] = None

        if fixture["de"] == 1.7976931348623157e+308:
            fixture["de"] = None

        fixture["f"] = byte_buffer.read_uint()
        fixture["d"] = byte_buffer.read_boolean()
        fixture["np"] = byte_buffer.read_boolean()

        if map_data["v"] >= 11:
            fixture["ng"] = byte_buffer.read_boolean()

        if map_data["v"] >= 12:
            fixture["ig"] = byte_buffer.read_boolean()

        physics["fixtures"].append(fixture)

    body_len = byte_buffer.read_short()

    for _ in range(body_len):
        body = {
            "p": [0.0, 0.0],
            "a": 0,
            "lv": [0, 0],
            "av": 0,
            "cf": {
                "x": 0.0,
                "y": 0.0,
                "w": True,
                "ct": 0.0
            },
            "fx": [],
            "fz": {
                "on": False,
                "x": 0.0,
                "y": 0.0,
                "d": True,
                "p": True,
                "a": True,
                "t": 0,
                "cf": 0.0
            },
            "s": {
                "type": "s",
                "n": "Unnamed",
                "fric": 0.3,
                "fricp": False,
                "re": 0.8,
                "de": 0.3,
                "ld": 0,
                "ad": 0,
                "fr": False,
                "bu": False,
                "f_c": 1,
                "f_p": True,
                "f_1": True,
                "f_2": True,
                "f_3": True,
                "f_4": True
            }
        }

        body["s"]["type"] = byte_buffer.read_utf()
        body["s"]["n"] = byte_buffer.read_utf()
        body["p"] = [byte_buffer.read_double(), byte_buffer.read_double()]
        body["a"] = byte_buffer.read_double()
        body["s"]["fric"] = byte_buffer.read_double()
        body["s"]["fricp"] = byte_buffer.read_boolean()
        body["s"]["re"] = byte_buffer.read_double()
        body["s"]["de"] = byte_buffer.read_double()
        body["lv"] = [byte_buffer.read_double(), byte_buffer.read_double()]
        body["av"] = byte_buffer.read_double()
        body["s"]["ld"] = byte_buffer.read_double()
        body["s"]["ad"] = byte_buffer.read_double()
        body["s"]["fr"] = byte_buffer.read_boolean()
        body["s"]["bu"] = byte_buffer.read_boolean()
        body["cf"]["x"] = byte_buffer.read_double()
        body["cf"]["y"] = byte_buffer.read_double()
        body["cf"]["ct"] = byte_buffer.read_double()
        body["cf"]["w"] = byte_buffer.read_boolean()
        body["s"]["f_c"] = byte_buffer.read_short()
        body["s"]["f_1"] = byte_buffer.read_boolean()
        body["s"]["f_2"] = byte_buffer.read_boolean()
        body["s"]["f_3"] = byte_buffer.read_boolean()
        body["s"]["f_4"] = byte_buffer.read_boolean()

        if map_data["v"] >= 2:
            body["s"]["f_p"] = byte_buffer.read_boolean()

        if map_data["v"] >= 14:
            body["fz"]["on"] = byte_buffer.read_boolean()

            if body["fz"]["on"]:
                body["fz"]["x"] = byte_buffer.read_double()
                body["fz"]["y"] = byte_buffer.read_double()
                body["fz"]["d"] = byte_buffer.read_boolean()
                body["fz"]["p"] = byte_buffer.read_boolean()
                body["fz"]["a"] = byte_buffer.read_boolean()

                if map_data["v"] >= 15:
                    body["fz"]["t"] = byte_buffer.read_short()
                    body["fz"]["cf"] = byte_buffer.read_double()

        fx_len = byte_buffer.read_short()

        for _ in range(fx_len):
            body["fx"].append(byte_buffer.read_short())

        physics["bodies"].append(body)

    spawn_len = byte_buffer.read_short()

    for _ in range(spawn_len):
        map_data["spawns"].append(
            {
                "x": byte_buffer.read_double(),
                "y": byte_buffer.read_double(),
                "xv": byte_buffer.read_double(),
                "yv": byte_buffer.read_double(),
                "priority": byte_buffer.read_short(),
                "r": byte_buffer.read_boolean(),
                "f": byte_buffer.read_boolean(),
                "b": byte_buffer.read_boolean(),
                "gr": byte_buffer.read_boolean(),
                "ye": byte_buffer.read_boolean(),
                "n": byte_buffer.read_utf()
            }
        )

    cap_zone_len = byte_buffer.read_short()

    for _ in range(cap_zone_len):
        cap_zone = {
            "n": byte_buffer.read_utf(),
            "l": byte_buffer.read_double(),
            "i": byte_buffer.read_short()
        }

        if map_data["v"] >= 6:
            cap_zone["ty"] = byte_buffer.read_short()

        map_data["capZones"].append(cap_zone)

    joint_len = byte_buffer.read_short()

    for _ in range(joint_len):
        joint_type = byte_buffer.read_short()
        joint = {"d": {}}

        if joint_type == 1:
            joint["type"] = "rv"
            joint["d"]["la"] = byte_buffer.read_double()
            joint["d"]["ua"] = byte_buffer.read_double()
            joint["d"]["mmt"] = byte_buffer.read_double()
            joint["d"]["ms"] = byte_buffer.read_double()
            joint["d"]["el"] = byte_buffer.read_boolean()
            joint["d"]["em"] = byte_buffer.read_boolean()
            joint["aa"] = [byte_buffer.read_double(), byte_buffer.read_double()]
        elif joint_type == 2:
            joint["type"] = "d"
            joint["d"]["fh"] = byte_buffer.read_double()
            joint["d"]["dr"] = byte_buffer.read_double()
            joint["aa"] = [byte_buffer.read_double(), byte_buffer.read_double()]
            joint["ab"] = [byte_buffer.read_double(), byte_buffer.read_double()]
        elif joint_type == 3:
            joint["type"] = "lpj"
            joint["pax"] = byte_buffer.read_double()
            joint["pay"] = byte_buffer.read_double()
            joint["pa"] = byte_buffer.read_double()
            joint["pf"] = byte_buffer.read_double()
            joint["pl"] = byte_buffer.read_double()
            joint["pu"] = byte_buffer.read_double()
            joint["plen"] = byte_buffer.read_double()
            joint["pms"] = byte_buffer.read_double()
        elif joint_type == 4:
            joint["type"] = "lsj"
            joint["sax"] = byte_buffer.read_double()
            joint["say"] = byte_buffer.read_double()
            joint["sf"] = byte_buffer.read_double()
            joint["slen"] = byte_buffer.read_double()
        elif joint_type == 5:
            joint["type"] = "g"
            joint["n"] = byte_buffer.read_utf()
            joint["ja"] = byte_buffer.read_short()
            joint["jb"] = byte_buffer.read_short()
            joint["r"] = byte_buffer.read_double()

        if joint_type != 5:
            joint["ba"] = byte_buffer.read_short()
            joint["bb"] = byte_buffer.read_short()
            joint["d"]["cc"] = byte_buffer.read_boolean()
            joint["d"]["bf"] = byte_buffer.read_double()
            joint["d"]["dl"] = byte_buffer.read_boolean()

        physics["joints"].append(joint)

    return map_data


# Credits to https://shaunx777.github.io/dbid2date/
def db_id_to_date(db_id: int) -> Union[datetime.datetime, str]:
    """
    Returns approximate account date creating from account database ID.

    :param db_id: account database ID.
    """

    with open("bot/dbids.json") as file:
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


def team_from_number(number: int) -> AnyTeam:
    """
    Returns mode class from its number according to bonk.io api.

    :param number: the number of team in bonk.io api.
    """

    teams = {
        0: Teams.Spectator,
        1: Teams.FFA,
        2: Teams.Red,
        3: Teams.Blue,
        4: Teams.Green,
        5: Teams.Yellow
    }

    return teams[number]


def mode_from_short_name(short_name: str) -> AnyMode:
    """
    Returns mode class from its short name according to bonk.io api.

    :param short_name: mode short name in bonk.io api.
    """

    modes = {
        "b": Modes.Classic,
        "bs": Modes.Simple,
        "ar": Modes.Arrows,
        "ard": Modes.DeathArrows,
        "sp": Modes.Grapple,
        "v": Modes.VTOL,
        "f": Modes.Football
    }

    return modes[short_name]


def move_direction_from_number(number: int) -> List[AnyGameInput]:
    """
    Parses the move bits to get input keys pressed for move.

    :param number: move bits.
    """

    heavy = 15 < number < 32
    special = 31 < number < 46
    heavy_and_special = number > 45
    movement_clear_number = number
    inputs = []

    if heavy:
        movement_clear_number -= 16
        inputs.append(GameInputs.Heavy)
    elif special:
        movement_clear_number -= 32
        inputs.append(GameInputs.Special)
    elif heavy_and_special:
        movement_clear_number -= 48
        inputs.append(GameInputs.Heavy)
        inputs.append(GameInputs.Special)

    move_directions = {
        0: [GameInputs.NoneInput],
        1: [GameInputs.Left],
        2: [GameInputs.Right],
        3: [GameInputs.Left, GameInputs.Right],
        4: [GameInputs.Up],
        5: [GameInputs.Up, GameInputs.Left],
        6: [GameInputs.Up, GameInputs.Right],
        7: [GameInputs.Up, GameInputs.Left, GameInputs.Right],
        8: [GameInputs.Down],
        9: [GameInputs.Down, GameInputs.Left],
        10: [GameInputs.Down, GameInputs.Right],
        11: [GameInputs.Down, GameInputs.Left, GameInputs.Right],
        12: [GameInputs.Up, GameInputs.Down],
        13: [GameInputs.Up, GameInputs.Down, GameInputs.Left],
        14: [GameInputs.Up, GameInputs.Down, GameInputs.Right],
        15: [GameInputs.Up, GameInputs.Down, GameInputs.Left, GameInputs.Right]
    }

    inputs.extend(move_directions[movement_clear_number])

    return inputs
