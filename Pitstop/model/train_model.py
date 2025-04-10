import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import sys
import os

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.parse_motec_csv import parse_motec_csv
from utils.required_columns import required_columns

# Cargar datos
df = parse_motec_csv("data/1vs4.csv")
# Convierte las columnas relevantes a tipo numérico
columnas_a_convertir = required_columns()
for columna in columnas_a_convertir:
    df[columna] = pd.to_numeric(df[columna], errors='coerce')

# Rellena valores NaN con 0
df = df.fillna(0)

 # Agregar etiquetas con reglas simples
def evaluar_parada(row):
     condiciones = [
         row['Fuel Level'] < 5,  # Poco combustible
         row['Lap Time'] > 100,  # Ritmo lento
         max(
             row['Tire Temp Core FL'],
             row['Tire Temp Core FR'],
             row['Tire Temp Core RL'],
             row['Tire Temp Core RR']
         ) > 110,  # Sobrecalentamiento neumáticos
         row['AID Tire Wear Rate'] > 1.5,  # Desgaste elevado
         max(row['Brake Temp FL'], row['Brake Temp FR']) > 600,  # Frenos calientes
         row['Corr Speed'] < 150,  # Ritmo general bajo
         abs(row['Tire Temp Core FL'] - row['Tire Temp Core RL']) > 15  # Desbalance térmico
     ]
     return int(any(condiciones))

df["pitstop"] = df.apply(evaluar_parada, axis=1)

 # Guardar como CSV limpio para referencias futuras
df.to_csv("data/session_data.csv", index=False)

 # Entrenamiento
# Entrenar el modelo solo con las columnas seleccionadas
X = df[columnas_a_convertir]
y = df['pitstop']


model = RandomForestClassifier()
model.fit(X, y)

pickle.dump(model, open("model/pitstop_model.pkl", "wb"))
print("✅ Modelo entrenado con etiquetas heurísticas.")
