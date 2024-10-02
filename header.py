from dataclasses import dataclass
import dataclasses
import struct

@dataclass
class Header:
    identifer: int
    flags: int
    num_qs: int = 0
    nums_as: int = 0
    num_auths: int = 0
    num_adds: int = 0

    def to_bytes(self):
        fields = dataclasses.astyple(self)
        return struct.pack("!HHHHHH", *fields)
