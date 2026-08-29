#api_ordenes.py
# presentacion/api_ordenes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# Nota: Importamos el generador de sesión desde tu config_bd

from datos.config_bd import obtener_bd as obtener_conexion_db

from .schemas import IngestaPedidoSchema

from negocios.gestor_ordenes import GestorOrdenes

router = APIRouter(prefix="/api/v1/pedidos", tags=["Órdenes"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def recibir_pedido_omnicanal(pedido: IngestaPedidoSchema, db: Session = Depends(obtener_conexion_db)):
    """
    Endpoint Unificado para la ingesta del Mockup o Webhooks externos.
    """
    try:
        # Transformar el esquema Pydantic a diccionario para la capa de negocio
        datos_dict = pedido.dict()
        
        # Delegar la ejecución completa a la capa de negocio
        resultado = GestorOrdenes.procesar_nueva_comanda(db, datos_dict)
        
        return {
            "status": "success",
            "message": "Comanda procesada e inyectada con éxito en el ecosistema relacional.",
            "data": resultado
        }
    except ValueError as err_negocio:
        # Captura errores controlados de las reglas de negocio (400 Bad Request)
        raise HTTPException(status_code=400, detail=str(err_negocio))
    except Exception as err_sistema:
        # Captura caídas inesperadas de Postgres o del driver (500 Internal Error)
        raise HTTPException(status_code=500, detail=f"Fallo crítico en infraestructura: {str(err_sistema)}")
