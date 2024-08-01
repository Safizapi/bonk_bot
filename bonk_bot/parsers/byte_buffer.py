import struct


class ByteBuffer:
    def __init__(self, data: bytes) -> None:
        self.data: bytes = data
        self.position = 0

    # Write methods
    def write_boolean(self, value: bool) -> None:
        self.data += value.to_bytes()

    def write_byte(self, value: bytes) -> None:
        self.data += value

    def write_short(self, value: int) -> None:
        self.data += struct.pack(">h", value)

    def write_int(self, value: int) -> None:
        self.data += struct.pack(">i", value)

    def write_uint(self, value: int) -> None:
        self.data += struct.pack(">I", value)

    def write_float(self, value: float) -> None:
        self.data += struct.pack(">f", value)

    def write_double(self, value: float) -> None:
        self.data += struct.pack(">d", value)

    def write_utf(self, value: str) -> None:
        self.data += struct.pack(">h", len(value))
        self.data += value.encode()

    # Read methods
    def read_boolean(self) -> bool:
        return self.read_byte() != 0

    def read_byte(self) -> bytes:
        value = struct.unpack("B", self.data[self.position:self.position + 1])[0]
        self.position += 1
        return value

    def read_short(self) -> int:
        value = struct.unpack(">h", self.data[self.position:self.position + 2])[0]
        self.position += 2
        return value

    def read_int(self) -> int:
        value = struct.unpack(">i", self.data[self.position:self.position + 4])[0]
        self.position += 4
        return value

    def read_uint(self) -> int:
        value = struct.unpack(">I", self.data[self.position:self.position + 4])[0]
        self.position += 4
        return value

    def read_float(self) -> float:
        value = struct.unpack(">f", self.data[self.position:self.position + 4])[0]
        self.position += 4
        return value

    def read_padding(self) -> None:
        self.position += 7

    def read_double(self) -> float:
        value = struct.unpack(">d", self.data[self.position:self.position + 8])[0]
        self.position += 8
        return value

    def read_utf(self) -> str:
        length = self.read_short()
        value = self.data[self.position:self.position + length].decode("utf-8")
        self.position += length
        return value
