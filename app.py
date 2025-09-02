import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import json
from datetime import datetime
from utils.organ_generator import OrganGenerator
from utils.bioink_calculator import BioinkCalculator
from utils.material_calculator import MaterialCalculator

app = Flask(__name__)
app.secret_key = 'bioprinting-secret-key-2025'
app.config['UPLOAD_FOLDER'] = 'static/models'

# Create directories if they don't exist
os.makedirs('static/models', exist_ok=True)
os.makedirs('utils', exist_ok=True)

# Database initialization
def init_db():
    conn = sqlite3.connect('bioprinting.db')
    c = conn.cursor()
    
    # Users table
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # Patient data table
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
    
    # Generated models table
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

@app.before_request
def create_tables():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('bioprinting.db')
        c = conn.cursor()
        
        # Check if user exists
        c.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if c.fetchone():
            flash('Username or email already exists')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        c.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                  (username, email, password_hash))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('bioprinting.db')
        c = conn.cursor()
        c.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('bioprinting.db')
    c = conn.cursor()
    c.execute('SELECT * FROM patient_data WHERE user_id = ? ORDER BY created_at DESC', 
              (session['user_id'],))
    patients = c.fetchall()
    conn.close()
    
    return render_template('dashboard.html', patients=patients)

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        age = int(request.form['age'])
        blood_group = request.form['blood_group']
        medical_conditions = request.form['medical_conditions']
        
        conn = sqlite3.connect('bioprinting.db')
        c = conn.cursor()
        c.execute("""INSERT INTO patient_data 
                     (user_id, patient_name, height, weight, age, blood_group, medical_conditions)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (session['user_id'], patient_name, height, weight, age, blood_group, medical_conditions))
        conn.commit()
        conn.close()
        
        flash('Patient data added successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('add_patient.html')

@app.route('/generate_organ/<int:patient_id>')
def generate_organ_form(patient_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('bioprinting.db')
    c = conn.cursor()
    c.execute('SELECT * FROM patient_data WHERE id = ? AND user_id = ?', 
              (patient_id, session['user_id']))
    patient = c.fetchone()
    conn.close()
    
    if not patient:
        flash('Patient not found')
        return redirect(url_for('dashboard'))
    
    return render_template('generate_organ.html', patient=patient)

@app.route('/process_organ_generation', methods=['POST'])
def process_organ_generation():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        patient_id = request.form['patient_id']
        organ_type = request.form['organ_type']
        special_requirements = request.form.get('special_requirements', '')
        
        # Get patient data
        conn = sqlite3.connect('bioprinting.db')
        c = conn.cursor()
        c.execute('SELECT * FROM patient_data WHERE id = ?', (patient_id,))
        patient = c.fetchone()
        
        if not patient:
            flash('Patient not found')
            return redirect(url_for('dashboard'))
        
        # Convert patient data to proper numeric types
        height = float(patient[2])
        weight = float(patient[3])
        age = int(patient[4])
        
        print(f"Processing organ generation: {organ_type} for patient {patient[2]}")
        print(f"Patient data: height={height}, weight={weight}, age={age}")
        
        # Generate 3D organ model
        organ_gen = OrganGenerator()
        model_data = organ_gen.generate_organ(
            organ_type=organ_type,
            height=height,
            weight=weight,
            age=age,
            blood_group=patient[5],
            special_requirements=special_requirements
        )
        
        print(f"Model generated successfully. Volume: {model_data['volume']}")
        
        # Calculate bioink requirements
        bioink_calc = BioinkCalculator()
        bioink_formula = bioink_calc.calculate_bioink(
            organ_type=organ_type,
            organ_volume=model_data['volume'],
            patient_weight=weight
        )
        
        # Calculate material requirements
        material_calc = MaterialCalculator()
        material_requirements = material_calc.calculate_materials(
            organ_type=organ_type,
            bioink_volume=bioink_formula['total_volume']
        )
        
        # Save to database
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_file_path = f"models/{organ_type}_{patient_id}_{timestamp}.stl"
        
        c.execute("""INSERT INTO generated_models 
                     (patient_id, organ_type, model_file_path, bioink_formula, material_requirements)
                     VALUES (?, ?, ?, ?, ?)""",
                  (patient_id, organ_type, model_file_path, 
                   json.dumps(bioink_formula), json.dumps(material_requirements)))
        model_id = c.lastrowid
        conn.commit()
        conn.close()
        
        # Save STL file
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{organ_type}_{patient_id}_{timestamp}.stl")
        organ_gen.save_stl(model_data['mesh'], full_path)
        
        print(f"STL file saved to: {full_path}")
        flash(f'3D organ model generated successfully! Model ID: {model_id}')
        
        return redirect(url_for('view_model', model_id=model_id))
        
    except Exception as e:
        print(f"Error in process_organ_generation: {e}")
        flash(f'Error generating model: {str(e)}')
        return redirect(url_for('dashboard'))

@app.route('/view_model/<int:model_id>')
def view_model(model_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('bioprinting.db')
    c = conn.cursor()
    c.execute("""SELECT gm.*, pd.patient_name, pd.height, pd.weight, pd.age, pd.blood_group
                 FROM generated_models gm
                 JOIN patient_data pd ON gm.patient_id = pd.id
                 WHERE gm.id = ? AND pd.user_id = ?""", (model_id, session['user_id']))
    model = c.fetchone()
    conn.close()
    
    if not model:
        flash('Model not found')
        return redirect(url_for('dashboard'))
    
    bioink_formula = json.loads(model[4])
    material_requirements = json.loads(model[5])
    
    return render_template('view_model.html', model=model, 
                         bioink_formula=bioink_formula, 
                         material_requirements=material_requirements)

@app.route('/download_model/<int:model_id>')
def download_model(model_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('bioprinting.db')
    c = conn.cursor()
    c.execute("""SELECT gm.model_file_path, pd.patient_name, gm.organ_type
                 FROM generated_models gm
                 JOIN patient_data pd ON gm.patient_id = pd.id
                 WHERE gm.id = ? AND pd.user_id = ?""", (model_id, session['user_id']))
    model = c.fetchone()
    conn.close()
    
    if not model:
        flash('Model not found')
        return redirect(url_for('dashboard'))
    
    file_path = os.path.join('static', model[0])
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, 
                        download_name=f"{model[1]}_{model[2]}.stl")
    else:
        flash('Model file not found')
        return redirect(url_for('dashboard'))

@app.route('/api/organ_types')
def api_organ_types():
    return jsonify({
        'heart': 'Human Heart',
        'liver': 'Human Liver',
        'kidney': 'Human Kidney',
        'ear': 'Human Ear'
    })

if __name__ == '__main__':
    init_db()  # Initialize database on startup
    app.run(debug=True)
