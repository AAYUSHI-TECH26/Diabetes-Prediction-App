"""
Diabetes Prediction System - Main Application
Features: User/Doctor Login, Prediction, PDF Reports, Doctor Verification
Dataset: Pima Indian Diabetes Dataset
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import sqlite3
import os
import hashlib
import json
from datetime import datetime
from model.predictor import DiabetesPredictor
from report_generator import generate_report

app = Flask(__name__)
app.secret_key = "diabetes_secret_key_2024"

DB_PATH = "database/diabetes_app.db"
predictor = DiabetesPredictor()

# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs("database", exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'patient',  -- 'patient' or 'doctor'
        doctor_id TEXT,                         -- unique doctor code
        approved INTEGER DEFAULT 1,            -- doctors need manual approval (demo: auto-approved)
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        patient_name TEXT,
        pregnancies REAL, glucose REAL, blood_pressure REAL,
        skin_thickness REAL, insulin REAL, bmi REAL,
        diabetes_pedigree REAL, age REAL,
        risk_score REAL, prediction INTEGER,
        risk_level TEXT, doctor_id INTEGER,
        doctor_verified INTEGER DEFAULT 0,
        doctor_notes TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_id) REFERENCES users(id)
    )""")

    # Demo doctor and patient accounts
    def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

    c.execute("INSERT OR IGNORE INTO users(name,email,password,role,doctor_id) VALUES(?,?,?,?,?)",
              ("Dr. Aryan Sharma", "doctor@demo.com", hash_pw("doctor123"), "doctor", "DOC001"))
    c.execute("INSERT OR IGNORE INTO users(name,email,password,role) VALUES(?,?,?,?)",
              ("Priya Mehta", "patient@demo.com", hash_pw("patient123"), "patient"))

    conn.commit()
    conn.close()

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ─────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        role = request.form.get("role","patient")
        doctor_code = request.form.get("doctor_code","").strip() if role=="doctor" else None

        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if existing:
            flash("Email already registered!", "danger")
            conn.close()
            return render_template("signup.html")

        conn.execute(
            "INSERT INTO users(name,email,password,role,doctor_id) VALUES(?,?,?,?,?)",
            (name, email, hash_password(password), role, doctor_code)
        )
        conn.commit()
        conn.close()
        flash("Account created! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, hash_password(password))
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))

# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    role = session["user_role"]
    uid = session["user_id"]

    if role == "doctor":
        # Doctor sees all pending/verified reports
        patients = conn.execute(
            "SELECT * FROM predictions ORDER BY created_at DESC"
        ).fetchall()
        pending = conn.execute(
            "SELECT COUNT(*) as cnt FROM predictions WHERE doctor_verified=0"
        ).fetchone()["cnt"]
        total = conn.execute("SELECT COUNT(*) as cnt FROM predictions").fetchone()["cnt"]
        high_risk = conn.execute(
            "SELECT COUNT(*) as cnt FROM predictions WHERE prediction=1"
        ).fetchone()["cnt"]
        conn.close()
        return render_template("doctor_dashboard.html",
                               patients=patients, pending=pending,
                               total=total, high_risk=high_risk)
    else:
        # Patient sees their own records
        records = conn.execute(
            "SELECT * FROM predictions WHERE patient_id=? ORDER BY created_at DESC", (uid,)
        ).fetchall()
        conn.close()
        return render_template("patient_dashboard.html", records=records)

# ─────────────────────────────────────────────
# PREDICTION
# ─────────────────────────────────────────────

@app.route("/predict", methods=["GET","POST"])
def predict():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            features = {
                "pregnancies":       float(request.form["pregnancies"]),
                "glucose":           float(request.form["glucose"]),
                "blood_pressure":    float(request.form["blood_pressure"]),
                "skin_thickness":    float(request.form["skin_thickness"]),
                "insulin":           float(request.form["insulin"]),
                "bmi":               float(request.form["bmi"]),
                "diabetes_pedigree": float(request.form["diabetes_pedigree"]),
                "age":               float(request.form["age"])
            }
        except ValueError:
            flash("Please fill all fields with valid numbers.", "danger")
            return render_template("predict.html")

        result = predictor.predict(features)
        features.update(result)

        conn = get_db()
        # Assign to first available doctor
        doctor = conn.execute("SELECT id FROM users WHERE role='doctor' LIMIT 1").fetchone()
        doctor_id = doctor["id"] if doctor else None

        conn.execute("""INSERT INTO predictions
            (patient_id, patient_name, pregnancies, glucose, blood_pressure,
             skin_thickness, insulin, bmi, diabetes_pedigree, age,
             risk_score, prediction, risk_level, doctor_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (session["user_id"], session["user_name"],
             features["pregnancies"], features["glucose"], features["blood_pressure"],
             features["skin_thickness"], features["insulin"], features["bmi"],
             features["diabetes_pedigree"], features["age"],
             result["risk_score"], result["prediction"],
             result["risk_level"], doctor_id))
        conn.commit()
        pred_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()

        return render_template("result.html", features=features, result=result, pred_id=pred_id)

    return render_template("predict.html")

# ─────────────────────────────────────────────
# DOCTOR VERIFICATION
# ─────────────────────────────────────────────

@app.route("/verify/<int:pred_id>", methods=["GET","POST"])
def verify(pred_id):
    if "user_id" not in session or session["user_role"] != "doctor":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db()
    record = conn.execute("SELECT * FROM predictions WHERE id=?", (pred_id,)).fetchone()

    if request.method == "POST":
        notes = request.form.get("notes","")
        conn.execute(
            "UPDATE predictions SET doctor_verified=1, doctor_notes=? WHERE id=?",
            (notes, pred_id)
        )
        conn.commit()
        conn.close()
        flash(f"Report #{pred_id} verified successfully!", "success")
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("verify.html", record=record)

# ─────────────────────────────────────────────
# PDF REPORT DOWNLOAD
# ─────────────────────────────────────────────

@app.route("/report/<int:pred_id>")
def download_report(pred_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    record = conn.execute("SELECT * FROM predictions WHERE id=?", (pred_id,)).fetchone()
    doctor = None
    if record["doctor_id"]:
        doctor = conn.execute(
            "SELECT name FROM users WHERE id=?", (record["doctor_id"],)
        ).fetchone()
    conn.close()

    if not record:
        flash("Record not found.", "danger")
        return redirect(url_for("dashboard"))

    doctor_name = doctor["name"] if doctor else "Pending"
    pdf_path = generate_report(dict(record), doctor_name)

    return send_file(pdf_path, as_attachment=True,
                     download_name=f"diabetes_report_{pred_id}.pdf")

# ─────────────────────────────────────────────
# MODEL INFO PAGE
# ─────────────────────────────────────────────

@app.route("/model-info")
def model_info():
    if "user_id" not in session:
        return redirect(url_for("login"))
    stats = predictor.get_model_stats()
    return render_template("model_info.html", stats=stats)

if __name__ == "__main__":
    init_db()
    predictor.train()
    print("\n" + "="*55)
    print("  🩺  Diabetes Prediction System Running!")
    print("  URL  →  http://127.0.0.1:5000")
    print("  Demo Doctor  →  doctor@demo.com / doctor123")
    print("  Demo Patient →  patient@demo.com / patient123")
    print("="*55 + "\n")
    app.run(debug=True)
