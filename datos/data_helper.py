# datos/data_helper.py
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datos.config_bd import logger_sql  # Reutilizamos tu logger rotativo de 5MB

Base = declarative_base()

class DataHelper:
    _instancia = None
    _lock = threading.Lock()  # Garantiza seguridad en entornos multi-hilo (Thread-Safe)

    def __new__(cls, *args, **kwargs):
        """Implementación estricta del patrón Singleton."""
        if not cls._instancia:
            with cls._lock:
                if not cls._instancia:
                    cls._instancia = super(DataHelper, cls).__new__(cls)
                    cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        """Inicialización única del pool de conexiones a PostgreSQL."""
        # Cadena de conexión corporativa a tu base de datos de producción
        self.DATABASE_URL = "postgresql://postgres:sa@localhost:5432/los_naranjos_db"
        
        logger_sql.info("SINGLETON: Inicializando el pool de conexiones único hacia PostgreSQL.")
        
        self.engine = create_engine(
            self.DATABASE_URL,
            echo=False,  # El logger_sql ya captura los queries en nivel INFO
            pool_size=10,
            max_overflow=20,
            client_encoding="utf8"
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def obtener_bd(self):
        """Generador de sesiones para la inyección de dependencias en FastAPI."""
        bd = self.SessionLocal()
        try:
            yield bd
        finally:
            bd.close()

    def inicializar_tablas(self):
        """Crea todas las entidades en PostgreSQL si no existen."""
        logger_sql.info("INFRAESTRUCTURA: Verificando y creando el esquema de tablas del MVP.")
        Base.metadata.create_all(bind=self.engine)
