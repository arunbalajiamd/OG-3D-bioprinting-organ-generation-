import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bioprinting-secret-key-2025'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///bioprinting.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/models'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Bioprinting specific settings
    SUPPORTED_ORGANS = ['heart', 'liver', 'kidney', 'ear']
    DEFAULT_CELL_DENSITY = 20e6  # cells/ml
    MAX_ORGAN_VOLUME = 2000  # ml
    MIN_ORGAN_VOLUME = 1  # ml

    # Material costs (USD per kg)
    MATERIAL_COSTS = {
        'alginate': 45.0,
        'gelatin': 25.0,
        'hyaluronic_acid': 280.0,
        'collagen': 180.0,
        'chitosan': 35.0
    }
