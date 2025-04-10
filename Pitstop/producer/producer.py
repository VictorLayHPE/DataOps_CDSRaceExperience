import json
from kafka import KafkaProducer
import time
import pandas as pd
import sys
import os

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.parse_motec_csv import parse_motec_csv  # Usando la función de parseo
from utils.required_columns import required_columns

time.sleep(15)  # Esperar 5 segundos antes de iniciar el productor
# Configura el productor de Kafka
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Leer el CSV
df = pd.read_csv("data/datos_limpiados.csv")

# Asegurarse de que las columnas del DataFrame están correctas y contienen los datos esperados
features = required_columns()

# Verificar si todas las columnas requeridas están presentes
missing_columns = [col for col in features if col not in df.columns]
if missing_columns:
    print(f"Error: Faltan columnas en el CSV: {', '.join(missing_columns)}")
else:
    # Enviar los datos a Kafka
    for _, row in df.iterrows():
        message = {feature: row[feature] for feature in features}

        # Enviar el mensaje a Kafka
        producer.send('f1-data', value=message)
        print(f"✅ Mensaje enviado: {message}")
        
        # Controlar el tiempo entre los mensajes si es necesario
        time.sleep(1)

    # Asegurarse de que todos los mensajes hayan sido enviados
    producer.flush()
    print("✅ Todos los datos fueron enviados a Kafka.")
