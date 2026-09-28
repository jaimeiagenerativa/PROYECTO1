"""
Punto de entrada principal de la aplicación FastAPI.
Configuración, inicialización y ejecución de la API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from database import init_db, close_db
from routes.productos import router as productos_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar.
    """
    # Startup
    logger.info("Inicializando aplicación...")
    await init_db()
    logger.info("Base de datos inicializada")
    yield
    # Shutdown
    logger.info("Cerrando aplicación...")
    await close_db()
    logger.info("Conexión de base de datos cerrada")


# Crear aplicación FastAPI
app = FastAPI(
    title="API Gestión de Productos",
    description="API REST profesional para gestionar productos con FastAPI y SQLAlchemy",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Incluir routers
app.include_router(productos_router)


@app.get("/", tags=["Root"], summary="Endpoint raíz")
async def root():
    """
    Endpoint raíz que retorna información sobre la API.
    """
    return {
        "mensaje": "Bienvenido a la API de Gestión de Productos",
        "versión": "1.0.0",
        "documentación": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "productos": "/productos",
        }
    }


@app.get("/health", tags=["Health"], summary="Health Check")
async def health_check():
    """
    Verificar que la aplicación está en ejecución.
    """
    return {
        "status": "healthy",
        "service": "API Gestión de Productos",
        "version": "1.0.0"
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Manejador general de excepciones.
    """
    logger.error(f"Error no manejado: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Error interno del servidor",
            "timestamp": str(__import__('datetime').datetime.utcnow())
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Configuración de ejecución
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
