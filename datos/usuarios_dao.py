#usuarios_dao.py
# datos/usuarios_dao.py
from sqlalchemy.orm import Session
from datos.modelos import UsuarioORM  # Tu modelo mapeado de SQLAlchemy

class UsuariosDAO:
    @staticmethod
    def buscar_por_username(db: Session, username: str) -> UsuarioORM:
        """
        Busca un usuario activo en PostgreSQL para el proceso de login.
        Fase QA: Filtra estrictamente que el usuario no tenga un borrado lógico (is_active=True).
        """
        return db.query(UsuarioORM).filter(
            UsuarioORM.username == username,
            UsuarioORM.is_active == True
        ).first()

    @staticmethod
    def registrar_usuario(db: Session, usuario_data: dict) -> UsuarioORM:
        """
        Persiste un nuevo operador (Mozo, Cocina, Administrador) en pgAdmin 4.
        """
        nuevo_usuario = UsuarioORM(
            username=usuario_data["username"],
            password_hash=usuario_data["password_hash"],
            rol=usuario_data["rol"],
            created_by=usuario_data["created_by"]
        )
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario
