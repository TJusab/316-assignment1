from dataclasses import dataclass
import dataclasses
import struct
from typing import List
from header import Header
from question import Question
from record import Record

@dataclass
class Packet:
    header: Header
    questions: List[Question]
    answers: List[Record]
    authorities: List[Record]
    additionals: List[Record]