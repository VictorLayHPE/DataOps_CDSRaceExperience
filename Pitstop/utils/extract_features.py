from utils import required_columns


def extract_features(df):
    print("Columnas del DataFrame:", df.columns)  # Esto te ayudará a ver las columnas disponibles
    
    required_columns_list = required_columns()
    
    # Verificar que todas las columnas requeridas estén presentes
    missing_columns = [col for col in required_columns_list if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Faltan las siguientes columnas: {', '.join(missing_columns)}")
    
    return [df[col].values[0] for col in required_columns_list]
