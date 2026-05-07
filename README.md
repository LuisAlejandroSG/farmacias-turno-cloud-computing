# 🏥 Sistema de Farmacias de Turno - Coronel, Lota, Arauco

## Descripción General

Sistema de gestión y consulta de farmacias de turno para las ciudades de Coronel, Lota y Arauco. Implementado con una arquitectura distribuida en dos instancias EC2 de AWS:

- **Instancia 1**: API FastAPI + PostgreSQL + Nginx
- **Instancia 2**: Cliente Python que consume la API

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    INSTANCIA EC2 #1                         │
│              (API + BD + Nginx Reverse Proxy)               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Nginx (Puerto 80)                                   │  │
│  │  └─ Reverse Proxy                                    │  │
│  │  └─ Rate Limiting (100 req/s)                        │  │
│  │  └─ Compresión Gzip                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│              ↓                    ↓                         │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │  FastAPI (Puerto 8000)  │  │  PostgreSQL 15     │        │
│  │                         │  │  (Puerto 5432)     │        │
│  │  - 7 Endpoints GET      │  │                    │        │
│  │  - 1 Endpoint POST      │  │  - Farmacias       │        │
│  │  - Health Check        │  │  - Vistas           │        │
│  │  - Documentación Swagger│  │  - Índices          │        │
│  └──────────────────────┘  └──────────────────────┘        │
│        (Docker)                 (Docker)                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
              ↑
              │ HTTP/80
              │
┌─────────────────────────────────────────────────────────────┐
│                    INSTANCIA EC2 #2                         │
│                    (Cliente Python)                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Cliente Python 3                                    │  │
│  │  - Clase ClienteFarmacias                            │  │
│  │  - Métodos de consulta                               │  │
│  │  - Demostración interactiva                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework asincrónico, rendimiento > 100k req/s
- **PostgreSQL 15**: BD relacional con vistas optimizadas
- **Nginx**: Reverse proxy, load balancer, rate limiting

### Contenedorización
- **Docker**: Contenedores para API, BD, Nginx
- **Docker Compose**: Orquestación de servicios

### Cliente
- **Python 3**: Lenguaje de programación
- **Requests**: Cliente HTTP

## Justificación Técnica

### ¿Por qué FastAPI?
1. **Rendimiento**: Basado en Starlette + Uvicorn (ASGI)
2. **Documentación automática**: Swagger UI integrado
3. **Validación de datos**: Pydantic integrado
4. **Fácil de testear**: Diseño modular
5. **Popular en industria**: Widely adopted para microservicios

### ¿Por qué PostgreSQL?
1. **ACID compliant**: Integridad de datos garantizada
2. **JSON nativo**: Soporte para datos semiestructurados
3. **Índices**: Performance en búsquedas por ciudad
4. **Vistas**: Simplificar consultas complejas
5. **Escalabilidad**: Soporta millones de registros

### ¿Por qué Puerto 80 con Nginx?
1. **Seguridad**: Puerto estándar, menos propenso a ataques
2. **Simpledad**: No requiere configuración especial de firewall
3. **Proxy reverso**: Oculta la verdadera dirección de la API
4. **Load balancing**: Posibilidad de escalar a múltiples instancias
5. **Rate limiting**: Protección contra abuso

## Instalación

### Instancia 1: API + BD

```bash
# 1. Descargar e instalar
bash scripts/instalar-instancia-1.sh

# 2. Copiar archivos del proyecto
# (Estructura esperada en ~/farmacias-turnos/)

# 3. Iniciar servicios
cd ~/farmacias-turnos
docker-compose up -d

# 4. Verificar que está funcionando
curl http://localhost/health
curl http://localhost/api/estadisticas
```

### Instancia 2: Cliente

```bash
# 1. Instalar dependencias
bash scripts/instalar-instancia-2.sh

# 2. Copiar cliente
cp cliente_farmacias.py ~/cliente-farmacias/

# 3. Editar IP del servidor
nano ~/cliente-farmacias/cliente_farmacias.py
# Cambiar: API_BASE_URL = "http://IP_INSTANCIA_1/api"

# 4. Crear entorno e instalar
cd ~/cliente-farmacias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Ejecutar cliente
python3 cliente_farmacias.py
```

## Endpoints API

### GET /health
Health check de la API
```bash
curl http://localhost/health
```

### GET /api/farmacias
Listar todas las farmacias (con filtros opcionales)
```bash
curl http://localhost/api/farmacias
curl "http://localhost/api/farmacias?ciudad=Coronel"
curl "http://localhost/api/farmacias?turno_domingo=true"
curl "http://localhost/api/farmacias?ciudad=Lota&turno_domingo=true"
```

### GET /api/farmacias/{id}
Obtener farmacia específica
```bash
curl http://localhost/api/farmacias/1
```

### GET /api/farmacias/ciudad/{ciudad}
Obtener todas las farmacias de una ciudad
```bash
curl http://localhost/api/farmacias/ciudad/Coronel
```

### GET /api/farmacias-turno/domingo
Obtener farmacias en turno para domingo
```bash
curl http://localhost/api/farmacias-turno/domingo
```

### GET /api/estadisticas
Obtener estadísticas generales
```bash
curl http://localhost/api/estadisticas
```

### POST /api/farmacias
Crear nueva farmacia
```bash
curl -X POST http://localhost/api/farmacias \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Farmacia Nueva",
    "ciudad": "Coronel",
    "direccion": "Calle Nueva 123",
    "telefonico": "41-2123456",
    "domingo_turno": true
  }'
```

## Estructura del Código

```
farmacias-turnos/
├── docker-compose.yml              # Orquestación principal
├── api/
│   ├── main.py                     # API FastAPI
│   ├── Dockerfile                  # Contenedor API
│   ├── requirements.txt            # Dependencias Python
│   └── init.sql                    # Datos iniciales
├── database/
│   ├── docker-compose.yml          # BD independiente (opcional)
│   └── init.sql                    # Script SQL
├── client/
│   ├── cliente_farmacias.py        # Cliente Python
│   └── requirements.txt            # Dependencias
├── nginx/
│   └── farmacias-api.conf          # Configuración Nginx
├── scripts/
│   ├── instalar-instancia-1.sh     # Setup Instancia 1
│   └── instalar-instancia-2.sh     # Setup Instancia 2
└── docs/
    ├── ARQUITECTURA.md             # Diagrama técnico
    ├── API_SPEC.md                 # Especificación API
    └── DEPLOYMENT.md               # Guía de despliegue
```

## Monitoreo y Troubleshooting

### Ver logs
```bash
# Todos los servicios
docker-compose logs -f

# Solo API
docker-compose logs -f api

# Solo BD
docker-compose logs -f postgres

# Solo Nginx
docker-compose logs -f nginx
```

### Verificar estado
```bash
# Estado de contenedores
docker-compose ps

# Conexión a BD
docker exec farmacias_api psql -U farmacia_user -d farmacias_db -c "SELECT COUNT(*) FROM farmacias;"

# Test de API
curl -v http://localhost/api/farmacias | jq .
```

### Problemas comunes

**Nginx no se conecta a API**
```bash
# Verificar que API está escuchando
docker exec farmacias_api curl http://localhost:8000/health

# Revisar logs Nginx
docker-compose logs nginx
```

**BD no inicializa con datos**
```bash
# Ejecutar script SQL manualmente
docker exec farmacias_db psql -U farmacia_user -d farmacias_db < database/init.sql
```

**Cliente no se conecta**
```bash
# Verificar IP privada de instancia 1
hostname -I

# Editar cliente_farmacias.py con IP correcta
# Probar conexión
curl http://IP_INSTANCIA_1/health
```

## Configuración de Seguridad

- ✅ Usuario no-root en contenedores
- ✅ Contraseña PostgreSQL fuerte
- ✅ Headers de seguridad en Nginx (X-Frame-Options, X-Content-Type-Options)
- ✅ CORS configurado
- ✅ Rate limiting: 100 req/s por IP
- ✅ Compresión Gzip habilitada
- ✅ Health checks automáticos

## Performance

- **API**: ~100,000+ req/s en máquina moderna
- **BD**: Índices optimizados en ciudad y turno_domingo
- **Nginx**: Buffering y compresión configurada
- **Timeout**: 30 segundos para conexiones largas

## Datos Incluidos

- **Coronel**: 5 farmacias
- **Lota**: 4 farmacias
- **Arauco**: 4 farmacias
- **Total**: 13 farmacias iniciales

Todas las farmacias incluyen:
- Nombre, ciudad, dirección
- Teléfono
- Horario apertura/cierre
- Turno domingo (sí/no)
- Estado activo/inactivo

## Créditos de Datos

Datos basados en:
- Datos abiertos de Chile: https://datos.gob.cl/dataset/farmacias-en-chile
- Registros de farmacias de turno MINSAL

## Licencia

Proyecto académico - I.P. Virginio Gómez

---

**Última actualización**: Mayo 2024
**Versión**: 1.0.0
