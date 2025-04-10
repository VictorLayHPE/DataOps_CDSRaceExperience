# kafka_consumer_predictor.py
from flask import Flask, render_template, jsonify
import json
import pickle
from kafka import KafkaConsumer
import sys
import os
import time
import pandas as pd
time.sleep(15)  # Esperar 15 segundos antes de iniciar el consumidor

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.preprocessing import clean_data
from utils.extract_features import extract_features
from utils.required_columns import required_columns

print(required_columns)



# Cargar el modelo entrenado
model = pickle.load(open('model/pitstop_model.pkl', 'rb'))

# Configurar el consumidor de Kafka
consumer = KafkaConsumer(
    'f1-data',
    bootstrap_servers='kafka:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Configurar Flask
app = Flask(__name__)

# Variable global para almacenar los datos más recientes
latest_data = {
    "speed": "--",
    "fuel_level": "--",
    "tire_wear_rate": "--",
    "status": "Esperando datos..."
}

# Ruta principal para mostrar el dashboard
@app.route('/')
def dashboard():
    print("Accediendo al dashboard...")
    return render_template('dashboard.html', data=latest_data)

# Ruta para obtener los datos más recientes en formato JSON
@app.route('/data')
def get_data():
    return jsonify(latest_data)

# Función para consumir mensajes de Kafka y actualizar los datos
def consume_kafka():
    global latest_data
    for message in consumer:
        try:
            raw_data = message.value
            print("Datos recibidos de Kafka:", raw_data)  # Muestra los datos que recibes
            
            # Procesar los datos
            cleaned_data = clean_data(raw_data)
        
            # Filtrar y organizar las columnas para que coincidan con las esperadas por el modelo
            feature_names = required_columns()
            cleaned_data = cleaned_data[feature_names]
            
            # Verificar que las columnas requeridas estén presentes
            missing_columns = [col for col in feature_names if col not in cleaned_data.columns]
            if missing_columns:
                print(f"❌ Faltan las siguientes columnas: {missing_columns}. Saltando al siguiente mensaje...")
                continue

            prediction = model.predict(cleaned_data)[0]
            latest_data = {
                "speed": f"{raw_data['Corr Speed']} km/h",
                "fuel_level": f"{raw_data['Fuel Level']} L",
                "tire_wear_rate": f"{raw_data['AID Tire Wear Rate']} %",
                "status": "🔴 PARAR en boxes ahora" if prediction else "🟢 Continuar en pista"
            }

        except ValueError as e:
            print(f"❌ Error al procesar el mensaje: {e}. Saltando al siguiente mensaje...")
            continue
        except Exception as e:
            print(f"❌ Error inesperado: {e}. Saltando al siguiente mensaje...")
            continue


# Iniciar el consumidor de Kafka en un hilo separado
from threading import Thread
kafka_thread = Thread(target=consume_kafka, daemon=True)
kafka_thread.start()

# Ejecutar la aplicación Flask
if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    app.run(host='0.0.0.0', port=5000, debug=True)
    print("Servidor Flask iniciado en http://localhost:5000")