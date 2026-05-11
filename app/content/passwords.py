"""
Password Security learning path content.
Covers weak passwords, credential stuffing, and password hashing.
"""

PASSWORD_EXERCISES = {

    "weak_passwords": {
        "title": "Weak Passwords",
        "path": "passwords",
        "learn": {
            "what_is_it": (
                "Weak passwords are short, predictable, or commonly used passwords that "
                "attackers can easily guess or crack. '123456', 'password', and 'qwerty' "
                "are among the most common passwords year after year."
            ),
            "how_it_works": (
                "Attackers use wordlists — massive files containing millions of known passwords "
                "from previous data breaches. Tools like Hashcat or John the Ripper can test "
                "billions of password hashes per second. A 6-character lowercase password can "
                "be cracked in under a second. A 12-character mixed password could take centuries."
            ),
            "what_ids_looks_for": (
                "While an IDS doesn't directly check password strength, it can detect the "
                "consequences of weak passwords: successful logins from unusual locations, "
                "multiple accounts accessed from one IP, or login patterns that suggest "
                "compromised credentials."
            ),
            "how_to_defend": [
                "Use passwords with 12+ characters mixing upper, lower, numbers, and symbols",
                "Use a password manager to generate and store unique passwords",
                "Never reuse passwords across different sites",
                "Enable multi-factor authentication everywhere possible",
            ],
            "real_world": (
                "The 2012 LinkedIn breach exposed 6.5 million password hashes. Because many "
                "users had weak passwords, over 90% were cracked within days. The leaked "
                "passwords were then used in credential stuffing attacks on other sites."
            ),
        },
        "quiz": [
            {
                "question": "How long would it take to crack a 6-character lowercase password?",
                "options": [
                    "Several years",
                    "Less than a second with modern tools",
                    "About one week",
                ],
                "answer": 1,
            },
            {
                "question": "What is the best way to manage strong, unique passwords?",
                "options": [
                    "Write them on a sticky note on your monitor",
                    "Use the same strong password everywhere",
                    "Use a password manager",
                ],
                "answer": 2,
            },
        ],
    },

    "credential_stuffing": {
        "title": "Credential Stuffing",
        "path": "passwords",
        "learn": {
            "what_is_it": (
                "Credential stuffing is when attackers take username/password pairs leaked "
                "from one data breach and try them on other websites. Since many people "
                "reuse passwords, this is surprisingly effective."
            ),
            "how_it_works": (
                "After a data breach, stolen credentials get sold or shared online. Attackers "
                "use automated tools to try these credentials on banking sites, email providers, "
                "and social media. If you used the same password on LinkedIn and your bank, "
                "and LinkedIn gets breached, your bank account is now at risk."
            ),
            "what_ids_looks_for": (
                "An IDS detects credential stuffing by spotting: many login attempts from one "
                "IP using different usernames, login attempts at unusual speeds (faster than "
                "a human could type), and traffic patterns matching known attack tools."
            ),
            "how_to_defend": [
                "Never reuse passwords across different sites",
                "Enable multi-factor authentication",
                "Use a password manager for unique passwords",
                "Check haveibeenpwned.com to see if your accounts were in a breach",
            ],
            "real_world": (
                "In 2020, over 500,000 Zoom accounts were found being sold on the dark web. "
                "They weren't stolen from Zoom directly — attackers used credential stuffing "
                "with passwords leaked from other breaches."
            ),
        },
        "quiz": [
            {
                "question": "What makes credential stuffing possible?",
                "options": [
                    "Weak encryption on websites",
                    "People reusing the same password on multiple sites",
                    "Slow internet connections",
                ],
                "answer": 1,
            },
            {
                "question": "What is the single best defence against credential stuffing?",
                "options": [
                    "Using a VPN",
                    "Using unique passwords for every site",
                    "Changing your password every week",
                ],
                "answer": 1,
            },
        ],
    },

    "password_hashing": {
        "title": "Password Hashing",
        "path": "passwords",
        "learn": {
            "what_is_it": (
                "Password hashing is how websites safely store your password. Instead of "
                "saving your actual password, they run it through a one-way mathematical "
                "function (a hash) and store the result. When you log in, they hash what "
                "you typed and compare it to the stored hash."
            ),
            "how_it_works": (
                "A hash function takes any input and produces a fixed-size output. For example, "
                "'password123' might hash to 'ef92b778...'. The same input always gives the "
                "same hash, but you can't reverse it to get the original password. Modern "
                "algorithms like bcrypt add 'salt' (random data) so even identical passwords "
                "produce different hashes."
            ),
            "what_ids_looks_for": (
                "An IDS doesn't directly monitor hashing, but it can detect attacks against "
                "hashed passwords: unusual database queries trying to extract the users table, "
                "or signs that an attacker is trying to exfiltrate the hash database for "
                "offline cracking."
            ),
            "how_to_defend": [
                "Use bcrypt, scrypt, or Argon2 for hashing (never MD5 or plain SHA)",
                "Always use unique salts per password",
                "Add pepper (a server-side secret) for extra security",
                "Use key stretching (multiple rounds) to slow down cracking",
            ],
            "real_world": (
                "Adobe's 2013 breach exposed 153 million accounts. They used weak 3DES "
                "encryption instead of proper hashing, with no salting. This made it trivial "
                "to crack millions of passwords. Had they used bcrypt with salts, the damage "
                "would have been far less severe."
            ),
        },
        "quiz": [
            {
                "question": "Why do websites hash passwords instead of storing them directly?",
                "options": [
                    "To make the database smaller",
                    "So even if the database is stolen, passwords can't be read directly",
                    "To make login faster",
                ],
                "answer": 1,
            },
            {
                "question": "What is a 'salt' in password hashing?",
                "options": [
                    "A type of encryption key",
                    "Random data added to each password before hashing so identical passwords produce different hashes",
                    "A seasoning for the server rack",
                ],
                "answer": 1,
            },
        ],
    },
}
