import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "database.db")

conn   = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Enable Foreign Keys
cursor.execute("PRAGMA foreign_keys = ON")

# ─── Drop Old Tables for Fresh Upgrade ─────────────────────────────────────────
cursor.execute("DROP TABLE IF EXISTS results")
cursor.execute("DROP TABLE IF EXISTS questions")
cursor.execute("DROP TABLE IF EXISTS subjects")
cursor.execute("DROP TABLE IF EXISTS users")

# ─── Users Table ──────────────────────────────────────────────────────────────
cursor.execute("""
CREATE TABLE users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    email      TEXT    NOT NULL UNIQUE,
    password   TEXT    NOT NULL,
    role       TEXT    DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ─── Subjects Table ───────────────────────────────────────────────────────────
cursor.execute("""
CREATE TABLE subjects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    slug        TEXT NOT NULL UNIQUE,
    description TEXT,
    icon        TEXT
)
""")

# ─── Questions Table ───────────────────────────────────────────────────────────
cursor.execute("""
CREATE TABLE questions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id     INTEGER,
    question       TEXT NOT NULL,
    option_a       TEXT NOT NULL,
    option_b       TEXT NOT NULL,
    option_c       TEXT NOT NULL,
    option_d       TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    explanation    TEXT,
    difficulty     TEXT DEFAULT 'medium',
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL
)
""")

# ─── Results Table ────────────────────────────────────────────────────────────
cursor.execute("""
CREATE TABLE results (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    subject_name TEXT DEFAULT 'Mixed Practice',
    score        INTEGER NOT NULL,
    total        INTEGER NOT NULL,
    percentage   REAL    NOT NULL,
    time_taken   INTEGER DEFAULT 0,
    tab_switches INTEGER DEFAULT 0,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

# ─── Seed Users ───────────────────────────────────────────────────────────────
admin_pw = generate_password_hash("admin123")
student_pw = generate_password_hash("student123")

cursor.execute(
    "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
    ("System Admin", "admin@exam.com", admin_pw, "admin")
)

cursor.execute(
    "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
    ("Rahul Sharma", "student@exam.com", student_pw, "student")
)

# ─── Seed Subjects ────────────────────────────────────────────────────────────
subjects_data = [
    ("Python Programming", "python", "Variables, Data Structures, OOPs & Core Syntax", "🐍"),
    ("Web Development", "webdev", "HTML5, CSS3, JavaScript & Modern Frontend", "🌐"),
    ("Database & SQL", "sql", "Queries, Keys, Relational Databases & Schema", "🗄️"),
    ("Computer & Aptitude", "aptitude", "Computer Fundamentals, Networks & Logical Skills", "💻"),
]

cursor.executemany(
    "INSERT INTO subjects (name, slug, description, icon) VALUES (?, ?, ?, ?)",
    subjects_data
)

# Fetch subject IDs
cursor.execute("SELECT id, slug FROM subjects")
subject_map = {row[1]: row[0] for row in cursor.fetchall()}

# ─── Seed Rich Questions Bank with Explanations ──────────────────────────────
questions = [
    # ── Python ──
    (
        subject_map["python"],
        "Python kya hai?",
        "High-level Programming Language", "Relational Database", "Operating System", "Web Browser",
        "a",
        "Python ek high-level, interpreted aur dynamically-typed general-purpose programming language hai.",
        "easy"
    ),
    (
        subject_map["python"],
        "Python mein text store karne ke liye kaun sa data type use hota hai?",
        "Integer (int)", "Float (float)", "String (str)", "Boolean (bool)",
        "c",
        "Textual data ko Python mein quotes (' ya \") ke andar 'str' (string) data type ke roop mein store kiya jata hai.",
        "easy"
    ),
    (
        subject_map["python"],
        "Python mein function define karne ke liye kaun sa keyword use hota hai?",
        "func", "define", "def", "function",
        "c",
        "Python mein kisi bhi function ko declare karne ke liye 'def' keyword ka istemaal kiya jata hai.",
        "easy"
    ),
    (
        subject_map["python"],
        "Python mein kaun sa data type immutable (unchangeable) hota hai?",
        "List", "Dictionary", "Set", "Tuple",
        "d",
        "Tuples ek baar create hone ke baad modify nahi kiye ja sakte, isliye yeh immutable hote hain.",
        "medium"
    ),
    (
        subject_map["python"],
        "Python mein single-line comment kaise shuru hota hai?",
        "//", "/*", "#", "--",
        "c",
        "Python single-line comments ke liye '#' symbol ka use karta hai.",
        "easy"
    ),

    # ── Web Development ──
    (
        subject_map["webdev"],
        "HTML ka full form kya hai?",
        "HyperText Markup Language", "High Transfer Markup Language", "HyperText Management Language", "Home Tool Markup Language",
        "a",
        "HTML stands for HyperText Markup Language, jo web pages ka structure create karne ke liye use hoti hai.",
        "easy"
    ),
    (
        subject_map["webdev"],
        "Web pages ko style aur colors dene ke liye kaun si technology use hoti hai?",
        "Python", "HTML", "CSS", "C++",
        "c",
        "CSS (Cascading Style Sheets) web pages ke layout, colors aur visual presentation ko design karti hai.",
        "easy"
    ),
    (
        subject_map["webdev"],
        "Kaun sa HTML tag sabse bada heading banata hai?",
        "<h6>", "<head>", "<h1>", "<header>",
        "c",
        "<h1> tag document ki highest rank/biggest size heading define karta hai.",
        "easy"
    ),
    (
        subject_map["webdev"],
        "JavaScript mein block-scoped variable declare karne ke liye kaun sa keyword use hota hai?",
        "var", "let", "define", "global",
        "b",
        "ES6 mein introduce kiya gaya 'let' aur 'const' keywords block-scoped variables banate hain.",
        "medium"
    ),
    (
        subject_map["webdev"],
        "Array ke end mein naya element add karne ka JavaScript method kaun sa hai?",
        "append()", "push()", "insert()", "add()",
        "b",
        "JavaScript arrays mein elements append karne ke liye array.push(item) use hota hai.",
        "easy"
    ),

    # ── SQL & Database ──
    (
        subject_map["sql"],
        "SQL ka full form kya hai?",
        "Structured Query Language", "Simple Queue Language", "System Quick Logic", "Sequential Query Library",
        "a",
        "SQL ka full form Structured Query Language hai, jo relational databases ko manage aur query karne ke kaam aati hai.",
        "easy"
    ),
    (
        subject_map["sql"],
        "Database table se data fetch/retrieve karne ke liye kaun si command use hoti hai?",
        "FETCH", "GET", "SELECT", "PULL",
        "c",
        "SELECT query ka use table se records read karne ke liye kiya jata hai (e.g. SELECT * FROM users).",
        "easy"
    ),
    (
        subject_map["sql"],
        "Table se specific criteria par rows filter karne ke liye kaun sa clause lagaya jata hai?",
        "ORDER BY", "GROUP BY", "WHERE", "LIMIT",
        "c",
        "WHERE clause conditions specify karta hai jisse specific records hi filter hote hain.",
        "easy"
    ),
    (
        subject_map["sql"],
        "Table se saare records aur table structure delete karne ke liye kaun si statement use hoti hai?",
        "REMOVE TABLE", "DELETE TABLE", "DROP TABLE", "CLEAR TABLE",
        "c",
        "DROP TABLE statement table ki definition aur saare rows ko permanently remove kar deti hai.",
        "medium"
    ),
    (
        subject_map["sql"],
        "Primary Key ka main purpose kya hota hai?",
        "Duplicate rows allow karna", "Har row ko uniquely identify karna", "Password encrypt karna", "Table hide karna",
        "b",
        "Primary Key ek ya ek se zyada columns ka combination hota hai jo table ke har record ko uniquely identify karta hai.",
        "easy"
    ),

    # ── Computer & Aptitude ──
    (
        subject_map["aptitude"],
        "CPU ka full form kya hai?",
        "Central Processing Unit", "Computer Personal Unit", "Central Program Utility", "Core Processing Utility",
        "a",
        "CPU stands for Central Processing Unit, jise computer ka brain kaha jata hai.",
        "easy"
    ),
    (
        subject_map["aptitude"],
        "HTTP ka full form kya hai?",
        "HyperText Transfer Protocol", "High Transfer Text Process", "Hyperlink Text Transport Program", "Home Tool Transfer Protocol",
        "a",
        "HTTP (HyperText Transfer Protocol) web browsers aur servers ke beech web pages transfer karne ka protocol hai.",
        "easy"
    ),
    (
        subject_map["aptitude"],
        "1 Byte mein kitne Bits hote hain?",
        "4 Bits", "8 Bits", "16 Bits", "32 Bits",
        "b",
        "Computer architecture mein exactly 8 bits milkar 1 byte banate hain.",
        "easy"
    ),
    (
        subject_map["aptitude"],
        "RAM computer mein kis type ki memory hoti hai?",
        "Non-volatile & Permanent", "Volatile & Temporary", "Optical Storage", "Magnetic Tape",
        "b",
        "RAM (Random Access Memory) volatile memory hoti hai, power off hote hi iska data erase ho jata hai.",
        "easy"
    ),
    (
        subject_map["aptitude"],
        "Domain name (e.g. google.com) ko IP address mein convert karne ka kaam kaun karta hai?",
        "DHCP", "DNS", "FTP", "SMTP",
        "b",
        "DNS (Domain Name System) human-friendly domain names ko machine-readable IP addresses mein resolve karta hai.",
        "medium"
    )
]

cursor.executemany("""
    INSERT INTO questions (subject_id, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", questions)

# ─── Seed Sample Result for Demo Leaderboard ─────────────────────────────────
cursor.execute("""
    INSERT INTO results (user_id, subject_name, score, total, percentage, time_taken, tab_switches)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (2, "Python Programming", 5, 5, 100.0, 95, 0))

conn.commit()
conn.close()

print("[OK] Database upgraded successfully with modern schema!")
print(f"  [+] 2 Users seeded: Admin (admin@exam.com / admin123), Student (student@exam.com / student123)")
print(f"  [+] {len(subjects_data)} Subjects created")
print(f"  [+] {len(questions)} Questions seeded across categories with explanations")
print(f"  [+] Results & Leaderboard ready")
