import subprocess
import sys

def run_dns_query(args):
    command = [sys.executable, "dnsClient.py"] + args
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    print("-" * 50)

def main():
    # Test case 1: Basic A record query
    run_dns_query(["@8.8.8.8", "example.com"])

    # Test case 2: MX record query
    run_dns_query(["-mx", "@8.8.8.8", "gmail.com"])

    # Test case 3: NS record query
    run_dns_query(["-ns", "@8.8.8.8", "amazon.com"])
    
    # Test case 4: Combination of options
    run_dns_query(["-mx", "-t", "2", "-r", "2", "@8.8.8.8", "microsoft.com"])

    # Test case 5: Custom timeout
    run_dns_query(["-t", "1", "@132.216.177.160", "example.com"])

    # Test case 6: Custom port and custom retries
    run_dns_query(["-r", "7", "-p", "8080", "@8.8.8.8", "example.com"])

    # Test case 7: Non-existent domain
    run_dns_query(["@8.8.8.8", "nonexistent-domain-12345.com"])

    # Test case 8: Invalid DNS server
    run_dns_query(["@192.0.2.1", "example.com"])  # Using a reserved IP address

    # Test case 9: Query against a different DNS server
    run_dns_query(["@1.1.1.1", "cloudflare.com"])  # Using Cloudflare's DNS
    
    # Test case 10: Syntax error handling
    run_dns_query(["-t", "-p", "@8.8.8.8", "example.com"])

if __name__ == "__main__":
    main()