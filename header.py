from dataclasses import dataclass
import struct

@dataclass
class Header:
    identifier: int
    flags: int
    num_qs: int = 0
    nums_as: int = 0
    num_auths: int = 0
    num_adds: int = 0
    flags_decoded = {}

    def to_bytes(self):
        return struct.pack("!HHHHHH", self.identifier,  self.flags, self.num_qs,  self.nums_as,  self.num_auths,  self.num_adds)

    def parse_flags(self):
        # Extract each field by shifting and masking the bits
        qr = (self.flags >> 15) & 0x1         # QR is the 16th bit
        opcode = (self.flags >> 11) & 0xF     # OPCODE is bits 12-15
        aa = (self.flags >> 10) & 0x1         # AA is the 11th bit
        tc = (self.flags >> 9) & 0x1          # TC is the 10th bit
        rd = (self.flags >> 8) & 0x1          # RD is the 9th bit
        ra = (self.flags >> 7) & 0x1          # RA is the 8th bit
        z = (self.flags >> 4) & 0x7           # Z is bits 5-7 (3 bits)
        rcode = self.flags & 0xF              # RCODE is bits 1-4 (last 4 bits)

        self.flags_decoded = {
            "QR": qr,
            "OPCODE": opcode,
            "AA": aa,
            "TC": tc,
            "RD": rd,
            "RA": ra,
            "Z": z,
            "RCODE": rcode
        }

    def error_flags(self):
        error = self.flags_decoded["RCODE"]

        if error == 0x0:
            return "No error condition"
        elif error == 0x1:
            return "Format error: the name server was unable to interpret the query"
        elif error == 0x2:
            return "Server failure: the name server was unable to process this query due to a problem with the name server"
        elif error == 0x3:
            return "Name error: meaningful only for responses from an authoritative name server, this code signifies that the domain name referenced in the query does not exist"
        elif error == 0x4:
            return "Not implemented: the name server does not support the requested kind of query"
        elif error == 0x5:
            return "Refused: the name server refuses to perform the requested operation for policy reasons"
        else:
            return "Code could not be parsed."
