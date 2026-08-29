# datos/modelos.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from datos.data_helper import Base

# =====================================================================
#  CLASE BASE DE AUDITORÍA (Shadow Properties para Trazabilidad)
# =====================================================================
class AuditoriaMixin:
    UsuarioCreacion = Column(String, nullable=False, default="sistema")
    FechaCreacion = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    UsuarioModificacion = Column(String, nullable=True)
    FechaModificacion = Column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    EstadoTupla = Column(Boolean, nullable=False, default=True) # Manejo de Soft Delete

# =====================================================================
#  DEFINICIÓN DE ENTIDADES EN POSTGRESQL (MVP LOS NARANJOS)
# =====================================================================

class SucursalModelo(Base, AuditoriaMixin):
    __tablename__ = "sucursales"
    id_sucursal = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
    direccion = Column(String, nullable=False)

    mesas = relationship("MesaModelo", back_populates="sucursal")

class MesaModelo(Base, AuditoriaMixin):
    __tablename__ = "mesas"
    id_mesa = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_sucursal = Column(Integer, ForeignKey("sucursales.id_sucursal"), nullable=False)
    numero = Column(Integer, nullable=False)
    capacidad = Column(Integer, nullable=False)

    sucursal = relationship("SucursalModelo", back_populates="mesas")
    pedidos = relationship("PedidoModelo", back_populates="mesa")

class ClienteModelo(Base, AuditoriaMixin):
    __tablename__ = "clientes"
    id_cliente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    rut = Column(String, unique=True, nullable=False)
    telefono = Column(String, nullable=False)
    email = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    tipo_cliente = Column(String, nullable=False) # ej: Frecuente, Crédito, VIP
    observaciones = Column(String, nullable=True)

    pedidos = relationship("PedidoModelo", back_populates="cliente")
    cuenta_credito = relationship("CuentaCreditoModelo", uselist=False, back_populates="cliente")

class PedidoModelo(Base, AuditoriaMixin):
    __tablename__ = "pedidos"
    id_pedido = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_sucursal = Column(Integer, ForeignKey("sucursales.id_sucursal"), nullable=False)
    id_mesa = Column(Integer, ForeignKey("mesas.id_mesa"), nullable=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"), nullable=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    fecha_hora = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    canal = Column(String, nullable=False) # Salón, WhatsApp, Tótem, Delivery
    estado = Column(String, nullable=False) # Pendiente, Preparando, Entregado, Pagado, Anulado

    mesa = relationship("MesaModelo", back_populates="pedidos")
    cliente = relationship("ClienteModelo", back_populates="pedidos")
    usuario = relationship("UsuarioModelo", back_populates="pedidos")
    detalles = relationship("DetallePedidoModelo", back_populates="pedido")
    comandas = relationship("ComandaModelo", back_populates="pedido")
    pagos = relationship("PagoModelo", back_populates="pedido")

class DetallePedidoModelo(Base, AuditoriaMixin):
    __tablename__ = "detalles_pedido"
    id_detalle = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    observaciones = Column(String, nullable=True)

    pedido = relationship("PedidoModelo", back_populates="detalles")
    producto = relationship("ProductoModelo", back_populates="detalles")

class ProductoModelo(Base, AuditoriaMixin):
    __tablename__ = "productos"
    id_producto = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    precio = Column(Float, nullable=False)

    detalles = relationship("DetallePedidoModelo", back_populates="producto")

class ComandaModelo(Base, AuditoriaMixin):
    __tablename__ = "comandas"
    id_comanda = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False)
    fecha_hora_emision = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    estado = Column(String, nullable=False) # En Cocina, Listó, Entregado, Anulado

    pedido = relationship("PedidoModelo", back_populates="comandas")

class PagoModelo(Base, AuditoriaMixin):
    __tablename__ = "pagos"
    id_pago = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False)
    medio_pago = Column(String, nullable=False) # Efectivo, Débito, Crédito, Transferencia
    monto = Column(Float, nullable=False)
    fecha_hora = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    pedido = relationship("PedidoModelo", back_populates="pagos")

# En datos/modelos.py - Reemplaza la clase UsuarioModelo por esta versión:

class UsuarioModelo(Base, AuditoriaMixin):
    __tablename__ = "usuarios"
    
    # Campo requerido para resolver la llave foránea relacional de los pedidos
    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hashed = Column(String, nullable=False)

    pedidos = relationship("PedidoModelo", back_populates="usuario")


# =====================================================================
#  MÓDULO SEPARADO DE CRÉDITO (Principio de Desacoplamiento)
# =====================================================================
class CuentaCreditoModelo(Base, AuditoriaMixin):
    __tablename__ = "cuentas_credito"
    id_cuenta_credito = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"), unique=True, nullable=False)
    saldo = Column(Float, nullable=False, default=0.0)
    limite_credito = Column(Float, nullable=False, default=100000.0)

    cliente = relationship("ClienteModelo", back_populates="cuenta_credito")
    movimientos = relationship("MovimientoCreditoModelo", back_populates="cuenta_credito")

class MovimientoCreditoModelo(Base, AuditoriaMixin):
    __tablename__ = "movimientos_credito"
    id_movimiento = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_cuenta_credito = Column(Integer, ForeignKey("cuentas_credito.id_cuenta_credito"), nullable=False)
    fecha_hora = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    tipo_movimiento = Column(String, nullable=False) # Consumo, Abono, Prepago, Ajuste
    monto = Column(Float, nullable=False)
    referencia = Column(String, nullable=True) # ID de Pedido o número de boleta/recibo

    cuenta_credito = relationship("CuentaCreditoModelo", back_populates="movimientos")
