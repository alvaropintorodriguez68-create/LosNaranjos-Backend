#ordenes_dao.py
# datos/ordenes_dao.py
from sqlalchemy.orm import Session
import uuid
# Nota: Asumimos que tienes tus modelos SQLAlchemy definidos en datos/modelos.py
from datos.modelos import Orden as OrdenORM, DetalleOrden as DetalleOrdenORM


class OrdenesDAO:
    @staticmethod
    def insertar_orden_completa(db: Session, orden_data: dict, items_data: list) -> dict:
        """
        Persiste una orden con sus detalles dentro de una transacción atómica.
        Fase QA: Si falla un ítem, la orden completa hace Rollback en Postgres.
        """
        try:
            # 1. Crear instancia del encabezado de la orden
            nueva_orden = OrdenORM(
                id_orden=uuid.uuid4(),
                id_mesa=orden_data.get("id_mesa"),
                id_cliente_remoto=orden_data.get("id_cliente_remoto"),
                origen=orden_data.get("origen"),
                estado="pendiente",
                total_neto=orden_data.get("total_neto", 0.0),
                created_by=orden_data.get("created_by")
            )
            db.add(nueva_orden)
            db.flush()  # Genera el ID en la sesión sin confirmar la transacción aún

            # 2. Crear las instancias de los detalles enlazados
            for item in items_data:
                nuevo_detalle = DetalleOrdenORM(
                    id_detalle=uuid.uuid4(),
                    id_orden=nueva_orden.id_orden,
                    sku_producto=item.get("sku_producto"),
                    nombre_producto=item.get("nombre_producto"),
                    cantidad=item.get("cantidad"),
                    precio_unitario=item.get("precio_unitario"),
                    observaciones=item.get("observaciones"),
                    created_by=orden_data.get("created_by")
                )
                db.add(nuevo_detalle)

            db.commit()  # Confirmación física en pgAdmin 4
            db.refresh(nueva_orden)
            
            return {
                "id_orden": nueva_orden.id_orden,
                "total_neto": nueva_orden.total_neto,
                "created_at": nueva_orden.created_at
            }
        except Exception as e:
            db.rollback()  # Resguardo de consistencia QA
            raise e
