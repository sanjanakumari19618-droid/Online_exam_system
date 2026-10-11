from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "online_exam_system_super_secret_key_2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "database.db")


# ─── Helper: DB Connection ───────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
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


# ─── Decorator: Admin Required ───────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "admin":
            flash("Is page ko dekhne ke liye Admin permission chahiye.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


# ─── HOME / LOGIN PAGE ───────────────────────────────────────────────────────
@app.route("/")
def home():
    if "user_id" in session:
        if session.get("role") == "admin":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard"))
    return render_template("login.html")


# ─── LOGIN ───────────────────────────────────────────────────────────────────
@app.route("/login", methods=["POST"])
def login():
    email    = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["id"]
        session["name"]    = user["name"]
        session["email"]   = user["email"]
        session["role"]    = user["role"]
        flash(f"Swagat hai, {user['name']}! 👋", "success")

        if user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))
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
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Sabhi fields bharna zaroori hai.", "danger")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password kam se kam 6 characters ka hona chahiye.", "danger")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)

        conn   = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, 'student')",
                (name, email, hashed_pw)
            )
            conn.commit()
            conn.close()
            flash("Registration successful! Ab aap login kar sakte hain. ✅", "success")
            return redirect(url_for("home"))

        except sqlite3.IntegrityError:
            conn.close()
            flash("Yeh email address already registered hai.", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")


# ─── LOGOUT ──────────────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    flash("Aap logout ho gaye hain.", "info")
    return redirect(url_for("home"))


# ─── STUDENT DASHBOARD ───────────────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    conn    = get_db()
    cursor  = conn.cursor()

    # Subjects with available question counts
    cursor.execute("""
        SELECT s.*, COUNT(q.id) as question_count
        FROM subjects s
        LEFT JOIN questions q ON s.id = q.subject_id
        GROUP BY s.id
    """)
    subjects = cursor.fetchall()

    # Total questions across all subjects
    cursor.execute("SELECT COUNT(*) FROM questions")
    total_db_questions = cursor.fetchone()[0]

    # Student stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total_attempts,
            AVG(percentage) as avg_percentage,
            MAX(percentage) as best_percentage
        FROM results
        WHERE user_id = ?
    """, (user_id,))
    stats_row = cursor.fetchone()

    total_attempts  = stats_row["total_attempts"] or 0
    avg_percentage  = round(stats_row["avg_percentage"], 1) if stats_row["avg_percentage"] else 0
    best_percentage = round(stats_row["best_percentage"], 1) if stats_row["best_percentage"] else 0

    # Recent 5 attempts
    cursor.execute("""
        SELECT id, subject_name, score, total, percentage, time_taken, attempted_at
        FROM results
        WHERE user_id = ?
        ORDER BY attempted_at DESC
        LIMIT 5
    """, (user_id,))
    recent_results = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        name=session["name"],
        subjects=subjects,
        total_db_questions=total_db_questions,
        total_attempts=total_attempts,
        avg_percentage=avg_percentage,
        best_percentage=best_percentage,
        recent_results=recent_results
    )


# ─── EXAM SETUP & START ──────────────────────────────────────────────────────
@app.route("/exam")
@login_required
def exam():
    subject_id = request.args.get("subject_id")
    conn       = get_db()
    cursor     = conn.cursor()

    subject_name = "All Subjects (Mock Test)"
    if subject_id and subject_id != "all":
        cursor.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,))
        sub = cursor.fetchone()
        if sub:
            subject_name = sub["name"]
            cursor.execute("SELECT * FROM questions WHERE subject_id = ? ORDER BY RANDOM() LIMIT 10", (subject_id,))
        else:
            cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 10")
    else:
        cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 10")

    questions = cursor.fetchall()
    conn.close()

    if not questions:
        flash("Is category mein abhi koi questions available nahi hain. Admin jald add karega.", "warning")
        return redirect(url_for("dashboard"))

    # Track question IDs in session so scoring only checks these specific questions
    session["current_exam"] = {
        "question_ids": [q["id"] for q in questions],
        "subject_name": subject_name,
        "total": len(questions)
    }

    # Timer duration in seconds (10 questions = 10 mins = 600 seconds)
    duration_seconds = len(questions) * 60

    return render_template(
        "exam.html",
        questions=questions,
        subject_name=subject_name,
        duration_seconds=duration_seconds,
        total_questions=len(questions)
    )


# ─── SUBMIT EXAM ─────────────────────────────────────────────────────────────
@app.route("/submit_exam", methods=["POST"])
@login_required
def submit_exam():
    exam_meta = session.get("current_exam")
    if not exam_meta or not exam_meta.get("question_ids"):
        flash("Invalid exam session. Kripya dobara exam start karein.", "warning")
        return redirect(url_for("dashboard"))

    question_ids = exam_meta["question_ids"]
    subject_name = exam_meta.get("subject_name", "General Exam")

    # Anti-cheating & Time metrics submitted from frontend
    time_taken   = int(request.form.get("time_taken", 0))
    tab_switches = int(request.form.get("tab_switches", 0))

    conn   = get_db()
    cursor = conn.cursor()

    # Fetch ONLY the questions that were presented in this exam
    placeholders = ",".join(["?"] * len(question_ids))
    cursor.execute(f"SELECT * FROM questions WHERE id IN ({placeholders})", question_ids)
    q_dict = {q["id"]: q for q in cursor.fetchall()}

    score   = 0
    results = []

    for qid in question_ids:
        question = q_dict.get(qid)
        if not question:
            continue

        submitted = request.form.get(f"q_{qid}", "").strip().lower()
        correct   = question["correct_answer"].strip().lower()
        is_correct = (submitted == correct)

        if is_correct:
            score += 1

        option_map = {
            "a": question["option_a"],
            "b": question["option_b"],
            "c": question["option_c"],
            "d": question["option_d"],
        }

        results.append({
            "id":             question["id"],
            "question":       question["question"],
            "submitted_opt":  submitted.upper() if submitted else "None",
            "submitted":      option_map.get(submitted, "Not Answered"),
            "correct_opt":    correct.upper(),
            "correct_answer": option_map.get(correct, correct),
            "is_correct":     is_correct,
            "explanation":    question["explanation"] or "No specific explanation provided."
        })

    total      = len(question_ids)
    percentage = round((score / total) * 100, 1) if total > 0 else 0
    passed     = percentage >= 60

    # Save result to DB
    cursor.execute("""
        INSERT INTO results (user_id, subject_name, score, total, percentage, time_taken, tab_switches)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session["user_id"], subject_name, score, total, percentage, time_taken, tab_switches))
    result_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Clear current exam session
    session.pop("current_exam", None)

    return render_template(
        "result.html",
        result_id=result_id,
        subject_name=subject_name,
        score=score,
        total=total,
        percentage=percentage,
        passed=passed,
        time_taken=time_taken,
        tab_switches=tab_switches,
        results=results
    )


# ─── CERTIFICATE ─────────────────────────────────────────────────────────────
@app.route("/certificate/<int:result_id>")
@login_required
def certificate(result_id):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, u.name as user_name
        FROM results r
        JOIN users u ON r.user_id = u.id
        WHERE r.id = ?
    """, (result_id,))
    res = cursor.fetchone()
    conn.close()

    if not res:
        flash("Certificate nahi mila.", "danger")
        return redirect(url_for("results_history"))

    # Security check: User can only view their own certificate unless admin
    if res["user_id"] != session["user_id"] and session.get("role") != "admin":
        flash("Aap doosre user ka certificate nahi dekh sakte.", "danger")
        return redirect(url_for("dashboard"))

    if res["percentage"] < 60:
        flash("Certificate sirf exam pass (60%+) karne par milta hai.", "warning")
        return redirect(url_for("results_history"))

    cert_serial = f"OE-{res['id']:04d}-{res['user_id']:03d}"

    return render_template(
        "certificate.html",
        res=res,
        cert_serial=cert_serial,
        user_name=res["user_name"]
    )


# ─── GLOBAL LEADERBOARD ──────────────────────────────────────────────────────
@app.route("/leaderboard")
@login_required
def leaderboard():
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            u.name as user_name,
            r.subject_name,
            r.score,
            r.total,
            r.percentage,
            r.time_taken,
            r.attempted_at
        FROM results r
        JOIN users u ON r.user_id = u.id
        ORDER BY r.percentage DESC, r.score DESC, r.time_taken ASC
        LIMIT 20
    """)
    top_scores = cursor.fetchall()
    conn.close()

    return render_template("leaderboard.html", top_scores=top_scores)


# ─── ALL RESULTS HISTORY ─────────────────────────────────────────────────────
@app.route("/results")
@login_required
def results_history():
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, subject_name, score, total, percentage, time_taken, tab_switches, attempted_at
        FROM results
        WHERE user_id = ?
        ORDER BY attempted_at DESC
    """, (session["user_id"],))
    all_results = cursor.fetchall()
    conn.close()

    return render_template("results_history.html", all_results=all_results, name=session["name"])


# ─── ADMIN DASHBOARD ─────────────────────────────────────────────────────────
@app.route("/admin")
@admin_required
def admin_dashboard():
    conn   = get_db()
    cursor = conn.cursor()

    # Overview Metrics
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*), AVG(percentage) FROM results")
    res_stats = cursor.fetchone()
    total_exams = res_stats[0]
    avg_platform_score = round(res_stats[1], 1) if res_stats[1] else 0

    # Subjects for dropdown
    cursor.execute("SELECT * FROM subjects ORDER BY name ASC")
    subjects = cursor.fetchall()

    # All Questions
    cursor.execute("""
        SELECT q.*, s.name as subject_name
        FROM questions q
        LEFT JOIN subjects s ON q.subject_id = s.id
        ORDER BY q.id DESC
    """)
    questions = cursor.fetchall()

    # Recent student results
    cursor.execute("""
        SELECT r.*, u.name as user_name, u.email as user_email
        FROM results r
        JOIN users u ON r.user_id = u.id
        ORDER BY r.attempted_at DESC
        LIMIT 15
    """)
    recent_submissions = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        total_students=total_students,
        total_questions=total_questions,
        total_exams=total_exams,
        avg_platform_score=avg_platform_score,
        subjects=subjects,
        questions=questions,
        recent_submissions=recent_submissions
    )


# ─── ADMIN: ADD QUESTION ─────────────────────────────────────────────────────
@app.route("/admin/add_question", methods=["POST"])
@admin_required
def admin_add_question():
    subject_id     = request.form.get("subject_id")
    question_text  = request.form.get("question", "").strip()
    opt_a          = request.form.get("option_a", "").strip()
    opt_b          = request.form.get("option_b", "").strip()
    opt_c          = request.form.get("option_c", "").strip()
    opt_d          = request.form.get("option_d", "").strip()
    correct_answer = request.form.get("correct_answer", "").strip().lower()
    explanation    = request.form.get("explanation", "").strip()
    difficulty     = request.form.get("difficulty", "medium").strip()

    if not all([question_text, opt_a, opt_b, opt_c, opt_d, correct_answer]):
        flash("Question aur charon options bharna anivarya hai.", "danger")
        return redirect(url_for("admin_dashboard"))

    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO questions (subject_id, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (subject_id, question_text, opt_a, opt_b, opt_c, opt_d, correct_answer, explanation, difficulty))
    conn.commit()
    conn.close()

    flash("Naya question successfully add ho gaya! 🎯", "success")
    return redirect(url_for("admin_dashboard"))


# ─── ADMIN: DELETE QUESTION ──────────────────────────────────────────────────
@app.route("/admin/delete_question/<int:question_id>", methods=["POST"])
@admin_required
def admin_delete_question(question_id):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()

    flash("Question successfully delete kar diya gaya.", "info")
    return redirect(url_for("admin_dashboard"))


# ─── RUN SERVER ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)