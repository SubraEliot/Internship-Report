# Mode Simulation - Samples Mock
"""
Version simulation du module samples.py pour tester sans matériel DAQ
"""
import numpy as np
import time

# Variables globales pour la simulation
_sim_pressure_base = 101325  # Pa
_sim_temperature_base = 298.15  # K
_sim_pitot_base = 1000  # Pa

def sample_pressure(para):
    """Simulation de l'échantillonnage de pression ambiante"""
    # Ajouter un peu de bruit réaliste
    noise = np.random.normal(0, 50)  # ±50 Pa de bruit
    return _sim_pressure_base + noise

def sample_temperature(para):
    """Simulation de l'échantillonnage de température"""
    # Variation lente de température avec bruit
    time_factor = time.time() % 3600  # Cycle de 1 heure
    temp_variation = 5 * np.sin(time_factor / 600)  # ±5K variation
    noise = np.random.normal(0, 0.5)  # ±0.5K de bruit
    return _sim_temperature_base + temp_variation + noise

def sample_pitot(para):
    """Simulation de l'échantillonnage du tube de Pitot"""
    # Simuler une pression différentielle basée sur une vitesse fictive
    # Relation : dp = 0.5 * rho * v²
    simulated_velocity = 10 + 5 * np.sin(time.time())  # Vitesse variable
    rho = 1.2  # kg/m³
    dp_ideal = 0.5 * rho * simulated_velocity**2
    
    # Ajouter du bruit et des effets non-linéaires
    noise = np.random.normal(0, 10)  # ±10 Pa de bruit
    return dp_ideal + noise

print("Mode simulation activé - Pas besoin de matériel DAQ !")
