# 3D Bioprinting Platform

A comprehensive web-based platform for generating patient-specific 3D organ models with automated bioink calculations and professional STL exports.

## Features

### 🫀 Organ Modeling
- **Heart**: Cardiac tissue engineering with specialized bioink formulations
- **Liver**: Hepatic tissue constructs for regenerative medicine  
- **Kidney**: Renal tissue constructs with filtration capabilities
- **Ear**: Auricular cartilage constructs for reconstructive surgery

### 🧪 Bioink Calculations
- Patient-specific organ scaling based on height, weight, and age
- Automated bioink component calculations
- Organ-specific formulations with optimal concentrations
- Material requirement analysis with cost estimation

### 🏥 Patient Management
- Secure user authentication and registration
- Patient database with medical history
- Multiple organ models per patient
- Progress tracking and model history

### 📊 Professional Outputs
- High-quality STL file generation
- Detailed bioink formulation reports
- Material procurement lists
- Cost breakdown analysis
- Preparation protocols

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup Instructions

1. **Create and activate virtual environment:**
   ```bash
   python -m venv bioprinting_env
   bioprinting_env\Scripts\activate  # Windows
   source bioprinting_env/bin/activate  # macOS/Linux
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run setup script:**
   ```bash
   python setup.py
   ```

4. **Start the application:**
   ```bash
   python app.py
   ```

5. **Open browser to:**
   ```
   http://localhost:5000
   ```

## Usage Guide

1. **Register** a new account
2. **Add patient data** with measurements
3. **Select organ type** to generate
4. **Download STL** and bioink formulation
5. **3D print** your organ model

## Technical Stack

- **Backend**: Flask, SQLite, Trimesh, NumPy/SciPy
- **Frontend**: Bootstrap 5, Three.js, Custom CSS/JS
- **3D Modeling**: Patient-specific scaling algorithms
- **Bioink**: Research-based formulations

## File Structure

```
3D_Bioprinting_App/
├── app.py                   # Main Flask application
├── config.py               # Configuration
├── requirements.txt        # Dependencies
├── templates/              # HTML templates
├── static/                 # CSS, JS, models
└── utils/                  # Core modules
```

## Safety & Compliance

- BSL-2 laboratory conditions required
- Personal protective equipment mandatory
- Sterile technique throughout process
- Quality control protocols included

## License

Research and educational use. Cite appropriately in publications.
