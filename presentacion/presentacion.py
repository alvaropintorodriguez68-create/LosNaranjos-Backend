# presentacion/presentacion.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datos.config_bd import inicializar_tablas_orm

# Importación de los controladores funcionales que aislamos
from presentacion.api_ordenes import router as router_ordenes
from presentacion.api_usuarios import router as router_usuarios

# 1. Inicialización de la Aplicación Core de FastAPI
app = FastAPI(
    title="Ecosystem Los Naranjos - I+D",
    version="2.0.0",
    description="Servidor unificado bajo Arquitectura en Capas (Layered Architecture)"
)

# 2. Configuración de Seguridad CORS (Fase de Laboratorio)
# Permite que las vistas HTML estáticas del mockup interactúen libremente con la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Registro y Acoplamiento de Enrutadores Modulares (Artefactos Acotados)
app.include_router(router_ordenes)
app.include_router(router_usuarios)

# 4. Evento de Arranque de Infraestructura
@app.on_event("startup")
def arrancar_servidor():
    """
    Gatilla la verificación del esquema de datos al encender el backend.
    Fase QA: Si el motor de Postgres está apagado, el log levantará una alerta inmediata.
    """
    print("[QA INFO] Inicializando conexiones y verificando consistencia en PostgreSQL...")
    inicializar_tablas_orm()
    print("[QA INFO] Tablas verificadas de forma exitosa. Servidor en escucha activa.")

# Endpoint base de sanidad de la API
@app.get("/", tags=["Sanidad"])
def verificar_estado_api():
    return {
        "status": "healthy",
        "proyecto": "Los Naranjos I+D",
        "arquitectura": "Decoupled Layered Architecture"
    }

if __name__ == "__main__":
    import uvicorn
    # Comando de ejecución nativo para pruebas locales rápidas
    uvicorn.run("presentacion.presentacion:app", host="127.0.0.1", port=8000, reload=True)
