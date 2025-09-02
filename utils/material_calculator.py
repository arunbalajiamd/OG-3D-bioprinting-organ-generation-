class MaterialCalculator:
    def __init__(self):
        self.scaffold_materials = {
            'heart': {
                'pcl_fibers': {'density': 1.145, 'porosity': 0.85, 'fiber_diameter': 0.1},  # mm
                'collagen_matrix': {'density': 1.3, 'concentration': 0.05},
                'elastin_fibers': {'density': 1.2, 'concentration': 0.02},
                'conductive_nanoparticles': {'density': 5.2, 'concentration': 0.001}
            },
            'liver': {
                'pla_framework': {'density': 1.24, 'porosity': 0.80, 'layer_thickness': 0.2},
                'hepatocyte_matrix': {'density': 1.1, 'concentration': 0.08},
                'growth_factors': {'density': 1.0, 'concentration': 0.0005},
                'vascular_channels': {'material': 'pva', 'density': 1.19, 'diameter': 0.5}
            },
            'kidney': {
                'pga_scaffold': {'density': 1.53, 'porosity': 0.90, 'pore_size': 0.15},
                'nephron_matrix': {'density': 1.25, 'concentration': 0.06},
                'basement_membrane': {'density': 1.1, 'concentration': 0.03},
                'filtration_membrane': {'density': 1.4, 'thickness': 0.01}
            },
            'ear': {
                'cartilage_scaffold': {'density': 1.2, 'porosity': 0.75, 'elasticity': 'high'},
                'chondrocyte_matrix': {'density': 1.15, 'concentration': 0.07},
                'shape_memory_polymer': {'density': 1.05, 'concentration': 0.02},
                'surface_coating': {'density': 1.3, 'thickness': 0.005}
            }
        }

        self.biological_materials = {
            'growth_factors': {
                'vegf': {'molecular_weight': 38000, 'units_per_mg': 50000, 'cost_per_mg': 250},
                'bfgf': {'molecular_weight': 17800, 'units_per_mg': 100000, 'cost_per_mg': 180},
                'tgf_beta': {'molecular_weight': 25000, 'units_per_mg': 20000, 'cost_per_mg': 320},
                'pdgf': {'molecular_weight': 28000, 'units_per_mg': 30000, 'cost_per_mg': 290}
            },
            'extracellular_proteins': {
                'collagen_i': {'concentration_mg_ml': 5, 'cost_per_g': 45},
                'collagen_iv': {'concentration_mg_ml': 2, 'cost_per_g': 85},  
                'laminin': {'concentration_mg_ml': 1, 'cost_per_g': 120},
                'fibronectin': {'concentration_mg_ml': 0.5, 'cost_per_g': 95},
                'elastin': {'concentration_mg_ml': 3, 'cost_per_g': 65}
            },
            'cell_nutrients': {
                'glucose': {'concentration_mg_ml': 4.5, 'cost_per_kg': 2.5},
                'amino_acids': {'concentration_mg_ml': 0.8, 'cost_per_kg': 25},
                'vitamins': {'concentration_mg_ml': 0.1, 'cost_per_kg': 150},
                'minerals': {'concentration_mg_ml': 0.3, 'cost_per_kg': 8}
            }
        }

        # Standard pricing for common materials (USD)
        self.material_costs = {
            'alginate': 45.0,      # per kg
            'gelatin': 25.0,       # per kg
            'hyaluronic_acid': 280.0,  # per kg
            'collagen': 180.0,     # per kg
            'chitosan': 35.0,      # per kg
            'peg_diacrylate': 95.0,    # per kg
            'calcium_chloride': 15.0,   # per kg
            'pbs_medium': 8.0,     # per liter
            'pcl_fibers': 120.0,   # per kg
            'pla_framework': 85.0, # per kg
            'pga_scaffold': 150.0, # per kg
        }

    def calculate_materials(self, organ_type, bioink_volume):
        """Calculate all material requirements including bioink, scaffold, and biologics"""
        if organ_type not in self.scaffold_materials:
            raise ValueError(f"Unsupported organ type: {organ_type}")

        # Calculate scaffold materials
        scaffold_reqs = self.calculate_scaffold_materials(organ_type, bioink_volume)

        # Calculate biological materials
        biological_reqs = self.calculate_biological_materials(organ_type, bioink_volume)

        # Calculate post-processing materials
        post_processing = self.calculate_post_processing_materials(organ_type, bioink_volume)

        # Calculate total costs
        total_cost = self.calculate_total_cost(scaffold_reqs, biological_reqs, post_processing)

        return {
            'organ_type': organ_type,
            'bioink_volume_ml': bioink_volume,
            'scaffold_materials': scaffold_reqs,
            'biological_materials': biological_reqs,
            'post_processing': post_processing,
            'cost_breakdown': total_cost,
            'material_safety': self.get_safety_requirements(organ_type),
            'storage_requirements': self.get_storage_requirements()
        }

    def calculate_scaffold_materials(self, organ_type, volume):
        """Calculate scaffold material requirements"""
        scaffold_config = self.scaffold_materials[organ_type]
        materials = {}

        for material_name, properties in scaffold_config.items():
            if 'density' in properties and 'porosity' in properties:
                # Solid volume calculation considering porosity
                solid_fraction = 1 - properties['porosity']
                solid_volume = volume * solid_fraction * 0.3  # 30% of bioink volume for scaffold
                material_mass = solid_volume * properties['density']  # grams

                materials[material_name] = {
                    'mass_g': material_mass,
                    'volume_ml': solid_volume,
                    'properties': properties,
                    'cost_usd': material_mass * self.material_costs.get(material_name.split('_')[0], 50) / 1000
                }

            elif 'concentration' in properties:
                # Concentration-based materials
                material_mass = volume * properties['concentration'] * properties['density']
                materials[material_name] = {
                    'mass_g': material_mass,
                    'concentration': properties['concentration'],
                    'cost_usd': material_mass * self.material_costs.get(material_name.split('_')[0], 50) / 1000
                }

        return materials

    def calculate_biological_materials(self, organ_type, volume):
        """Calculate biological material requirements"""
        biological_materials = {}

        # Growth factors - organ specific
        if organ_type == 'heart':
            required_factors = ['vegf', 'bfgf', 'pdgf']
        elif organ_type == 'liver':
            required_factors = ['vegf', 'bfgf', 'tgf_beta']
        elif organ_type == 'kidney':
            required_factors = ['vegf', 'tgf_beta', 'pdgf']
        else:  # ear
            required_factors = ['tgf_beta', 'bfgf']

        for factor in required_factors:
            if factor in self.biological_materials['growth_factors']:
                factor_data = self.biological_materials['growth_factors'][factor]
                # Calculate required amount (typically 10-100 ng/ml)
                required_ng_ml = 50  # Average requirement
                total_ng = volume * required_ng_ml
                total_mg = total_ng / 1e6

                biological_materials[factor] = {
                    'amount_mg': total_mg,
                    'concentration_ng_ml': required_ng_ml,
                    'cost_usd': total_mg * factor_data['cost_per_mg'],
                    'molecular_weight': factor_data['molecular_weight']
                }

        # Extracellular proteins
        for protein, data in self.biological_materials['extracellular_proteins'].items():
            required_amount = volume * data['concentration_mg_ml'] / 1000  # Convert to grams
            biological_materials[protein] = {
                'amount_g': required_amount,
                'cost_usd': required_amount * data['cost_per_g'],
                'concentration_mg_ml': data['concentration_mg_ml']
            }

        # Cell nutrients
        for nutrient, data in self.biological_materials['cell_nutrients'].items():
            required_amount = volume * data['concentration_mg_ml'] / 1000  # Convert to grams
            biological_materials[nutrient] = {
                'amount_g': required_amount,
                'cost_usd': required_amount * data['cost_per_kg'] / 1000,
                'concentration_mg_ml': data['concentration_mg_ml']
            }

        return biological_materials

    def calculate_post_processing_materials(self, organ_type, volume):
        """Calculate materials needed for post-processing and maturation"""
        post_processing = {
            'culture_medium': {
                'volume_ml': volume * 5,  # 5x volume for culture
                'changes_per_week': 3,
                'culture_duration_weeks': 4,
                'cost_per_liter': 25.0
            },
            'antibiotics': {
                'penicillin_streptomycin': volume * 0.01,  # 1% of volume
                'cost_per_ml': 0.15
            },
            'maturation_factors': {
                'mechanical_stimulation': True,
                'electrical_stimulation': organ_type == 'heart',
                'flow_perfusion': organ_type in ['liver', 'kidney'],
                'estimated_cost': volume * 2.5  # $2.5 per ml for maturation
            },
            'quality_control': {
                'histology_staining': 150.0,
                'immunofluorescence': 200.0,
                'mechanical_testing': 300.0,
                'viability_assays': 100.0
            }
        }

        # Calculate culture medium total cost
        total_medium_volume = (post_processing['culture_medium']['volume_ml'] * 
                             post_processing['culture_medium']['changes_per_week'] * 
                             post_processing['culture_medium']['culture_duration_weeks'])

        post_processing['culture_medium']['total_cost'] = (total_medium_volume / 1000 * 
                                                        post_processing['culture_medium']['cost_per_liter'])

        return post_processing

    def calculate_total_cost(self, scaffold_reqs, biological_reqs, post_processing):
        """Calculate total cost breakdown"""
        costs = {
            'scaffold_materials': sum(mat.get('cost_usd', 0) for mat in scaffold_reqs.values()),
            'biological_materials': sum(mat.get('cost_usd', 0) for mat in biological_reqs.values()),
            'culture_medium': post_processing['culture_medium']['total_cost'],
            'antibiotics': (post_processing['antibiotics']['penicillin_streptomycin'] * 
                          post_processing['antibiotics']['cost_per_ml']),
            'maturation': post_processing['maturation_factors']['estimated_cost'],
            'quality_control': sum(post_processing['quality_control'].values()),
            'labor_estimate': 2500.0,  # Estimated labor cost
            'equipment_usage': 800.0   # Equipment depreciation and usage
        }

        costs['subtotal'] = sum(costs.values())
        costs['overhead_20_percent'] = costs['subtotal'] * 0.20
        costs['total_estimated_cost'] = costs['subtotal'] + costs['overhead_20_percent']

        return costs

    def get_safety_requirements(self, organ_type):
        """Get safety requirements for handling materials"""
        return {
            'biosafety_level': 'BSL-2',
            'ppe_required': ['gloves', 'lab_coat', 'safety_glasses', 'face_mask'],
            'ventilation': 'biosafety_cabinet_class_ii',
            'waste_disposal': 'biohazard_autoclave',
            'special_precautions': [
                'All work must be performed in sterile conditions',
                'Regular sterility testing required',
                'Temperature monitoring throughout process',
                'Documentation of all material lots and expiration dates'
            ]
        }

    def get_storage_requirements(self):
        """Get storage requirements for all materials"""
        return {
            'bioink_components': {
                'temperature': '2-8°C',
                'humidity': '<60%',
                'light_protection': True,
                'shelf_life': '6-24 months depending on component'
            },
            'biological_materials': {
                'temperature': '-20°C to -80°C',
                'aliquoting': 'recommended to avoid freeze-thaw cycles',
                'shelf_life': '12-36 months'
            },
            'scaffold_materials': {
                'temperature': 'room temperature',
                'humidity': '<30%',
                'protection': 'sealed containers with desiccant'
            },
            'finished_constructs': {
                'temperature': '37°C in incubator',
                'co2_concentration': '5%',
                'humidity': '95%',
                'medium_changes': 'every 2-3 days'
            }
        }

    def generate_material_list(self, material_data):
        """Generate a comprehensive material procurement list"""
        material_list = {
            'immediate_order': [],
            'advance_order': [],
            'custom_synthesis': [],
            'total_estimated_cost': material_data['cost_breakdown']['total_estimated_cost']
        }

        # Categorize materials by procurement timeline
        for category, items in material_data.items():
            if category in ['scaffold_materials', 'biological_materials']:
                for item_name, item_data in items.items():
                    item_info = {
                        'name': item_name.replace('_', ' ').title(),
                        'amount': item_data.get('mass_g', item_data.get('amount_g', item_data.get('amount_mg', 0))),
                        'unit': 'g' if 'mass_g' in item_data or 'amount_g' in item_data else 'mg',
                        'cost': item_data.get('cost_usd', 0),
                        'supplier': 'Standard biochemical supplier'
                    }

                    # Categorize by lead time
                    if 'growth_factor' in item_name or 'matrix' in item_name:
                        material_list['advance_order'].append(item_info)
                    elif 'custom' in item_name or 'specialized' in item_name:
                        material_list['custom_synthesis'].append(item_info)
                    else:
                        material_list['immediate_order'].append(item_info)

        return material_list
