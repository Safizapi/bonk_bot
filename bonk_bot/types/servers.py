from typing import Union, Type


class Servers:
    """Class for holding server types."""

    class Warsaw:
        api_name = "b2warsaw1"
        latitude = 52.2370
        longitude = 21.0175
        country = "PL"

    class Paris:
        api_name = "b2paris1"
        latitude = 48.8647
        longitude = 2.3490
        country = "FR"

    class Stockholm:
        api_name = "b2stockholm1"
        latitude = 59.3346
        longitude = 18.0632
        country = "SE"

    class Frankfurt:
        api_name = "b2frankfurt1"
        latitude = 50.1109
        longitude = 8.6821
        country = "GE"

    class Amsterdam:
        api_name = "b2amsterdam1"
        latitude = 52.3779
        longitude = 4.897
        country = "NL"

    class London:
        api_name = "b2london1"
        latitude = 51.5098
        longitude = -0.1180
        country = "UK"

    class Seoul:
        api_name = "b2seoul1"
        latitude = 37.5326
        longitude = 127.0246
        country = "KR"

    class Seattle:
        api_name = "b2seattle1"
        latitude = 47.6080
        longitude = -122.3352
        country = "US"

    class SanFrancisco:
        api_name = "b2sanfrancisco1"
        latitude = 37.7740
        longitude = -122.4312
        country = "US"

    class Mississippi:
        api_name = "b2river1"
        latitude = 35.5147
        longitude = -89.9125
        country = "US"

    class Dallas:
        api_name = "b2dallas1"
        latitude = 32.7792
        longitude = -96.8089
        country = "US"

    class NewYork:
        api_name = "b2ny1"
        latitude = 40.7306
        longitude = -73.9352
        country = "US"

    class Atlanta:
        api_name = "b2atlanta1"
        latitude = 33.7537
        longitude = -84.3863
        country = "US"

    class Sydney:
        api_name = "b2sydney1"
        latitude = -33.8651
        longitude = 151.2099
        country = "AU"

    class Brazil:
        api_name = "b2brazil1"
        latitude = -22.9083
        longitude = -43.1963
        country = "BR"


AnyServer = Union[
    Type[Servers.Warsaw], Type[Servers.Stockholm], Type[Servers.Frankfurt], Type[Servers.London], Type[Servers.Seoul],
    Type[Servers.Seattle], Type[Servers.SanFrancisco], Type[Servers.Mississippi], Type[Servers.Dallas],
    Type[Servers.NewYork], Type[Servers.Atlanta], Type[Servers.Sydney], Type[Servers.Brazil]
]

all_servers_list = [
    Servers.Warsaw, Servers.Stockholm, Servers.Frankfurt, Servers.London, Servers.Seoul, Servers.Seattle,
    Servers.SanFrancisco, Servers.Mississippi, Servers.Dallas, Servers.NewYork, Servers.Atlanta, Servers.Sydney,
    Servers.Brazil
]
