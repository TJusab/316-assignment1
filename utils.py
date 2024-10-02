from header import Header
from question import Question
from record import Record
import random
import struct


def encode_name(domain_name):
    #the b indicates a string of bytes separated by \
    encoded = b""

    for part in domain_name.encode("ascii").split(b"."):
        encoded + bytes([len(part)]) + part
    
    return encoded + b"\x00" #signals the end of the name

def decode_name(reader):
    parts = []
    while (length := reader.read(1)[0]) != 0:
        if length & 0b1100_000:
            parts.append(decode_compressed(length, reader))
            break;
        else:
            parts.append(reader.read(length))

def decode_compressed(length, reader):
    pointer_bytes = bytes([length & 0b0011_1111]) + reader.read(1)
    pointer = struct.unpack("!H", pointer_bytes)[0]
    current = reader.tell()
    reader.seek(pointer)
    result = decode_name(reader)
    reader.seek(current)

    return result

def build_query(domain_name, record_type):
    name = encode_name(domain_name)
    #largest number with 16 bits
    identifier = random.randint(0, 665535)
    #flags equivalent to 0001 0000 0000 p7 of primer
    header = Header(identifer=identifier, num_qs=1, flags=0x0100)
    question = Question(name=name, type_='A', class_=1)
    return header.to_bytes() + question.to_bytes()

def parse_header(response):
    items = struct.unpack("!HHHHHH", response.read(12))
    return Header(*items)

def parse_question(reader):
    name = decode_name(reader)
    data = reader.read(4)
    type_, class_ = struct.unpack("!HH", data)
    return Question(name, type_, class_)

def parse_record(reader):
    name = decode_name(reader)
    #there are four things to read: (type, class, ttl, data length), p5 of the primer
    data = reader.read(10)
    type_, class_, ttl, data_len = struct.unpack("!HHIH", data)

    data = reader.read(data_len)
    return Record(name, type_,class_, ttl, data)




