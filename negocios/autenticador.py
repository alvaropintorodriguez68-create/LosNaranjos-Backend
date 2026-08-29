#autenticador.py
# negocios/autenticador.py
import hashlib
from datos.usuarios_dao import UsuariosDAO
from sqlalchemy.orm import Session

class Autenticador:
    @staticmethod
    def generar_sha256_hash(password: str) -> str:
        """
        Genera un hash SHA-256 seguro a partir de texto plano.
        Solución nativa robusta elegida en la fase de I+D.
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @classmethod
    def verificar_credenciales(cls, db: Session, username: str, password_plano: str) -> dict:
        """
        Valida el acceso comparando los hashes SHA-256 de forma segura.
        """
        # 1. Recuperar el usuario desde el DAO
        usuario = UsuariosDAO.buscar_por_username(db, username)
        
        # Regla QA: Si el usuario no existe en Postgres, se rechaza de inmediato
        if not usuario:
            raise ValueError("Acceso denegado: Credenciales inválidas.")

        # 2. Hashear la contraseña ingresada y comparar
        hash_ingresado = cls.generar_sha256_hash(password_plano)
        
        if hash_ingresado != usuario.password_hash:
            raise ValueError("Acceso denegado: Credenciales inválidas.")

        # Retornar payload de sesión limpio si todo es exitoso
        return {
            "username": usuario.username,
            "rol": usuario.rol,
            "status": "autenticado"
        }
