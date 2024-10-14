from dataclasses import dataclass

@dataclass
class Record:
    name: bytes
    type_: int
    class_: int
    ttl: int
    data: bytes
    alias: str
    mx_preference: int = None  



