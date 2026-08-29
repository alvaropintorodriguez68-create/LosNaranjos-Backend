#gestor_ordenes.py
# negocios/gestor_ordenes.py
from datos.ordenes_dao import OrdenesDAO
from sqlalchemy.orm import Session

class GestorOrdenes:
    @staticmethod
    def procesar_nueva_comanda(db: Session, datos_pedido: dict) -> dict:
        """
        Aplica reglas de negocio omnicanal y calcula costos antes de la persistencia.
        """
        origen = datos_pedido.get("origen")
        items = datos_pedido.get("pedido_items", [])

        # Regla 1: Validaciones cruzadas de Origen (Filtro QA de consistencia)
        if origen == "salon" and not datos_pedido.get("id_mesa"):
            raise ValueError("Error de Negocio: Los pedidos de salón requieren un número de mesa válido.")
            
        if origen == "whatsapp" and not datos_pedido.get("id_cliente_remoto"):
            raise ValueError("Error de Negocio: Los pedidos de WhatsApp requieren identificador de cliente remoto.")

        # Regla 2: El pedido no puede ir vacío
        if not items:
            raise ValueError("Error de Negocio: La orden debe contener al menos un producto.")

        # Regla 3: Cálculo automatizado del total neto en el servidor
        total_calculado = sum(item["cantidad"] * item["precio_unitario"] for item in items)
        
        # Estructurar payloads limpios para la capa DAO
        orden_payload = {
            "id_mesa": datos_pedido.get("id_mesa"),
            "id_cliente_remoto": datos_pedido.get("id_cliente_remoto"),
            "origen": origen,
            "total_neto": total_calculado,
            "created_by": datos_pedido.get("created_by")
        }

        # Invocar la capa de acceso a datos
        resultado_dao = OrdenesDAO.insertar_orden_completa(db, orden_payload, items)
        return resultado_dao
