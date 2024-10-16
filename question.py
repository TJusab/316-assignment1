from dataclasses import dataclass
import struct

@dataclass
class Question:
    name: bytes
    type_: int
    class_: int

    #H means two-byte integer so this is formating the values as 2 2-byte integers (16 bits)
    def to_bytes(self):
        return self.name + struct.pack("!HH", self.type_, self.class_)
    
