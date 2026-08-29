from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime, timezone
from datos.config_bd import Base, engine

# =====================================================================
#  CLASE BASE DE AUDITORÍA (Mixin para heredar en todas las tablas)
# =====================================================================
class AuditoriaMixin:
    UsuarioCreacion = Column(String, nullable=False, default="sistema")
    FechaCreacion = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    UsuarioModificacion = Column(String, nullable=True)
    FechaModificacion = Column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    EstadoTupla = Column(Boolean, nullable=False, default=True) # True = Activo, False = Eliminado Lógico

# ==========================================
#         DEFINICIÓN DE LOS MODELOS 
# ==========================================

class ProductoModelo(Base, AuditoriaMixin):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)

class UsuarioModelo(Base, AuditoriaMixin):
    __tablename__ = "usuarios"

    username = Column(String, primary_key=True, index=True)
    password_hashed = Column(String, nullable=False)

def inicializar_tablas_orm():
    """Crea o actualiza las tablas en Postgres con las nuevas columnas."""
    Base.metadata.create_all(bind=engine)

# ==========================================
#         CONSULTAS DEL REPOSITORIO MODIFICADAS
# ==========================================

def obtener_todos_los_productos(db):
    """Investigación: Filtramos para traer SOLO los registros con EstadoTupla = True (Activos)"""
    return db.query(ProductoModelo).filter(ProductoModelo.EstadoTupla == True).all()

def insertar_producto(db, nombre: str, precio: float, usuario: str):
    """Guarda un registro inyectando el usuario de forma segura."""
    # Validación preventiva: si por algún motivo 'usuario' viene vacío, nulo o en blanco, 
    # le asignamos la cadena corporativa por defecto.
    usuario_seguro = usuario if (usuario and usuario.strip()) else "sistema"
    
    nuevo_producto = ProductoModelo(
        nombre=nombre, 
        precio=precio, 
        UsuarioCreacion=usuario_seguro, # Guardamos el usuario validado
        EstadoTupla=True
    )
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto

def eliminar_producto_por_id(db, id_producto: int, usuario: str):
    """¡BORRADO LÓGICO DE PRODUCCIÓN!
    Busca el objeto y en lugar de db.delete(), apaga su EstadoTupla.
    """
    from datetime import datetime, timezone
    
    producto = db.query(ProductoModelo).filter(ProductoModelo.id == id_producto).first()
    if producto:
        producto.EstadoTupla = False
        producto.UsuarioModificacion = usuario
        producto.FechaModificacion = datetime.now(timezone.utc)
        db.commit()

def obtener_usuario(db, username: str):
    """Busca un usuario y retorna su hash string."""
    usuario = db.query(UsuarioModelo).filter(UsuarioModelo.username == username).first()
    return usuario.password_hashed if usuario else None

def registrar_usuario(db, username: str, password_hashed: str):
    """Registra el hash string del usuario mediante el ORM."""
    existe = db.query(UsuarioModelo).filter(UsuarioModelo.username == username).first()
    if existe:
        raise ValueError("El nombre de usuario ya existe.")
    
    nuevo_usuario = UsuarioModelo(username=username, password_hashed=password_hashed)
    db.add(nuevo_usuario)
    db.commit()
