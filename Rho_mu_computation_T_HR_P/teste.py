import pandas as pd

# Chemin vers le fichier CSV
file_path = "dataexport_20250609T110413.csv"

# Lire le CSV en sautant les 5 premières lignes de métadonnées
df = pd.read_csv(file_path, skiprows=5)

# Renommer les colonnes pour plus de clarté
df.columns = ['datetime', 'temperature', 'humidity', 'pressure']

# Convertir les colonnes dans le bon format
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')
df['pressure'] = pd.to_numeric(df['pressure'], errors='coerce')

# Supprimer les lignes avec des valeurs manquantes
df = df.dropna()

# Extraire les données dans des listes
dates = df['datetime'].tolist()
temperatures = df['temperature'].tolist()
humidites = df['humidity'].tolist()
pressions = df['pressure'].tolist()

# Afficher quelques exemples
print("Dates :", dates[:3])
print("Températures :", temperatures[:3])
print("Humidité :", humidites[:3])
print("Pression :", pressions[:3])
