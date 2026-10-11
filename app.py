from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "online_exam_secret_key_2024"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "database.db")


# ─── Helper: DB Connection ───────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ─── Decorator: Login Required ───────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Pehle login karein.", "warning")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated


# ─── HOME / LOGIN PAGE ───────────────────────────────────────────────────────
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")


# ─── LOGIN ───────────────────────────────────────────────────────────────────
@app.route("/login", methods=["POST"])
def login():
    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["id"]
        session["name"]    = user["name"]
        flash(f"Welcome back, {user['name']}! 👋", "success")
        return redirect(url_for("dashboard"))

    flash("Email ya password galat hai. Dobara try karein.", "danger")
    return redirect(url_for("home"))


# ─── REGISTER ────────────────────────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Sab fields bharein.", "danger")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password kam se kam 6 characters ka hona chahiye.", "danger")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)

        conn   = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_pw)
            )
            conn.commit()
            conn.close()
            flash("Registration successful! Ab login karein. ✅", "success")
            return redirect(url_for("home"))

        except sqlite3.IntegrityError:
            conn.close()
            flash("Yeh email already registered hai.", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")


# ─── LOGOUT ──────────────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    flash("Aap logout ho gaye hain.", "info")
    return redirect(url_for("home"))


# ─── DASHBOARD ───────────────────────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    conn    = get_db()
    cursor  = conn.cursor()

    # Last 5 attempts
    cursor.execute(
        "SELECT score, total, percentage, attempted_at FROM results WHERE user_id = ? ORDER BY attempted_at DESC LIMIT 5",
        (user_id,)
    )
    recent_results = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", name=session["name"], recent_results=recent_results)


# ─── EXAM ────────────────────────────────────────────────────────────────────
@app.route("/exam")
@login_required
def exam():
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 10")
    questions = cursor.fetchall()
    conn.close()

    if not questions:
        flash("Abhi koi questions available nahi hain. Admin se contact karein.", "warning")
        return redirect(url_for("dashboard"))

    return render_template("exam.html", questions=questions)


# ─── SUBMIT EXAM ─────────────────────────────────────────────────────────────
@app.route("/submit_exam", methods=["POST"])
@login_required
def submit_exam():
    conn   = get_db()
    cursor = conn.cursor()

    # Fetch all questions
    cursor.execute("SELECT * FROM questions")
    all_questions = {str(q["id"]): q for q in cursor.fetchall()}

    score   = 0
    results = []

    for qid, question in all_questions.items():
        submitted = request.form.get(f"q_{qid}", "").strip().lower()
        correct   = question["correct_answer"].strip().lower()
        is_correct = submitted == correct

        if is_correct:
            score += 1

        option_map = {
            "a": question["option_a"],
            "b": question["option_b"],
            "c": question["option_c"],
            "d": question["option_d"],
        }

        results.append({
            "question":       question["question"],
            "submitted":      option_map.get(submitted, "Not answered"),
            "correct_answer": option_map.get(correct, correct),
            "is_correct":     is_correct,
        })

    total      = len(all_questions)
    percentage = round((score / total) * 100, 1) if total > 0 else 0
    passed     = percentage >= 60

    # Save result to DB
    cursor.execute(
        "INSERT INTO results (user_id, score, total, percentage) VALUES (?, ?, ?, ?)",
        (session["user_id"], score, total, percentage)
    )
    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        score=score,
        total=total,
        percentage=percentage,
        passed=passed,
        results=results,
    )


# ─── ALL RESULTS HISTORY ─────────────────────────────────────────────────────
@app.route("/results")
@login_required
def results_history():
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT score, total, percentage, attempted_at FROM results WHERE user_id = ? ORDER BY attempted_at DESC",
        (session["user_id"],)
    )
    all_results = cursor.fetchall()
    conn.close()
    return render_template("results_history.html", all_results=all_results, name=session["name"])


# ─── RUN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)