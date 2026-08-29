# datos/ordenes_dao.py
from sqlalchemy.orm import Session
# Importamos tus clases reales con los alias que espera el resto de las capas
from datos.modelos import PedidoModelo as OrdenORM, DetallePedidoModelo as DetalleOrdenORM 

class OrdenesDAO:
    @staticmethod
    def insertar_orden_completa(db: Session, orden_data: dict, items_data: list) -> dict:
        """
        Persiste una orden con sus detalles dentro de una transacción atómica.
        Fase QA: Si falla un ítem, la orden completa hace Rollback en Postgres.
        """
        try:
            # 1. Crear instancia del encabezado de la orden (Campos reales de tu PedidoModelo)
            nueva_orden = OrdenORM(
                id_sucursal=1,  # Valor por defecto inicial para tu relación obligatoria
                id_mesa=orden_data.get("id_mesa"),
                id_cliente=orden_data.get("id_cliente_remoto"),
                id_usuario=1,   # Operador inicial (puedes dinamizarlo luego con el login)
                canal=orden_data.get("origen"), # 'salon' o 'whatsapp'
                estado="Pendiente",
                created_by=orden_data.get("created_by")
            )
            db.add(nueva_orden)
            db.flush()  # Genera el id_pedido de forma secuencial en Postgres antes del commit

            # 2. Crear las instancias de los detalles (Campos reales de tu DetallePedidoModelo)
            for item in items_data:
                nuevo_detalle = DetalleOrdenORM(
                    id_pedido=nueva_orden.id_pedido,
                    id_producto=item.get("id_producto", 1), # Usa id_producto numérico como pide tu FK
                    cantidad=item.get("cantidad"),
                    precio_unitario=item.get("precio_unitario"),
                    observaciones=item.get("observaciones"),
                    created_by=orden_data.get("created_by")
                )
                db.add(nuevo_detalle)

            db.commit()  # Confirmación física y atómica en pgAdmin 4
            db.refresh(nueva_orden)
            
            return {
                "id_pedido": nueva_orden.id_pedido,
                "canal": nueva_orden.canal,
                "estado": nueva_orden.estado,
                "created_at": getattr(nueva_orden, "created_at", None) # Extraído de tu AuditoriaMixin
            }
        except Exception as e:
            db.rollback()  # Resguardo de consistencia estricta QA
            raise e
