ShadowScan is an educational Intrusion Detection System (IDS) that teaches beginners how cyber attacks work through interactive exercises. Users learn about different attack types, run simulated IDS demonstrations, and test their knowledge with quizzes.

All attack simulations are fake - no real network traffic is captured, making the platform ethical and safe to host publicly.

Features

-User Accounts with registration and login
-4 learning paths covering 11 exercises:
  -Network Attacks (port scanning, DoS, brute force)
  -Injection Attacks (SQL injection, XSS)
  -Password Security (weak passwords, credential stuffing, hashing)
  -Malware (viruses, ransomware, trojans)
-Three part exercises: Learn → Simulate → Quiz
-IDS simulation showing how attacks are detected using signature, heuristic, and ML methods
-Progress tracking per user

Quick Start:

pip install -r requirements.txt

python run.py

Run Tests:

pytest tests/ -v


Technologies

-Python 3, Flask, Flask-Login
-SQLite (zero configuration database)
-Bcyrpt
-HTML/CSS with Jinja2 templates
-pytest for testing
