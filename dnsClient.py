import argparse

DEFAULT_TIMEOUT = 5
DEFAULT_MAX_RETRIES = 3
DEFAULT_PORT = 53

class DNSClient:
    def __init__(self, server, name, timeout=DEFAULT_TIMEOUT, max_retries=DEFAULT_MAX_RETRIES, port=DEFAULT_PORT, query_type=None):
        self.server = server
        self.name = name
        self.timeout = timeout
        self.max_retries = max_retries
        self.port = port
        self.query_type = query_type
        
    def run(self):
        print(f"server: {self.server}\nname: {self.name}\ntimeout: {self.timeout}\nmax_retries: {self.max_retries}\nport: {self.port}\nquery: {self.query_type}")
        
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
    
    parser.add_argument("server", help="DNS server IP address")
    parser.add_argument("name", help="Domain name to query")
    
    args = parser.parse_args()
    
    client = DNSClient(
        server=args.server,
        name=args.name,
        timeout=args.timeout,
        max_retries=args.max_retries,
        port=args.port,
        query_type="MX" if args.mx else "NS" if args.ns else "A"
    )
    client.run()
    