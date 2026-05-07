from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

# ============ CONFIGURACIÓN ============
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://farmacia_user:SecurePass2024!@postgres:5432/farmacias_db")

app = FastAPI(
    title="API Farmacias de Turno",
    description="API para consultar farmacias de turno en Coronel, Lota y Arauco",
    version="1.0.0"
)

# CORS para permitir solicitudes desde otras instancias
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ MODELOS ============
class Farmacia(BaseModel):
    id: int
    nombre: str
    ciudad: str
    direccion: Optional[str]
    telefonico: Optional[str]
    horario_apertura: Optional[str]
    horario_cierre: Optional[str]
    domingo_turno: bool
    esta_activa: bool

class FarmaciaCreate(BaseModel):
    nombre: str
    ciudad: str
    direccion: Optional[str] = None
    telefonico: Optional[str] = None
    horario_apertura: Optional[str] = None
    horario_cierre: Optional[str] = None
    domingo_turno: bool = False

# ============ FUNCIONES DE BASE DE DATOS ============
def get_db_connection():
    """Conectar a PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        print(f"Error conectando a BD: {e}")
        raise HTTPException(status_code=500, detail="Error conectando a base de datos")

# ============ RUTAS ============
@app.get("/")
async def root():
    """Endpoint raíz - verificar que la API está activa"""
    return {
        "mensaje": "API Farmacias de Turno v1.0",
        "estado": "operativo",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check para verificar conectividad con BD"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/farmacias", response_model=List[Farmacia])
async def obtener_farmacias(
    ciudad: Optional[str] = Query(None, description="Filtrar por ciudad"),
    turno_domingo: Optional[bool] = Query(None, description="Filtrar por turno domingo"),
    activas_solo: bool = Query(True, description="Mostrar solo farmacias activas")
):
    """
    Obtener lista de farmacias con filtros opcionales
    
    Parámetros:
    - ciudad: Coronel, Lota, Arauco (opcional)
    - turno_domingo: true/false (opcional)
    - activas_solo: true por defecto
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Construir query dinámicamente
        query = "SELECT * FROM farmacias WHERE 1=1"
        params = []
        
        if activas_solo:
            query += " AND esta_activa = TRUE"
        
        if ciudad:
            query += " AND ciudad = %s"
            params.append(ciudad)
        
        if turno_domingo is not None:
            query += " AND domingo_turno = %s"
            params.append(turno_domingo)
        
        query += " ORDER BY ciudad, nombre"
        
        cursor.execute(query, params)
        farmacias = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [Farmacia(**farm) for farm in farmacias]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo farmacias: {str(e)}")

@app.get("/api/farmacias/{farmacia_id}", response_model=Farmacia)
async def obtener_farmacia(farmacia_id: int):
    """Obtener farmacia por ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM farmacias WHERE id = %s", (farmacia_id,))
        farmacia = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not farmacia:
            raise HTTPException(status_code=404, detail="Farmacia no encontrada")
        
        return Farmacia(**farmacia)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo farmacia: {str(e)}")

@app.get("/api/farmacias/ciudad/{ciudad}")
async def obtener_farmacias_por_ciudad(ciudad: str):
    """Obtener todas las farmacias de una ciudad específica"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT * FROM farmacias WHERE ciudad = %s AND esta_activa = TRUE ORDER BY nombre",
            (ciudad,)
        )
        farmacias = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "ciudad": ciudad,
            "total": len(farmacias),
            "farmacias": [Farmacia(**farm) for farm in farmacias]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo farmacias: {str(e)}")

@app.get("/api/farmacias-turno/domingo")
async def obtener_farmacias_domingo():
    """Obtener farmacias en turno para domingo"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT * FROM farmacias WHERE domingo_turno = TRUE AND esta_activa = TRUE ORDER BY ciudad, nombre"
        )
        farmacias = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "turno": "domingo",
            "total": len(farmacias),
            "farmacias": [Farmacia(**farm) for farm in farmacias]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo farmacias: {str(e)}")

@app.post("/api/farmacias", response_model=Farmacia)
async def crear_farmacia(farmacia: FarmaciaCreate):
    """Crear una nueva farmacia (requiere validación)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            """
            INSERT INTO farmacias 
            (nombre, ciudad, direccion, telefonico, horario_apertura, horario_cierre, domingo_turno)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                farmacia.nombre,
                farmacia.ciudad,
                farmacia.direccion,
                farmacia.telefonico,
                farmacia.horario_apertura,
                farmacia.horario_cierre,
                farmacia.domingo_turno
            )
        )
        
        nueva_farmacia = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return Farmacia(**nueva_farmacia)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando farmacia: {str(e)}")

@app.get("/api/estadisticas")
async def obtener_estadisticas():
    """Obtener estadísticas generales de farmacias"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Total de farmacias
        cursor.execute("SELECT COUNT(*) as total FROM farmacias WHERE esta_activa = TRUE")
        total = cursor.fetchone()['total']
        
        # Por ciudad
        cursor.execute(
            "SELECT ciudad, COUNT(*) as cantidad FROM farmacias WHERE esta_activa = TRUE GROUP BY ciudad"
        )
        por_ciudad = cursor.fetchall()
        
        # En turno domingo
        cursor.execute("SELECT COUNT(*) as total FROM farmacias WHERE domingo_turno = TRUE AND esta_activa = TRUE")
        domingo_turno = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return {
            "total_farmacias": total,
            "farmacias_en_turno_domingo": domingo_turno,
            "por_ciudad": {item['ciudad']: item['cantidad'] for item in por_ciudad},
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

# ============ MANEJO DE ERRORES ============
@app.get("/docs")
async def swagger_ui():
    """Acceso a documentación Swagger UI"""
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
