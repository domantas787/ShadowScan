# test_shadowscan.py - Test Suite
# Run with: pytest tests/ -v

import os
import sys
import json
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["SECRET_KEY"] = "test-secret"

# Set up a temp DB before importing anything
import app.db as db_module
_tf = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
db_module.DB_PATH = _tf.name

from app.app import create_app, login_attempts
from app.db import init_db, get_db
from app.exercises import LEARNING_PATHS, EXERCISES, get_exercise, get_path_exercises

# Single shared app for all tests
_app = create_app()
_app.config["TESTING"] = True
_app.config["WTF_CSRF_ENABLED"] = False

with _app.app_context():
    init_db()


def _wipe_db():
    """Clear simulation data between tests (keep users for session continuity)."""
    conn = get_db()
    conn.executescript("DELETE FROM alerts; DELETE FROM progress;")
    conn.commit()
    conn.close()


def _register_and_login(client):
    """Helper: register a user and log them in."""
    client.post("/register", data={
        "username": "testuser", "password": "testpass123", "confirm": "testpass123",
    })
    client.post("/login", data={
        "username": "testuser", "password": "testpass123",
    })


@pytest.fixture
def client():
    with _app.app_context():
        _wipe_db()
    with _app.test_client() as c:
        yield c


@pytest.fixture
def logged_in_client():
    with _app.app_context():
        # Ensure testuser exists (might already from a previous test)
        conn = get_db()
        row = conn.execute("SELECT id FROM users WHERE username = 'testuser'").fetchone()
        conn.close()

    with _app.test_client() as c:
        login_attempts.clear()  # Reset rate limiter for tests
        if not row:
            c.post("/register", data={
                "username": "testuser", "password": "testpass123", "confirm": "testpass123",
            })
        c.post("/login", data={
            "username": "testuser", "password": "testpass123",
        })
        yield c


# Database Tests

class TestDatabase:
    def test_init_db(self, client):
        with _app.app_context():
            conn = get_db()
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            names = {r["name"] for r in tables}
            assert "users" in names
            assert "progress" in names
            assert "alerts" in names

    def test_insert_user(self, client):
        with _app.app_context():
            conn = get_db()
            conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                         ("dbtest", "hash123"))
            conn.commit()
            row = conn.execute("SELECT * FROM users WHERE username = 'dbtest'").fetchone()
            assert row is not None
            assert row["username"] == "dbtest"


# Auth Tests

class TestAuth:
    def test_register_page_loads(self, client):
        assert client.get("/register").status_code == 200

    def test_login_page_loads(self, client):
        assert client.get("/login").status_code == 200

    def test_register_new_user(self, client):
        res = client.post("/register", data={
            "username": "newuser", "password": "password123", "confirm": "password123",
        })
        assert res.status_code == 302  # Redirects to login on success

    def test_register_duplicate_user(self, client):
        client.post("/register", data={
            "username": "dupuser", "password": "pass12345", "confirm": "pass12345",
        })
        res = client.post("/register", data={
            "username": "dupuser", "password": "pass12345", "confirm": "pass12345",
        }, follow_redirects=True)
        assert b"already taken" in res.data

    def test_register_password_mismatch(self, client):
        res = client.post("/register", data={
            "username": "mismatch", "password": "pass12345", "confirm": "different1",
        }, follow_redirects=True)
        assert b"do not match" in res.data

    def test_register_short_password(self, client):
        res = client.post("/register", data={
            "username": "shortpw", "password": "abc", "confirm": "abc",
        }, follow_redirects=True)
        assert b"at least 8" in res.data

    def test_register_invalid_username(self, client):
        res = client.post("/register", data={
            "username": "bad user!", "password": "pass12345", "confirm": "pass12345",
        }, follow_redirects=True)
        assert b"letters, numbers" in res.data

    def test_login_valid(self, client):
        client.post("/register", data={
            "username": "logintest", "password": "pass12345", "confirm": "pass12345",
        })
        res = client.post("/login", data={
            "username": "logintest", "password": "pass12345",
        })
        assert res.status_code == 302  # Redirects to dashboard

    def test_login_invalid(self, client):
        res = client.post("/login", data={
            "username": "nobody", "password": "wrongpass",
        }, follow_redirects=True)
        assert b"Invalid" in res.data

    def test_redirect_when_not_logged_in(self, client):
        res = client.get("/")
        assert res.status_code == 302

    def test_bcrypt_hash_stored(self, client):
        """Verify passwords are hashed with bcrypt (starts with $2b$)."""
        client.post("/register", data={
            "username": "hashcheck", "password": "mypassword123", "confirm": "mypassword123",
        })
        with _app.app_context():
            conn = get_db()
            row = conn.execute("SELECT password_hash FROM users WHERE username = 'hashcheck'").fetchone()
            assert row is not None
            assert row["password_hash"].startswith("$2b$")

    def test_security_headers(self, client):
        """Verify security headers are present."""
        res = client.get("/login")
        assert res.headers.get("X-Frame-Options") == "DENY"
        assert res.headers.get("X-Content-Type-Options") == "nosniff"
        assert "Content-Security-Policy" in res.headers

    def test_csrf_token_in_forms(self, client):
        """Verify forms contain CSRF tokens."""
        assert b"csrf_token" in client.get("/login").data
        assert b"csrf_token" in client.get("/register").data


# Pages Tests

class TestPages:
    def test_dashboard_loads(self, logged_in_client):
        res = logged_in_client.get("/")
        assert res.status_code == 200
        assert b"Network Attacks" in res.data

    def test_learning_path_loads(self, logged_in_client):
        res = logged_in_client.get("/path/network")
        assert res.status_code == 200
        assert b"Port Scanning" in res.data

    def test_invalid_path_redirects(self, logged_in_client):
        res = logged_in_client.get("/path/nonexistent", follow_redirects=True)
        assert b"not found" in res.data

    def test_exercise_loads(self, logged_in_client):
        res = logged_in_client.get("/exercise/port_scan")
        assert res.status_code == 200
        assert b"Port Scanning" in res.data

    def test_invalid_exercise_redirects(self, logged_in_client):
        res = logged_in_client.get("/exercise/fake_exercise", follow_redirects=True)
        assert b"not found" in res.data


# Exercise Content Tests

class TestExercises:
    def test_all_paths_have_exercises(self):
        for path_id, path in LEARNING_PATHS.items():
            for eid in path["exercises"]:
                assert eid in EXERCISES

    def test_all_exercises_have_required_fields(self):
        for eid, ex in EXERCISES.items():
            assert "title" in ex
            assert "path" in ex
            assert "learn" in ex
            assert "quiz" in ex
            assert len(ex["quiz"]) >= 2

    def test_all_quizzes_have_valid_answers(self):
        for eid, ex in EXERCISES.items():
            for q in ex["quiz"]:
                assert 0 <= q["answer"] < len(q["options"])

    def test_get_exercise(self):
        assert get_exercise("port_scan")["title"] == "Port Scanning"

    def test_get_path_exercises(self):
        assert len(get_path_exercises("network")) == 3


# Simulator Tests

class TestSimulator:
    def test_port_scan_simulation(self, logged_in_client):
        res = logged_in_client.post("/exercise/port_scan/simulate")
        data = res.get_json()
        assert data["status"] == "ok"
        assert data["alert_count"] >= 1

    def test_dos_simulation(self, logged_in_client):
        data = logged_in_client.post("/exercise/dos_attack/simulate").get_json()
        assert data["status"] == "ok"

    def test_sqli_simulation(self, logged_in_client):
        data = logged_in_client.post("/exercise/sql_injection/simulate").get_json()
        assert data["status"] == "ok"

    def test_all_exercises_have_simulators(self, logged_in_client):
        for eid in EXERCISES:
            data = logged_in_client.post(f"/exercise/{eid}/simulate").get_json()
            assert data["status"] == "ok", f"Simulator failed for {eid}"

    def test_simulation_clears_previous(self, logged_in_client):
        logged_in_client.post("/exercise/port_scan/simulate")
        res1 = logged_in_client.post("/exercise/port_scan/simulate").get_json()
        # Should only have alerts from the second run
        with _app.app_context():
            conn = get_db()
            count = conn.execute(
                "SELECT COUNT(*) FROM alerts WHERE exercise_id = 'port_scan'"
            ).fetchone()[0]
            assert count == res1["alert_count"]


# Quiz Tests

class TestQuiz:
    def test_submit_correct_answers(self, logged_in_client):
        ex = get_exercise("port_scan")
        correct = [q["answer"] for q in ex["quiz"]]
        data = logged_in_client.post("/exercise/port_scan/quiz",
            data=json.dumps({"answers": correct}),
            content_type="application/json").get_json()
        assert data["correct"] == data["total"]

    def test_submit_wrong_answers(self, logged_in_client):
        ex = get_exercise("port_scan")
        wrong = [0 for _ in ex["quiz"]]
        data = logged_in_client.post("/exercise/port_scan/quiz",
            data=json.dumps({"answers": wrong}),
            content_type="application/json").get_json()
        assert data["correct"] == 0

    def test_quiz_saves_progress(self, logged_in_client):
        ex = get_exercise("dos_attack")
        correct = [q["answer"] for q in ex["quiz"]]
        logged_in_client.post("/exercise/dos_attack/quiz",
            data=json.dumps({"answers": correct}),
            content_type="application/json")
        with _app.app_context():
            conn = get_db()
            prog = conn.execute(
                "SELECT * FROM progress WHERE exercise_id = 'dos_attack'"
            ).fetchone()
            assert prog is not None
            assert prog["completed"] == 1
