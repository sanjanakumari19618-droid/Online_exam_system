# 📝 Online Exam System (Pro Edition)

Python (Flask) aur SQLite par bana hua comprehensive aur modern **Online Exam & Assessment Management System**.

---

## 🌟 Key Features Implemented

### 1. 🛡️ Exam Experience & Proctoring
- **Live Countdown Timer:** Configurable timer with urgent pulsing animation and automatic submission upon expiry.
- **Anti-Cheating Window/Tab Detection:** Tracks whenever a candidate leaves the exam tab or minimizes the window. Shows alert warnings (3 warnings limit before auto-submit).
- **Question Navigator Palette:** Interactive 1-10 grid showing Answered (Green) vs Unanswered (Gray) status, with instant scroll-to-question.
- **Copy & Right-Click Disabled:** Restricts copying exam questions or opening inspect element during test.

### 2. 📂 Subject & Category System
- **Topic Selection:** Python Programming, Web Development, Database & SQL, Computer & Aptitude, plus Mixed Full Mock Test.
- **Dynamic Question Selection & Bug-free Scoring:** Scores strictly the questions presented in the current attempt.

### 3. 💡 Analysis & Gamification
- **Instant Answer Key with Explanations:** Result screen displays each question, your answer, correct answer, and detailed solution explanations.
- **Celebration Confetti:** Animated celebration upon passing (≥ 60%).
- **Printable Certificate of Completion:** Pass karne par authentic verifiable certificate (with ID serial number, signature, and stamp) jise browser se direct PDF download ya print kiya ja sakta hai.
- **Global Leaderboard:** Top rankers list with 🥇 Gold, 🥈 Silver, 🥉 Bronze medals.

### 4. ⚙️ Admin Management Portal
- **Role-based Authentication:** Separate student and admin roles.
- **Question Bank CRUD:** Admin portal se direct naye questions add karein (options, correct answer, explanation, difficulty) aur delete karein.
- **Live Submissions Audit:** Sabhi students ke results, marks, aur anti-cheat metrics live dekhein.

### 5. 🎨 UI/UX & Dark Mode
- **Dark / Light Mode Toggle:** Persistent theme memory (stored in `localStorage`).
- **Responsive Design:** Mobile, tablet, aur desktop par optimized layout.

---

## ⚡ Demo Login Credentials

Login page par 1-click auto-fill buttons available hain:

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@exam.com` | `admin123` |
| **Student** | `student@exam.com` | `student123` |

*(Aap naya account bhi register kar sakte hain)*

---

## 🚀 Setup & Run Instructions

### 1. Install Dependencies
```bash
pip install flask werkzeug
```

### 2. Database Initialize / Reset
```bash
python init_db.py
```

### 3. Run Application
```bash
python app.py
```

### 4. Open in Browser
```
http://127.0.0.1:5000
```
