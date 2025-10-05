# Mode Simulation - Tunnels Interaction Mock
"""
Version simulation du module tunnels_interaction.py pour tester sans matériel DAQ
"""
import time

# Variables globales pour traquer les commandes
_last_tunnel_command = 0
_last_range_command = 0
_command_log = []

def write_tunnel(value, para):
    """Simulation de l'écriture vers le tunnel"""
    global _last_tunnel_command, _command_log
    
    _last_tunnel_command = value
    timestamp = time.strftime("%H:%M:%S")
    
    # Log de la commande
    mode_str = "Big Tunnel" if para["mode"] == 1 else "Small Tunnel"
    log_entry = f"[{timestamp}] {mode_str}: Tunnel command = {value:.3f}V"
    _command_log.append(log_entry)
    
    # Garder seulement les 50 dernières commandes
    if len(_command_log) > 50:
        _command_log.pop(0)
    
    print(f"SIM: {log_entry}")
    return

def set_range_big_tunnel(value):
    """Simulation du réglage de gamme pour le grand tunnel"""
    global _last_range_command, _command_log
    
    _last_range_command = value
    timestamp = time.strftime("%H:%M:%S")
    
    log_entry = f"[{timestamp}] Big Tunnel Range: {value}V"
    _command_log.append(log_entry)
    
    if len(_command_log) > 50:
        _command_log.pop(0)
    
    print(f"SIM: {log_entry}")

def get_simulation_status():
    """Fonction utilitaire pour obtenir l'état de la simulation"""
    return {
        "last_tunnel_command": _last_tunnel_command,
        "last_range_command": _last_range_command,
        "recent_commands": _command_log[-10:] if _command_log else []
    }

print("Mode simulation activé - Commandes tunnel simulées !")
