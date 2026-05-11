
#Main Flask app

import os
import time
from collections import defaultdict

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf.csrf import CSRFProtect

from app.db import get_db, init_db
from app.auth import auth_bp, login_manager, bcrypt
from app.exercises import LEARNING_PATHS, EXERCISES, get_exercise, get_path, get_path_exercises
from app.simulator import run_simulation_with_visuals


# simple in-memory rate limiter
login_attempts = defaultdict(list)

MAX_LOGIN_ATTEMPTS = 5      # max tries in the window
RATE_LIMIT_WINDOW = 60      # window length in seconds


def is_rate_limited(ip):
    """Has this IP exceeded the login rate limit?"""
    now = time.time()
    # drop attempts that are old
    login_attempts[ip] = [t for t in login_attempts[ip] if now - t < RATE_LIMIT_WINDOW]
    return len(login_attempts[ip]) >= MAX_LOGIN_ATTEMPTS


def record_login_attempt(ip):
    login_attempts[ip].append(time.time())


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Secret key
    app.secret_key = os.getenv("SECRET_KEY", "shadowscan-dev-key-change-in-production")

    # session cookie hardening
    app.config["SESSION_COOKIE_HTTPONLY"] = True     # JS can't read the cookie
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"    # helps prevent CSRF

    # CSRF protection on every POST form
    csrf = CSRFProtect(app)

    # Set up the extensions
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # auth routes
    app.register_blueprint(auth_bp)

    # create the DB tables
    with app.app_context():
        init_db()

   
    # JSON API endpoints
    @csrf.exempt
    @app.route("/exercise/<exercise_id>/simulate", methods=["POST"])
    @login_required
    def simulate(exercise_id):
        """Run an attack simulation and return the alerts + visualisation data."""
        ex = get_exercise(exercise_id)
        if not ex:
            return jsonify({"error": "Exercise not found"}), 404

        result = run_simulation_with_visuals(current_user.id, exercise_id)
        return jsonify({
            "status": "ok",
            "alert_count": len(result["alerts"]),
            "alerts": result["alerts"],
            "visual": result["visual"],
        })

    @csrf.exempt
    @app.route("/exercise/<exercise_id>/quiz", methods=["POST"])
    @login_required
    def submit_quiz(exercise_id):
        """Score the quiz answers and save the user's progress."""
        ex = get_exercise(exercise_id)
        if not ex:
            return jsonify({"error": "Exercise not found"}), 404

        quiz = ex.get("quiz", [])
        body = request.get_json() or {}
        user_answers = body.get("answers", [])

        # Compare each answer to the correct one
        correct = 0
        results = []
        for i, question in enumerate(quiz):
            chosen = user_answers[i] if i < len(user_answers) else -1
            is_correct = (chosen == question["answer"])
            if is_correct:
                correct += 1
            results.append({
                "question": question["question"],
                "correct_answer": question["answer"],
                "user_answer": chosen,
                "is_correct": is_correct,
            })

        # save progress
        conn = get_db()
        conn.execute(
            """INSERT INTO progress (user_id, exercise_id, completed, quiz_score, completed_at)
               VALUES (?, ?, 1, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(user_id, exercise_id)
               DO UPDATE SET completed = 1, quiz_score = ?, completed_at = CURRENT_TIMESTAMP""",
            (current_user.id, exercise_id, correct, correct)
        )
        conn.commit()
        conn.close()

        return jsonify({
            "correct": correct,
            "total": len(quiz),
            "results": results,
        })

    # Security headers added to every response
    @app.after_request
    def add_security_headers(response):
        response.headers["X-Frame-Options"] = "DENY"               # clickjacking protection
        response.headers["X-Content-Type-Options"] = "nosniff"     # no MIME sniffing
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # CSP - only allow scripts from self
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Page routes
    @app.route("/")
    @login_required
    def dashboard():
        """Main page after login - shows all 4 learning paths with progress bars."""
        conn = get_db()
        rows = conn.execute(
            "SELECT exercise_id, completed, quiz_score FROM progress WHERE user_id = ?",
            (current_user.id,)
        ).fetchall()
        conn.close()

        # turn rows into a lookup
        user_progress = {}
        for r in rows:
            user_progress[r["exercise_id"]] = {
                "completed": r["completed"],
                "quiz_score": r["quiz_score"],
            }

        # build the list of paths
        paths = []
        for path_id, info in LEARNING_PATHS.items():
            total = len(info["exercises"])
            done = sum(
                1 for eid in info["exercises"]
                if user_progress.get(eid, {}).get("completed", 0)
            )
            paths.append({
                "id": path_id,
                "title": info["title"],
                "description": info["description"],
                "icon": info["icon"],
                "total": total,
                "completed": done,
            })

        return render_template("dashboard.html", paths=paths)

    @app.route("/path/<path_id>")
    @login_required
    def learning_path(path_id):
        """List of exercises for one specific learning path."""
        path = get_path(path_id)
        if not path:
            flash("Learning path not found.", "error")
            return redirect(url_for("dashboard"))

        exercises = get_path_exercises(path_id)

        # get the users progress
        conn = get_db()
        rows = conn.execute(
            "SELECT exercise_id, completed, quiz_score FROM progress WHERE user_id = ?",
            (current_user.id,)
        ).fetchall()
        conn.close()

        user_progress = {}
        for r in rows:
            user_progress[r["exercise_id"]] = {
                "completed": r["completed"],
                "quiz_score": r["quiz_score"],
            }

        return render_template(
            "path.html",
            path_id=path_id,
            path=path,
            exercises=exercises,
            progress=user_progress,
        )

    @app.route("/exercise/<exercise_id>")
    @login_required
    def exercise(exercise_id):
        """Individual exercise page with the Learn/Simulate/Quiz tabs."""
        ex = get_exercise(exercise_id)
        if not ex:
            flash("Exercise not found.", "error")
            return redirect(url_for("dashboard"))

        conn = get_db()
        # any previous alerts from running the simulation before
        alerts = conn.execute(
            "SELECT * FROM alerts WHERE user_id = ? AND exercise_id = ? "
            "ORDER BY detected_at DESC",
            (current_user.id, exercise_id)
        ).fetchall()
        # progress
        prog = conn.execute(
            "SELECT completed, quiz_score FROM progress WHERE user_id = ? AND exercise_id = ?",
            (current_user.id, exercise_id)
        ).fetchone()
        conn.close()

        return render_template(
            "exercise.html",
            exercise_id=exercise_id,
            exercise=ex,
            alerts=[dict(a) for a in alerts],
            progress=dict(prog) if prog else None,
        )

    # make the rate limiter functions reachable
    app.is_rate_limited = is_rate_limited
    app.record_login_attempt = record_login_attempt

    return app
