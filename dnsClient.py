import argparse
import socket
from io import BytesIO
from utils import *
from record import Record
import struct
import time

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
        print("Request type:", RECORD_TYPES[self.query_type])

        query = build_query(self.name, self.query_type)
        retries = -1
        start_time = time.time()  # Start tracking the total time
        

        while retries < self.max_retries:
            try:
                retries += 1
                # Create a new socket in each retry attempt
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(self.timeout)

                sock.sendto(query, (self.server, self.port))
                start_query_time = time.time()  # Track the time for this specific query

                response, _ = sock.recvfrom(4096)  # receive the response
                response_time = time.time() - start_query_time  # Calculate response time
                packet = parse_packet(response)

                if packet.header.error_flags() == "No error condition":
                    print(f"Response received after {response_time:.4f} seconds ({retries} retries)")

                    if packet.answers:
                        print(f"***Answer Section ({len(packet.answers)} records)***")
                        for answer in packet.answers:
                            auth = "auth" if packet.header.flags_decoded['AA'] == 0 else "noauth"
                            if answer.type_ == 1:  # A (IPv4)
                                ip = ".".join(str(byte) for byte in answer.data)
                                print(f"IP \t{ip}\t{answer.ttl}\t {auth}")
                            elif answer.type_ == 2:  # NS
                                print(f"NS \t {answer.alias} \t {answer.ttl} \t {auth}")
                            elif answer.type_ == 5:  # CNAME
                                print(f"CNAME \t {answer.alias} \t {answer.ttl} \t {auth}")
                            elif answer.type_ == 15:  # MX
                                print(f"MX \t {answer.alias} \t {answer.mx_preference} \t {answer.ttl} \t {auth}")

                    if packet.additionals:
                        print(f"***Additional Section ({len(packet.additionals)} records)***")
                        for additional in packet.additionals:
                            auth = "auth" if packet.header.flags_decoded['AA'] == 0 else "noauth"
                            if additional.type_ == 1:  # A (IPv4)
                                ip = ".".join(str(byte) for byte in additional.data)
                                print(f"IP \t{ip}\t{additional.ttl}\t {auth}")
                            elif additional.type_ == 2:  # NS
                                print(f"NS \t {additional.alias} \t {additional.ttl} \t {auth}")
                            elif answer.type_ == 5:  # CNAME
                                print(f"CNAME \t {additional.alias} \t {additional.ttl} \t {auth}")
                            elif answer.type_ == 15:  # MX
                                print(f"MX \t {additional.alias} \t {additional.mx_preference} \t {additional.ttl} \t {auth}")
                    else:
                        print("NOTFOUND")

                    # If the response was successful, exit the loop
                    break  

            except socket.timeout:
                print(f"Request timed out after {self.timeout} seconds (attempt {retries})")
                if retries >= self.max_retries:
                    print("Maximum retries reached. Exiting.")
                continue

            finally:
                # Close the socket after each attempt
                sock.close()

        total_time = time.time() - start_time  


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
