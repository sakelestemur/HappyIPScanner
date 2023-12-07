import platform
import subprocess
import threading
from queue import Queue
import ipaddress
import socket

# Function to perform ARP scan for a given IP address
def arp_scan(target_ip):
    try:
        subprocess.check_output(["arping", "-c", "1", target_ip], stderr=subprocess.STDOUT, universal_newlines=True)
        print(f"Scanning {target_ip}... [Live] (ARP)")
        live_ips.append(target_ip)
    except subprocess.CalledProcessError:
        print(f"Scanning {target_ip}... [Not Live] (ARP)")

# Function to perform ICMP ping for a given IP address
def icmp_ping(target_ip):
    # Use the appropriate command based on the operating system
    if platform.system().lower() == "windows":
        command = ["ping", "-n", "1", target_ip]
    else:
        command = ["ping", "-c", "1", target_ip]

    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        print(f"Scanning {target_ip}... [Live] (ICMP)")
        live_ips.append(target_ip)
    except subprocess.CalledProcessError:
        print(f"Scanning {target_ip}... [Not Live] (ICMP)")

# Function to perform TCP ping for a given IP address and port range
def tcp_ping(target_ip, ports):
    open_ports = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            sock.connect((target_ip, port))
            print(f"Scanning {target_ip}:{port}... [Live] (TCP)")
            open_ports.append(port)
        except socket.error:
            print(f"Scanning {target_ip}:{port}... [Not Live] (TCP)")
        finally:
            sock.close()

    if open_ports:
        live_ips.append((target_ip, open_ports))

# Function to perform UDP ping for a given IP address and port range
def udp_ping(target_ip, ports):
    open_ports = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        try:
            sock.sendto(b"ping", (target_ip, port))
            data, addr = sock.recvfrom(1024)
            print(f"Scanning {target_ip}:{port}... [Live] (UDP)")
            open_ports.append(port)
        except socket.error:
            print(f"Scanning {target_ip}:{port}... [Not Live] (UDP)")
        finally:
            sock.close()

    if open_ports:
        live_ips.append((target_ip, open_ports))

# Worker function to process IPs from the queue
def worker(ping_method, ports=None):
    while not ip_queue.empty():
        target_ip = ip_queue.get()
        if ping_method == "arp":
            arp_scan(target_ip)
        elif ping_method == "icmp":
            icmp_ping(target_ip)
        elif ping_method == "tcp":
            tcp_ping(target_ip, ports)
        elif ping_method == "udp":
            udp_ping(target_ip, ports)
        ip_queue.task_done()

# Get the base IP address from the user
base_ip = input("Enter the base IP address (e.g., 192.168.1): ")

# Ensure the CIDR input includes the '/' character
while True:
    cidr = input("Enter the CIDR (e.g., /24): ")
    if '/' in cidr:
        break
    else:
        print("CIDR notation must include the '/' character.")

# Let the user select the ping method
ping_method = input("Select the ping method (arp/icmp/tcp/udp): ").lower()

# Validate the ping method
while ping_method not in ["arp", "icmp", "tcp", "udp"]:
    print("Invalid ping method. Please choose either 'arp', 'icmp', 'tcp', or 'udp'.")
    ping_method = input("Select the ping method (arp/icmp/tcp/udp): ").lower()

# If TCP or UDP is selected, ask for the port range
ports = None
if ping_method in ["tcp", "udp"]:
    ports_input = input("Enter the port range (e.g., 80-100) or a comma-separated list of ports: ")
    if "-" in ports_input:
        start_port, end_port = map(int, ports_input.split('-'))
        ports = list(range(start_port, end_port + 1))
    else:
        ports = [int(port) for port in ports_input.split(',')]

# Create a queue to hold IP addresses for pinging
ip_queue = Queue()

# List to store live IPs
live_ips = []

# Generate IP addresses from the CIDR
network = f"{base_ip}{cidr}"
ip_network = ipaddress.IPv4Network(network, strict=False)
ip_addresses = [str(ip) for ip in ip_network]

# Enqueue IP addresses for pinging
for target_ip in ip_addresses:
    ip_queue.put(target_ip)

# Number of worker threads
num_threads = 10

# Create and start worker threads
for _ in range(num_threads):
    thread = threading.Thread(target=worker, args=(ping_method, ports))
    thread.daemon = True
    thread.start()

# Wait for all threads to finish
ip_queue.join()

# Display results based on the selected ping method
print("\nResults:")
if ping_method in ["tcp", "udp"]:
    for entry in live_ips:
        ip = entry[0]
        open_ports = entry[1] if len(entry) == 2 else []
        print(f"{ip} - Open Ports: {', '.join(map(str, open_ports))}")
else:  # ICMP or ARP
    for ip in live_ips:
        print(ip)
