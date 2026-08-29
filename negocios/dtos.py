# negocios/dtos.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# ==========================================
#          DTOs DE SUCURSAL y MESA
# ==========================================
class MesaRespuestaDTO(BaseModel):
    id_mesa: int
    numero: int
    capacidad: int
    
    class Config:
        from_attributes = True # Permite a Pydantic leer objetos ORM de SQLAlchemy

# ==========================================
#          DTOs DE CLIENTE (Fidelización)
# ==========================================
class ClienteCrearDTO(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    rut: str = Field(..., min_length=8, max_length=12) # ej: 12345678-9
    telefono: str = Field(...)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    tipo_cliente: str = Field(default="Frecuente") # Frecuente, VIP, Crédito
    observaciones: Optional[str] = None

class ClienteRespuestaDTO(BaseModel):
    id_cliente: int
    nombre: str
    rut: str
    tipo_cliente: str
    estado: bool = Field(alias="EstadoTupla") # Mapeo limpio para el frontend

    class Config:
        from_attributes = True

# ==========================================
#          DTOs DE PRODUCTO
# ==========================================
class ProductoRespuestaDTO(BaseModel):
    id_producto: int
    nombre: str
    categoria: str
    precio_neto: float = Field(alias="precio")
    precio_con_iva: float

    class Config:
        from_attributes = True

# ==========================================
#          DTOs DE PEDIDO Y DETALLES
# ==========================================
class DetallePedidoCrearDTO(BaseModel):
    id_producto: int
    cantidad: int = Field(..., gt=0) # Debe ser mayor a 0
    observaciones: Optional[str] = None

class PedidoCrearDTO(BaseModel):
    id_sucursal: int
    id_mesa: Optional[int] = None
    id_cliente: Optional[int] = None
    id_usuario: int
    canal: str # Salón, WhatsApp, Retiro, Delivery
    detalles: List[DetallePedidoCrearDTO]

class PedidoRespuestaDTO(BaseModel):
    id_pedido: int
    fecha_hora: datetime
    canal: str
    estado: str
    monto_total_neto: float
    monto_total_iva: float

    class Config:
        from_attributes = True
# Agregar al final de negocios/dtos.py

class MovimientoCreditoCrearDTO(BaseModel):
    id_cliente: int
    tipo_movimiento: str # Consumo, Abono, Prepago, Ajuste
    monto: float = Field(..., gt=0) # Debe ser mayor a cero
    referencia: Optional[str] = None # ej: "Boleta 1023" o "Pedido 4"

class EstadoCreditoRespuestaDTO(BaseModel):
    id_cliente: int
    saldo_actual: float
    limite_credito: float
    saldo_disponible: float

    class Config:
        from_attributes = True
