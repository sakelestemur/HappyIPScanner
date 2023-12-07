# happyipscanner
Console based IP scanner using ICMP, ARP, TCP and UDP ping methods.

HappyIPScanner is a straightforward yet powerful tool designed for discovering live hosts on a network. It employs ICMP, ARP, TCP, and UDP protocols to conduct live host scans. When utilizing ICMP, the tool exclusively provides a list of live hosts. However, with TCP and UDP scans, it goes a step further by identifying open ports on the live hosts. Users have the flexibility to specify port ranges or individual ports, separated by commas.

At the core of the application is its ability to concurrently send packets to multiple hosts, thanks to a default worker count of 10. This means that it efficiently scans up to 10 hosts simultaneously, contributing to faster results. Users can adjust the worker count based on factors such as network conditions or the presence of firewalls on the target systems.

Upon execution, HappyIPScanner prompts users to input the base IP address, followed by the CIDR notation (e.g., /24), and then select the packet type to be sent. In the case of TCP and UDP, users are prompted to specify the port(s) for scanning.

HappyIPScanner is a valuable tool for network administrators, security professionals, and anyone looking to identify and analyze live hosts within a network. Its versatility in employing various protocols and ease of use make it a reliable choice for network scanning tasks.
