import math

class BioinkCalculator:
    def __init__(self):
        self.bioink_formulations = {
            'heart': {
                'base_formulation': {
                    'alginate': 0.02,  # 2% w/v
                    'gelatin': 0.05,   # 5% w/v
                    'hyaluronic_acid': 0.01,  # 1% w/v
                    'collagen': 0.03,  # 3% w/v
                    'fibrinogen': 0.002,  # 0.2% w/v
                },
                'crosslinking_agents': {
                    'calcium_chloride': 0.001,  # 0.1% w/v
                    'thrombin': 0.0001,  # 0.01% w/v
                },
                'cell_density': 20e6,  # cells/ml
                'printing_viscosity': 1500,  # mPa·s
            },
            'liver': {
                'base_formulation': {
                    'alginate': 0.015,  # 1.5% w/v
                    'gelatin': 0.06,    # 6% w/v
                    'hyaluronic_acid': 0.008,  # 0.8% w/v
                    'chitosan': 0.01,   # 1% w/v
                    'decellularized_ecm': 0.02,  # 2% w/v
                },
                'crosslinking_agents': {
                    'calcium_chloride': 0.0008,  # 0.08% w/v
                    'genipin': 0.0002,  # 0.02% w/v
                },
                'cell_density': 15e6,  # cells/ml
                'printing_viscosity': 1200,  # mPa·s
            },
            'kidney': {
                'base_formulation': {
                    'alginate': 0.025,  # 2.5% w/v
                    'gelatin': 0.04,    # 4% w/v
                    'hyaluronic_acid': 0.012,  # 1.2% w/v
                    'peg_diacrylate': 0.015,  # 1.5% w/v
                    'laminin': 0.001,   # 0.1% w/v
                },
                'crosslinking_agents': {
                    'calcium_chloride': 0.0012,  # 0.12% w/v
                    'photoinitiator': 0.0001,  # 0.01% w/v
                },
                'cell_density': 25e6,  # cells/ml
                'printing_viscosity': 1800,  # mPa·s
            },
            'ear': {
                'base_formulation': {
                    'alginate': 0.018,  # 1.8% w/v
                    'gelatin': 0.045,   # 4.5% w/v
                    'hyaluronic_acid': 0.006,  # 0.6% w/v
                    'chondroitin_sulfate': 0.008,  # 0.8% w/v
                    'agarose': 0.005,   # 0.5% w/v
                },
                'crosslinking_agents': {
                    'calcium_chloride': 0.0009,  # 0.09% w/v
                },
                'cell_density': 30e6,  # cells/ml
                'printing_viscosity': 2000,  # mPa·s
            }
        }

        # Material densities (g/ml)
        self.material_densities = {
            'alginate': 1.6,
            'gelatin': 1.27,
            'hyaluronic_acid': 1.2,
            'collagen': 1.3,
            'fibrinogen': 1.4,
            'chitosan': 1.35,
            'decellularized_ecm': 1.1,
            'peg_diacrylate': 1.12,
            'laminin': 1.2,
            'chondroitin_sulfate': 1.25,
            'agarose': 1.02,
            'calcium_chloride': 2.15,
            'thrombin': 1.3,
            'genipin': 1.27,
            'photoinitiator': 1.1
        }

    def calculate_bioink(self, organ_type, organ_volume, patient_weight):
        """Calculate bioink formulation based on organ specifications"""
        if organ_type not in self.bioink_formulations:
            raise ValueError(f"Unsupported organ type: {organ_type}")

        formulation = self.bioink_formulations[organ_type]

        # Account for printing waste and multiple attempts (typically 20-30% extra)
        waste_factor = 1.25
        total_volume = organ_volume * waste_factor  # ml

        # Calculate individual component volumes and masses
        components = {}
        total_solids_volume = 0

        # Base formulation components
        for component, concentration in formulation['base_formulation'].items():
            component_volume = total_volume * concentration  # ml
            component_mass = component_volume * self.material_densities[component]  # g
            components[component] = {
                'concentration': concentration,
                'volume_ml': component_volume,
                'mass_g': component_mass
            }
            total_solids_volume += component_volume

        # Crosslinking agents
        for agent, concentration in formulation['crosslinking_agents'].items():
            agent_volume = total_volume * concentration  # ml
            agent_mass = agent_volume * self.material_densities[agent]  # g
            components[agent] = {
                'concentration': concentration,
                'volume_ml': agent_volume,
                'mass_g': agent_mass
            }
            total_solids_volume += agent_volume

        # Calculate solvent (usually PBS or culture medium) volume
        solvent_volume = total_volume - total_solids_volume
        components['pbs_medium'] = {
            'concentration': solvent_volume / total_volume,
            'volume_ml': solvent_volume,
            'mass_g': solvent_volume * 1.0  # assuming density of water
        }

        # Patient-specific adjustments based on weight
        patient_adjustment_factor = self.calculate_patient_adjustment(patient_weight)

        # Adjust cell density based on patient weight
        adjusted_cell_density = formulation['cell_density'] * patient_adjustment_factor

        return {
            'organ_type': organ_type,
            'total_volume': total_volume,
            'components': components,
            'cell_density': adjusted_cell_density,
            'printing_viscosity': formulation['printing_viscosity'],
            'patient_weight': patient_weight,
            'adjustment_factor': patient_adjustment_factor,
            'estimated_printing_time': self.estimate_printing_time(total_volume, organ_type),
            'storage_temperature': self.get_storage_temperature(organ_type),
            'shelf_life_hours': self.get_shelf_life(organ_type)
        }

    def calculate_patient_adjustment(self, patient_weight):
        """Calculate adjustment factor based on patient weight"""
        # Reference weight: 70kg
        reference_weight = 70

        # Logarithmic scaling to avoid extreme adjustments
        if patient_weight > 0:
            adjustment = 0.8 + 0.4 * math.log(patient_weight / reference_weight) / math.log(2)
            # Clamp between 0.5 and 1.5
            return max(0.5, min(1.5, adjustment))
        else:
            return 1.0

    def estimate_printing_time(self, volume, organ_type):
        """Estimate printing time based on volume and complexity"""
        # Base printing rates (ml/hour) for different organs
        printing_rates = {
            'heart': 8,    # Complex geometry, slower printing
            'liver': 12,   # Medium complexity
            'kidney': 10,  # Medium-high complexity
            'ear': 15      # Simpler geometry, faster printing  
        }

        rate = printing_rates.get(organ_type, 10)
        estimated_hours = volume / rate

        return {
            'hours': estimated_hours,
            'minutes': estimated_hours * 60,
            'rate_ml_per_hour': rate
        }

    def get_storage_temperature(self, organ_type):
        """Get recommended storage temperature for bioink"""
        # Most bioinks require cold storage
        return {
            'temperature_celsius': 4,
            'temperature_fahrenheit': 39.2,
            'notes': 'Store in refrigerator, use within recommended shelf life'
        }

    def get_shelf_life(self, organ_type):
        """Get shelf life of prepared bioink in hours"""
        shelf_lives = {
            'heart': 24,   # Fibrinogen-based formulations are less stable
            'liver': 48,   # More stable formulation
            'kidney': 36,  # Medium stability
            'ear': 72      # Most stable formulation
        }
        return shelf_lives.get(organ_type, 24)

    def generate_preparation_protocol(self, bioink_data):
        """Generate step-by-step preparation protocol"""
        protocol = [
            "1. Pre-cool all solutions to 4°C",
            "2. Prepare sterile PBS medium in biosafety cabinet",
            "3. Dissolve polymers in the following order:"
        ]

        # Sort components by dissolution order (largest molecules first)
        dissolution_order = ['gelatin', 'alginate', 'hyaluronic_acid', 'collagen', 
                           'chitosan', 'decellularized_ecm', 'peg_diacrylate', 
                           'chondroitin_sulfate', 'agarose']

        step = 4
        for component in dissolution_order:
            if component in bioink_data['components']:
                comp_data = bioink_data['components'][component]
                protocol.append(f"{step}. Add {comp_data['mass_g']:.3f}g {component.replace('_', ' ').title()}")
                protocol.append(f"   Mix at 37°C for 30 minutes until fully dissolved")
                step += 1

        protocol.extend([
            f"{step}. Cool solution to room temperature",
            f"{step+1}. Add crosslinking agents just before printing:",
        ])

        step += 2
        for agent in bioink_data['components'].keys():
            if 'calcium' in agent or 'thrombin' in agent or 'genipin' in agent or 'photoinitiator' in agent:
                comp_data = bioink_data['components'][agent]
                protocol.append(f"   - {comp_data['mass_g']:.4f}g {agent.replace('_', ' ').title()}")

        protocol.extend([
            f"{step}. Filter sterilize through 0.22μm filter",
            f"{step+1}. Load into bioprinter cartridge",
            f"{step+2}. Begin printing within 30 minutes of preparation"
        ])

        return protocol
