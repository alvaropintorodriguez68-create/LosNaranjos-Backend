import os
import logging
# IMPORTANTE: Cargamos el manejador de rotación relacional nativo
from logging.handlers import RotatingFileHandler 
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. CONFIGURACIÓN DEL LOGGER
logger_sql = logging.getLogger("sqlalchemy.engine")
logger_sql.setLevel(logging.INFO)

formato = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

# Aseguramos la existencia de la carpeta aislada
os.makedirs("logs", exist_ok=True)

# EQUIVALENTE AL ROLLINGFILEAPPENDER:
# - maxBytes = 5 * 1024 * 1024 (Equivale a 5 Megabytes por archivo)
# - backupCount = 5 (Mantiene auditoria_sql.log, .log.1, .log.2 ... hasta .log.5)
manejador_archivo = RotatingFileHandler(
    "logs/auditoria_sql.log", 
    maxBytes=5 * 1024 * 1024, 
    backupCount=5, 
    encoding="utf-8"
)
manejador_archivo.setFormatter(formato)
logger_sql.addHandler(manejador_archivo)

# Manejador de Consola
manejador_consola = logging.StreamHandler()
manejador_consola.setFormatter(formato)
logger_sql.addHandler(manejador_consola)


# =====================================================================
# 1.B LOGGER DE APLICACIÓN / NEGOCIO (Nuevo canal para auditoría de acciones)
# =====================================================================
logger_negocio = logging.getLogger("aplicacion.negocio")
logger_negocio.setLevel(logging.INFO)

# Handler rotativo de 5MB, igual que el de SQL, pero escribe en 'auditoria_negocio.log'
manejador_negocio = RotatingFileHandler(
    "logs/auditoria_negocio.log", 
    maxBytes=5 * 1024 * 1024, 
    backupCount=5, 
    encoding="utf-8"
)
manejador_negocio.setFormatter(formato)
logger_negocio.addHandler(manejador_negocio)

# También lo mandamos a consola para verlo en tiempo real al desarrollar
logger_negocio.addHandler(manejador_consola)

# ==========================================
# 2. MOTOR DE LA BASE DE DATOS (POSTGRESQL)
# ==========================================

DATABASE_URL = "postgresql://postgres:tu_clave_aqui@localhost:5432/los_naranjos_db"
# El usuario de administración predeterminado en Postgres es 'postgres'
DATABASE_URL = "postgresql://postgres:sa@localhost:5432/los_naranjos_db"

engine = create_engine(
    DATABASE_URL, 
    echo=False,
    client_encoding="utf8"
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()






def obtener_bd():
    bd = SessionLocal()
    try:
        yield bd
    finally:
        bd.close()

def inicializar_tablas_orm():
    Base.metadata.create_all(bind=engine)

# Alias de compatibilidad para la capa de presentación
obtener_conexion_db = obtener_bd
