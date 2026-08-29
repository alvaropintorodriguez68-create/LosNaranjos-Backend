#api_usuarios.py
# presentacion/api_usuarios.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from datos.config_bd import obtener_bd as obtener_conexion_db

from negocios.autenticador import Autenticador

router = APIRouter(prefix="/api/v1/auth", tags=["Seguridad"])

# Esquema Pydantic local exclusivo para la validación del Login
class LoginRequestSchema(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login_operador(credenciales: LoginRequestSchema, db: Session = Depends(obtener_conexion_db)):
    """
    Endpoint modular para el ingreso de usuarios al ecosistema Los Naranjos.
    """
    try:
        resultado = Autenticador.verificar_credenciales(
            db=db,
            username=credenciales.username,
            password_plano=credenciales.password
        )
        return {
            "status": "success",
            "message": f"Bienvenido al sistema, operador {resultado['username']}.",
            "sesion": resultado
        }
    except ValueError as err_autenticacion:
        # Captura el rechazo de credenciales (401 Unauthorized)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=str(err_autenticacion)
        )
    except Exception as err_sistema:
        # Resguardo ante fallos de conexión con Postgres (500)
        raise HTTPException(
            status_code=500, 
            detail=f"Fallo en infraestructura de autenticación: {str(err_sistema)}"
        )
