import json
import psycopg2
import re
import os

DB_CONFIG = {
    "host": "localhost",
    "database": "farmacias_db",
    "user": "farmacia_user",
    "password": "SecurePass2024!",
    "port": "5432"
}

def clean_html_to_json(filepath):

    try:
        if not os.path.exists(filepath):
            print(f"Archivo no encontrado: {filepath}")
            return None
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Busca el patrón de arreglo JSON [ {...}, {...} ]
        match = re.search(r'\[.*\]', content)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception as e:
        print(f"Error al procesar el archivo HTML: {e}")
        return None

def setup_db(cur):

    print("Configurando tablas en PostgreSQL...")
    cur.execute("DROP TABLE IF EXISTS farmacias;")
    cur.execute("""
    CREATE TABLE farmacias (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(255),
        ciudad VARCHAR(100),
        direccion VARCHAR(255),
        telefonico VARCHAR(50),
        horario_apertura TIME,
        horario_cierre TIME,
        funcionamiento_dia VARCHAR(100),
        latitud DECIMAL(12, 9),
        longitud DECIMAL(12, 9),
        esta_activa BOOLEAN DEFAULT TRUE,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

def sync_data():


    file_path = "farmacias.html" 
    data = clean_html_to_json(file_path)
    
    if not data:
        print("No se encontraron datos válidos. Verifique que 'farmacias.html' exista.")
        return

    comunas_objetivo = ['CORONEL', 'LOTA', 'ARAUCO', 'CONCEPCION']
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Preparar la tabla
        setup_db(cur)

        print(f"Iniciando filtrado y carga para: {', '.join(comunas_objetivo)}...")
        count = 0
        
        for item in data:
            # Normalizar nombre de comuna para comparación
            comuna_nombre = str(item.get('comuna_nombre', '')).upper().strip()
            
            if comuna_nombre in comunas_objetivo:
                query = """
                INSERT INTO farmacias (
                    nombre, ciudad, direccion, telefonico, 
                    horario_apertura, horario_cierre, funcionamiento_dia,
                    latitud, longitud
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                
                lat = item.get('local_lat')
                lng = item.get('local_lng')

                values = (
                    item.get('local_nombre'),
                    comuna_nombre, 
                    item.get('local_direccion'),
                    item.get('local_telefono'),
                    item.get('funcionamiento_hora_apertura') or None,
                    item.get('funcionamiento_hora_cierre') or None,
                    item.get('funcionamiento_dia'),
                    float(lat) if lat and str(lat).strip() not in ["", "0"] else None,
                    float(lng) if lng and str(lng).strip() not in ["", "0"] else None
                )
                cur.execute(query, values)
                count += 1

        conn.commit()
        print(f"--- Sincronización Exitosa ---")
        print(f"Total de registros cargados: {count}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error crítico en la sincronización: {e}")

if __name__ == "__main__":
    sync_data()