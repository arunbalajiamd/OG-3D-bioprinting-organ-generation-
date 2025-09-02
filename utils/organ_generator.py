import numpy as np
import trimesh
from scipy.spatial.distance import cdist
from scipy.spatial import ConvexHull
import math

class OrganGenerator:
    def __init__(self):
        self.organ_parameters = {
            'heart': {
                'base_volume': 310,  # ml for adult male
                'dimensions': {'length': 12, 'width': 8.5, 'height': 6},  # cm
                'scaling_factors': {'height': 0.7, 'weight': 0.3}
            },
            'liver': {
                'base_volume': 1400,  # ml for adult male
                'dimensions': {'length': 26, 'width': 15, 'height': 8},  # cm
                'scaling_factors': {'height': 0.8, 'weight': 0.2}
            },
            'kidney': {
                'base_volume': 150,  # ml for adult male (one kidney)
                'dimensions': {'length': 11, 'width': 6, 'height': 3},  # cm
                'scaling_factors': {'height': 0.6, 'weight': 0.4}
            },
            'ear': {
                'base_volume': 8,  # ml for adult male
                'dimensions': {'length': 6.5, 'width': 3.5, 'height': 2.5},  # cm
                'scaling_factors': {'height': 0.9, 'weight': 0.1}
            }
        }
    
    def calculate_organ_size(self, organ_type, height, weight, age):
        """Calculate patient-specific organ size based on anthropometric data"""
        if organ_type not in self.organ_parameters:
            raise ValueError(f"Unsupported organ type: {organ_type}")
        
        # CRITICAL FIX: Convert inputs to numeric types
        try:
            height = float(height)
            weight = float(weight)
            age = int(age)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid numeric input: height={height}, weight={weight}, age={age}. Error: {e}")
        
        params = self.organ_parameters[organ_type]
        
        # Reference values for scaling (70kg adult male, 175cm height)
        ref_height = 175  # cm
        ref_weight = 70   # kg
        ref_age = 35      # years
        
        # Height scaling factor
        height_factor = (height / ref_height) ** params['scaling_factors']['height']
        
        # Weight scaling factor
        weight_factor = (weight / ref_weight) ** params['scaling_factors']['weight']
        
        # Age factor (organs typically reduce in size with age after 30)
        if age > 30:
            age_factor = 1.0 - ((age - 30) * 0.002)  # 0.2% reduction per year after 30
        else:
            age_factor = 1.0
        
        # Combined scaling factor
        scale_factor = height_factor * weight_factor * age_factor
        
        # Calculate scaled dimensions
        scaled_volume = params['base_volume'] * scale_factor
        scaled_dimensions = {
            key: value * (scale_factor ** (1/3)) 
            for key, value in params['dimensions'].items()
        }
        
        return {
            'volume': scaled_volume,
            'dimensions': scaled_dimensions,
            'scale_factor': scale_factor
        }
    
    def generate_heart_mesh(self, dimensions):
        """Generate a simplified heart mesh using mathematical equations"""
        # Heart parametric equations
        def heart_function(u, v):
            x = 16 * np.sin(u)**3
            y = 13 * np.cos(u) - 5 * np.cos(2*u) - 2 * np.cos(3*u) - np.cos(4*u)
            z = v * 5  # Add depth
            return x, y, z
        
        # Generate heart surface
        u = np.linspace(0, 2*np.pi, 50)
        v = np.linspace(-1, 1, 20)
        U, V = np.meshgrid(u, v)
        
        X, Y, Z = heart_function(U.flatten(), V.flatten())
        
        # Scale to required dimensions
        scale_x = dimensions['width'] / 32
        scale_y = dimensions['length'] / 26
        scale_z = dimensions['height'] / 10
        
        X = X * scale_x
        Y = Y * scale_y
        Z = Z * scale_z
        
        # Create vertices
        vertices = np.column_stack((X, Y, Z))
        
        # Create triangular faces using Delaunay triangulation
        hull = ConvexHull(vertices)
        faces = hull.simplices
        
        return trimesh.Trimesh(vertices=vertices, faces=faces)
    
    def generate_liver_mesh(self, dimensions):
        """Generate a simplified liver mesh"""
        # Create an irregular ellipsoid for liver
        phi = np.linspace(0, np.pi, 30)
        theta = np.linspace(0, 2*np.pi, 40)
        PHI, THETA = np.meshgrid(phi, theta)
        
        # Irregular scaling for liver shape
        r = 1 + 0.3 * np.sin(3 * THETA) * np.sin(2 * PHI)
        
        X = r * np.sin(PHI) * np.cos(THETA) * dimensions['width'] / 2
        Y = r * np.sin(PHI) * np.sin(THETA) * dimensions['length'] / 2
        Z = r * np.cos(PHI) * dimensions['height'] / 2
        
        vertices = np.column_stack((X.flatten(), Y.flatten(), Z.flatten()))
        
        hull = ConvexHull(vertices)
        faces = hull.simplices
        
        return trimesh.Trimesh(vertices=vertices, faces=faces)
    
    def generate_kidney_mesh(self, dimensions):
        """Generate kidney bean-shaped mesh"""
        # Kidney bean parametric surface
        u = np.linspace(0, 2*np.pi, 40)
        v = np.linspace(0, np.pi, 30)
        U, V = np.meshgrid(u, v)
        
        # Bean shape with indentation
        r = 1 - 0.3 * np.cos(U)
        
        X = r * np.sin(V) * np.cos(U) * dimensions['width'] / 2
        Y = r * np.sin(V) * np.sin(U) * dimensions['length'] / 2
        Z = r * np.cos(V) * dimensions['height'] / 2
        
        vertices = np.column_stack((X.flatten(), Y.flatten(), Z.flatten()))
        
        hull = ConvexHull(vertices)
        faces = hull.simplices
        
        return trimesh.Trimesh(vertices=vertices, faces=faces)
    
    def generate_ear_mesh(self, dimensions):
        """Generate simplified ear mesh"""
        # Create ear-like curved surface
        u = np.linspace(0, 2*np.pi, 25)
        v = np.linspace(0, np.pi, 20)
        U, V = np.meshgrid(u, v)
        
        # Ear shape with curves and folds
        r = 1 + 0.5 * np.sin(2*U) * np.sin(V)
        
        X = r * np.sin(V) * np.cos(U) * dimensions['width'] / 2
        Y = r * np.sin(V) * np.sin(U) * dimensions['length'] / 2
        Z = (r * np.cos(V) + 0.3 * np.sin(3*U)) * dimensions['height'] / 2
        
        vertices = np.column_stack((X.flatten(), Y.flatten(), Z.flatten()))
        
        hull = ConvexHull(vertices)
        faces = hull.simplices
        
        return trimesh.Trimesh(vertices=vertices, faces=faces)
    
    def generate_organ(self, organ_type, height, weight, age, blood_group, special_requirements):
        """Generate patient-specific 3D organ model"""
        # Calculate organ size
        organ_data = self.calculate_organ_size(organ_type, height, weight, age)
        
        # Generate mesh based on organ type
        if organ_type == 'heart':
            mesh = self.generate_heart_mesh(organ_data['dimensions'])
        elif organ_type == 'liver':
            mesh = self.generate_liver_mesh(organ_data['dimensions'])
        elif organ_type == 'kidney':
            mesh = self.generate_kidney_mesh(organ_data['dimensions'])
        elif organ_type == 'ear':
            mesh = self.generate_ear_mesh(organ_data['dimensions'])
        else:
            raise ValueError(f"Unsupported organ type: {organ_type}")
        
        # Apply special requirements modifications
        if special_requirements:
            mesh = self.apply_special_requirements(mesh, special_requirements)
        
        return {
            'mesh': mesh,
            'volume': organ_data['volume'],
            'dimensions': organ_data['dimensions'],
            'scale_factor': organ_data['scale_factor'],
            'metadata': {
                'patient_height': height,
                'patient_weight': weight,
                'patient_age': age,
                'blood_group': blood_group,
                'special_requirements': special_requirements
            }
        }
    
    def apply_special_requirements(self, mesh, requirements):
        """Apply special modifications based on patient requirements"""
        # Simple modifications based on text requirements
        if 'enlarged' in requirements.lower():
            mesh = mesh.apply_scale(1.1)
        elif 'reduced' in requirements.lower():
            mesh = mesh.apply_scale(0.9)
        
        return mesh
    
    def save_stl(self, mesh, filepath):
        """Save mesh to STL file"""
        mesh.export(filepath)
        return filepath
