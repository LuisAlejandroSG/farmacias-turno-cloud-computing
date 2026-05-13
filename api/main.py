from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, time
import requests

app = FastAPI(
    title="API Farmacias de Turno",
    description="API para consultar y gestionar farmacias de turno (Coronel, Lota, Arauco, Concepción)",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Farmacia(BaseModel):
    id: int
    nombre: str
    ciudad: str
    direccion: Optional[str]
    telefonico: Optional[str]
    horario_apertura: Optional[time]
    horario_cierre: Optional[time]
    funcionamiento_dia: Optional[str]
    latitud: Optional[float]
    longitud: Optional[float]
    esta_activa: bool

class FarmaciaCreate(BaseModel):
    nombre: str
    ciudad: str
    direccion: str
    telefonico: Optional[str] = None
    horario_apertura: Optional[str] = "09:00"
    horario_cierre: Optional[str] = "21:00"
    funcionamiento_dia: Optional[str] = "lunes a domingo"
    latitud: Optional[float] = None
    longitud: Optional[float] = None

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        print(f"Error conectando a BD: {e}")
        raise HTTPException(status_code=500, detail="Error de conexión con el motor de base de datos")


@app.get("/")
async def root():
    return {
        "mensaje": "API Farmacias de Turno v1.1 - FastAPI",
        "estado": "operativo",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/farmacias", response_model=List[Farmacia])
async def obtener_farmacias(
    ciudad: Optional[str] = Query(None),
    activas_solo: bool = Query(True)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = "SELECT * FROM farmacias WHERE 1=1"
        params = []
        
        if activas_solo:
            query += " AND esta_activa = TRUE"
        if ciudad:
            query += " AND ciudad = %s"
            params.append(ciudad.upper())
            
        query += " ORDER BY id DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/farmacias", response_model=Farmacia)
async def crear_farmacia(farmacia: FarmaciaCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            INSERT INTO farmacias (
                nombre, ciudad, direccion, telefonico, 
                horario_apertura, horario_cierre, funcionamiento_dia,
                latitud, longitud
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
        """
        
        cursor.execute(query, (
            farmacia.nombre,
            farmacia.ciudad.upper(),
            farmacia.direccion,
            farmacia.telefonico,
            farmacia.horario_apertura,
            farmacia.horario_cierre,
            farmacia.funcionamiento_dia,
            farmacia.latitud,
            farmacia.longitud
        ))
        
        nueva = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return nueva
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar farmacia: {str(e)}")

@app.post("/api/update-data")
async def update_database():
    url = "https://midas.minsal.cl/farmacia_v2/WS/getLocalesTurnos.php"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise Exception("No se pudo conectar con el servidor ministerial")
            
        all_data = response.json()
        ciudades_objetivo = ["CORONEL", "LOTA", "ARAUCO", "CONCEPCION"]
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("TRUNCATE TABLE farmacias RESTART IDENTITY CASCADE;")
        
        query = """
            INSERT INTO farmacias (
                nombre, ciudad, direccion, telefonico, 
                horario_apertura, horario_cierre, funcionamiento_dia,
                latitud, longitud
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        count = 0
        for f in all_data:
            if f['comuna_nombre'].upper() in ciudades_objetivo:
                cur.execute(query, (
                    f['local_nombre'],
                    f['comuna_nombre'].upper(),
                    f['local_direccion'],
                    f['local_telefono'],
                    f['funcionamiento_hora_apertura'],
                    f['funcionamiento_hora_cierre'],
                    f['funcionamiento_dia'],
                    float(f['local_lat']) if f['local_lat'] else None,
                    float(f['local_lng']) if f['local_lng'] else None
                ))
                count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {"status": "success", "actualizados": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo en ETL: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)