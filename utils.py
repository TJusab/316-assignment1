from header import Header
from question import Question
from record import Record
from packet import Packet
import random
import struct
from io import BytesIO


def encode_name(domain_name):
    encoded = b""
    # Split the domain name by '.' and encode each part
    for part in domain_name.encode("ascii").split(b"."):
        encoded += bytes([len(part)]) + part
    # Append a null byte to mark the end of the domain name
    return encoded + b"\x00"


def decode_name(reader):
    parts = []
    while (length := reader.read(1)[0]) != 0:
        if length & 0b1100_0000:  # Check for compression offset
            parts.append(decode_compressed(length, reader))
            break
        else:
            parts.append(reader.read(length).decode("ascii"))

    return ".".join(parts)

def decode_compressed(length, reader):
    pointer_bytes = bytes([length & 0b0011_1111]) + reader.read(1)
    pointer = struct.unpack("!H", pointer_bytes)[0]
    current = reader.tell()  # Save the current position
    reader.seek(pointer)  # Jump to the compressed name location
    result = decode_name(reader)  # Decode the name at the pointer
    reader.seek(current)  # Return to the original position

    return result  # Return the decoded domain name as a string

def build_query(domain_name, record_type):
    name = encode_name(domain_name)
    #largest number with 16 bits
    identifier = random.randint(0, 65535)
    #flags equivalent to 0001 0000 0000 p2-3 of primer
    header = Header(identifier=identifier, num_qs=1, flags=0x0100)
    question = Question(name=name, type_=record_type, class_=1)
    return header.to_bytes() + question.to_bytes()

def parse_header(response):
    #read 12 bytes from the stream because header is 12 bytes
    identifier, flags, num_qs, num_as, num_auths, num_adds = struct.unpack("!HHHHHH", response.read(12))
    return Header(identifier=identifier, flags=flags, num_qs=num_qs, num_as=num_as, num_auths=num_auths, num_adds=num_adds)

def parse_question(reader):
    name = decode_name(reader)
    data = reader.read(4)
    type_, class_ = struct.unpack("!HH", data)
    #print("name from parse_question", name)
    #print("type", type_)
    #print("class", class_)
    return Question(name, type_, class_)

def parse_record(reader):
    name = decode_name(reader)
    record_header = reader.read(10)
    type_, class_, ttl, data_len = struct.unpack("!HHIH", record_header)
    
    alias, data = None, None
    mx_preference = None

    if type_ == 15:  # MX record
        mx_preference = reader.read(2)
        mx_preference = struct.unpack("!H", mx_preference[:2])[0]
        exchange = decode_name(reader)
        alias = exchange
    elif type_ in [2, 5]:  # NS or CNAME
        alias = decode_name(reader)
    else:
        data = reader.read(data_len)

    return Record(name, type_, class_, ttl, data, alias, mx_preference)


def parse_packet(data):
    reader = BytesIO(data)
    header = parse_header(reader)
    header.parse_flags()
    questions = [parse_question(reader) for _ in range(header.num_qs)]
    answers = [parse_record(reader) for _ in range(header.num_as)]
    authorities = [parse_record(reader) for _ in range(header.num_auths)]
    additionals = [parse_record(reader) for _ in range(header.num_adds)]

    return Packet(header, questions, answers, authorities, additionals)




