
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# Estructura de cada plato/ítem en el JSON
class DetallePedidoSchema(BaseModel):
    sku_producto: str
    nombre_producto: str
    cantidad: int = Field(..., gt=0, description="La cantidad debe ser mayor a 0")
    precio_unitario: float
    observaciones: Optional[str] = None

# Estructura del Pedido Universal (Puerta de Entrada)
class IngestaPedidoSchema(BaseModel):
    id_mesa: Optional[int] = None
    id_cliente_remoto: Optional[int] = None
    origen: str = Field(..., description="Valores válidos: salon, whatsapp, delivery_app")
    created_by: str = Field(..., description="ID del usuario o sistema que gatilla la orden")
    pedido_items: List[DetallePedidoSchema]
