import pandas as pd

def parse_motec_csv(file_path):
    # Leer el archivo original línea por línea
    with open(file_path, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    # Eliminar las primeras 13 filas de metadatos
    lineas = lineas[13:]  # Elimina las primeras 13 filas (ajusta este número según lo que necesites)

    lineas_limpias = []
    for linea in lineas:
        # Paso 1: Corregir campos que empiecen mal, por ejemplo: "0 → ""0""
        if linea.startswith('"') and not linea.startswith('""'):
            linea = '"' + linea

        # Paso 2: Dentro de los campos (entre comillas dobles), cambiar las comas por puntos decimales
        resultado = ""
        dentro_campo = True
        i = 0
        while i < len(linea):
            char = linea[i]
            #Cuando encontramos una comilla doble, alternamos el estado de "dentro_campo"
            if char == '"' and i + 1 < len(linea) and linea[i + 1] == '"':
                dentro_campo = not dentro_campo
                resultado += '""'
                i += 1
            # Si estamos dentro de un campo y encontramos una coma, la cambiamos por un punto
            elif char == ',' and dentro_campo:
                resultado += '.'
            else:
                resultado += char
            i += 1

        # Paso 3: Eliminar todas las comillas dobles que quedaron en el archivo
        resultado = resultado.replace('"', '')
        lineas_limpias.append(resultado.strip())

    # Guardar el resultado limpio como un nuevo CSV
    with open("datos_limpiados.csv", "w", encoding="utf-8") as f:
        for linea in lineas_limpias:
            f.write(linea + "\n")

    # Leer el nuevo CSV procesado
    df = pd.read_csv("datos_limpiados.csv", skiprows=[1])

    # Rellenar NaNs y limpiar nombres de columnas
    df = df.fillna(0)
    df.columns = df.columns.str.strip()

    return df
