import pandas as pd

from utils.required_columns import required_columns

def clean_data(data):
     # Convierte el raw_data a un DataFrame (si aún no lo es)
    df = pd.DataFrame([data])  # Suponiendo que raw_data es un diccionario
    
    # Asegúrate de que las columnas requeridas sean numéricas
    columnas_a_convertir = required_columns()
    for columna in columnas_a_convertir:
        df[columna] = pd.to_numeric(df[columna], errors='coerce')  # Convierte a numérico y reemplaza errores con NaN

    # Rellena valores NaN con 0
    df = df.fillna(0)
    
    return df
    
