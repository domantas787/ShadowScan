"""
Network Attacks learning path content.
Three exercises: port scanning, DoS, brute force.
"""

NETWORK_EXERCISES = {

    "port_scan": {
        "title": "Port Scanning",
        "path": "network",
        "learn": {
            "what_is_it": (
                "A port scan is when someone sends packets to many different ports on a "
                "computer to find out which services are running. Think of it like trying "
                "every door and window on a building to see which ones are open."
            ),
            "how_it_works": (
                "Every network service (like a web server or SSH) listens on a specific "
                "port number. Port 80 is for HTTP, port 22 is for SSH, port 443 is for "
                "HTTPS. An attacker sends connection requests to hundreds or thousands of "
                "ports to map out what's running. Tools like Nmap are commonly used for this."
            ),
            "what_ids_looks_for": (
                "An IDS detects port scans by counting how many different destination ports "
                "a single source IP contacts in a short time window. Normal users connect to "
                "1-3 ports. If someone hits 20+ ports in 30 seconds, that's a scan."
            ),
            "how_to_defend": [
                "Close unused ports with a firewall",
                "Only run services you actually need",
                "Use an IDS to detect and alert on scanning activity",
                "Implement port knocking for sensitive services",
            ],
            "real_world": (
                "The 2017 WannaCry ransomware spread by scanning for open port 445 (SMB) "
                "across the internet. Attackers routinely scan millions of IPs looking for "
                "vulnerable services."
            ),
        },
        "quiz": [
            {
                "question": "What is the main purpose of a port scan?",
                "options": [
                    "To crash a server",
                    "To discover which services are running on a target",
                    "To steal passwords",
                ],
                "answer": 1,
            },
            {
                "question": "How does an IDS typically detect a port scan?",
                "options": [
                    "By reading the attacker's emails",
                    "By counting unique destination ports from one source in a short time",
                    "By checking if the user has antivirus installed",
                ],
                "answer": 1,
            },
            {
                "question": "Which of these is a good defence against port scanning?",
                "options": [
                    "Opening more ports so the scan finishes faster",
                    "Closing unused ports with a firewall",
                    "Turning off the IDS so it doesn't slow things down",
                ],
                "answer": 1,
            },
        ],
    },

    "dos_attack": {
        "title": "Denial of Service (DoS)",
        "path": "network",
        "learn": {
            "what_is_it": (
                "A Denial of Service attack tries to overwhelm a system with so much traffic "
                "that it can't respond to real users. Imagine thousands of people trying to "
                "cram through a single doorway at once — nobody gets through."
            ),
            "how_it_works": (
                "The attacker floods the target with an enormous number of packets per second. "
                "This can be TCP SYN floods (sending connection requests without completing them), "
                "UDP floods, or HTTP request floods. The target's CPU, memory, or bandwidth gets "
                "exhausted and it stops responding to legitimate traffic."
            ),
            "what_ids_looks_for": (
                "An IDS detects DoS by monitoring the packet rate from each source IP. If one "
                "IP sends more than a threshold (e.g. 200 packets per minute), an alert is raised. "
                "The IDS counts packets in a sliding 60-second window."
            ),
            "how_to_defend": [
                "Rate limiting — cap requests per IP address",
                "SYN cookies to handle SYN floods efficiently",
                "Cloud-based DDoS protection like Cloudflare",
                "Firewalls that can detect and block flood traffic",
            ],
            "real_world": (
                "In 2016, the Mirai botnet launched a massive DDoS attack against Dyn DNS, "
                "taking down Twitter, Netflix, Reddit, and many other websites for hours. "
                "The attack used thousands of hacked IoT devices like cameras and routers."
            ),
        },
        "quiz": [
            {
                "question": "What is the goal of a DoS attack?",
                "options": [
                    "To steal data from the server",
                    "To make a service unavailable to legitimate users",
                    "To install malware on the target",
                ],
                "answer": 1,
            },
            {
                "question": "What does an IDS monitor to detect a DoS attack?",
                "options": [
                    "The colour of the packets",
                    "The packet rate from each source IP",
                    "Whether the user is logged in",
                ],
                "answer": 1,
            },
        ],
    },

    "brute_force": {
        "title": "Brute Force Attack",
        "path": "network",
        "learn": {
            "what_is_it": (
                "A brute force attack is when an attacker tries many different passwords "
                "to break into an account. It's like trying every combination on a padlock "
                "until it opens."
            ),
            "how_it_works": (
                "The attacker targets login services like SSH (port 22) or RDP (port 3389). "
                "They use automated tools to try thousands of username/password combinations "
                "per minute. Dictionary attacks use lists of common passwords. Credential "
                "stuffing uses passwords leaked from other data breaches."
            ),
            "what_ids_looks_for": (
                "An IDS detects brute force by counting repeated connection attempts (TCP SYN "
                "packets) to authentication ports from the same source IP. More than 15 attempts "
                "in 60 seconds to ports like 22, 23, or 3389 triggers an alert."
            ),
            "how_to_defend": [
                "Use strong, unique passwords (12+ characters)",
                "Enable multi-factor authentication (MFA)",
                "Lock accounts after several failed attempts",
                "Use fail2ban to auto-block attacking IPs",
                "Disable password login for SSH (use keys instead)",
            ],
            "real_world": (
                "Millions of SSH brute force attempts happen daily across the internet. "
                "The average internet-facing SSH server sees thousands of login attempts "
                "per day from automated botnets."
            ),
        },
        "quiz": [
            {
                "question": "What is a brute force attack?",
                "options": [
                    "Physically breaking into a server room",
                    "Trying many passwords until one works",
                    "Scanning for open ports",
                ],
                "answer": 1,
            },
            {
                "question": "Which defence is most effective against brute force?",
                "options": [
                    "Using a longer ethernet cable",
                    "Multi-factor authentication (MFA)",
                    "Running the server on a different port only",
                ],
                "answer": 1,
            },
            {
                "question": "What ports does an IDS watch for brute force attempts?",
                "options": [
                    "Port 80 (HTTP) and 443 (HTTPS)",
                    "Authentication ports like 22 (SSH) and 3389 (RDP)",
                    "Port 53 (DNS) only",
                ],
                "answer": 1,
            },
        ],
    },
}
