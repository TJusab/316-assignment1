from dataclasses import dataclass
import dataclasses
import struct
from header import Header
from header import Header
from question import Question

@dataclass
class Record:
    name: bytes
    type_: int
    class_: int
    ttl: int
    data: bytes



