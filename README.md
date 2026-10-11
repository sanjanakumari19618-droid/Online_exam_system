# Online Exam System 📝

Flask aur SQLite se bana hua ek simple Online Exam System.

## Features
- User Register / Login / Logout
- Password Hashing (secure)
- DB se dynamic exam questions
- Automatic scoring (score, percentage, pass/fail)
- Exam history / results
- Responsive styled UI

## Setup & Run

### 1. Python install karo (agar nahi hai)
[python.org](https://python.org) se download karo.

### 2. Dependencies install karo
```bash
pip install flask werkzeug
```

### 3. Database initialize karo (sirf pehli baar)
```bash
python init_db.py
```

### 4. App start karo
```bash
python app.py
```

### 5. Browser mein kholo
```
http://127.0.0.1:5000
```

## Tech Stack
- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS (Jinja2 templates)
