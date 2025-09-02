#!/usr/bin/env python3
import os
import sys
import subprocess
import sqlite3

def setup():
    print("Setting up 3D Bioprinting Platform...")

    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8+ required")
        sys.exit(1)

    # Install requirements
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully")
    except:
        print("Error installing requirements")
        sys.exit(1)

    # Create directories
    os.makedirs("static/models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Initialize database
    conn = sqlite3.connect('bioprinting.db')
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS patient_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        patient_name TEXT NOT NULL,
        height REAL NOT NULL,
        weight REAL NOT NULL,
        age INTEGER NOT NULL,
        blood_group TEXT NOT NULL,
        medical_conditions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS generated_models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        organ_type TEXT NOT NULL,
        model_file_path TEXT NOT NULL,
        bioink_formula TEXT NOT NULL,
        material_requirements TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patient_data (id)
    )""")

    conn.commit()
    conn.close()

    print("Setup complete! Run: python app.py")

if __name__ == "__main__":
    setup()
