import argparse
import socket
from io import BytesIO
from utils import *
from record import Record
import struct

DEFAULT_TIMEOUT = 5
DEFAULT_MAX_RETRIES = 3
DEFAULT_PORT = 53
DEFAULT_QUERY_TYPE = 1
DNS_QUERY_TYPES = {
    "A": 1,
    "NS": 2,
    "MX": 15,
}
RECORD_TYPES = {
    1: "A",
    2: "NS",
    5: "CNAME",
    15: "MX"
}

class DNSClient:
    def __init__(self, server, name, timeout=DEFAULT_TIMEOUT, max_retries=DEFAULT_MAX_RETRIES, port=DEFAULT_PORT, query_type=DEFAULT_QUERY_TYPE):
        self.server = server
        self.name = name
        self.timeout = timeout
        self.max_retries = max_retries
        self.port = port
        self.query_type = query_type
        
    def run(self):
        print("DnsClient sending request for", self.name)
        print("Server:", self.server)
        print("Request type:",RECORD_TYPES[self.query_type])

        query = build_query(self.name, self.query_type)
        #print("query", query)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)

        try:
            sock.sendto(query, (self.server, self.port))
            response, _ = sock.recvfrom(1024)  # receive the response from the DNS server that we're using
            #print("response", response)
            
            packet = parse_packet(response)

            if packet.header.error_flags() == "No error condition":
                print("Response received after [time] seconds ([num-retries] retries)")

            if packet.answers: 
                print(f"***Answer Section ({len(packet.answers)} records)***")
                for answer in packet.answers:
                        auth = None
                        if packet.header.flags_decoded['AA'] == 0:
                                auth = "auth"
                        else:
                            auth = "noauth"
                        if answer.type_ == 1:  # check if the answer type is A (IPv4)
                            ip = answer.data
                            full_ip = ".".join(str(byte) for byte in ip)
                            print(f"IP \t{full_ip}\t{answer.ttl}\t {auth}")
                        elif answer.type_ == 2: #NS type
                            print(f"NS \t {answer.alias_str} \t {answer.ttl} \t {auth}")
                        elif answer.type_ == 5: #CNAME the RDATE is the name
                            print(f"CNAME \t {answer.alias_str} \t {answer.ttl} \t {auth}")
                        elif answer.type_ == 15: #MX
                             pref = struct.unpack("!I", answer.data[:4]) #the preference is the first 16 bits 
                             print(f"MX \t {answer.alias_str} \t {pref} \t {answer.ttl} \t {auth}")
                
            if packet.additionals:
                 print(f"***Additional Section ({len(packet.additionals)} records)***")
            else: 
                 print("NOTFOUND")

        except socket.timeout:
            print(f"Request timed out after {self.timeout} seconds")
        finally:
            sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DNS Client")
    parser.add_argument("-t", "--timeout", type=int, default=DEFAULT_TIMEOUT, 
                        help=f"Timeout value to wait before retransmitting in seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("-r", "--max-retries", type=int, default=DEFAULT_MAX_RETRIES,
                        help=f"Maximum number of times to retransmit a query (default: {DEFAULT_MAX_RETRIES})")
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT,
                        help=f"UDP port number of the DNS server (default: {DEFAULT_PORT})")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-mx", action="store_true", help="Query for MX record")
    group.add_argument("-ns", action="store_true", help="Query for NS record")
    
    parser.add_argument("server", help="DNS server IP address (use @ before IP)")
    parser.add_argument("name", help="Domain name to query")
    
    args = parser.parse_args()

    # handling the server argument (remove '@' if included)
    server = args.server.lstrip("@") if args.server.startswith("@") else args.server  # Strip '@' if present
    
    query_type = DNS_QUERY_TYPES.get("MX" if args.mx else "NS" if args.ns else "A")
    
    client = DNSClient(
        server=server,
        name=args.name,
        timeout=args.timeout,
        max_retries=args.max_retries,
        port=args.port,
        query_type=query_type
    )
    client.run()
