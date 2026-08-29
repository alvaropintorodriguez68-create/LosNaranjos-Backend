# negocios/gestor_ordenes.py
from datos.ordenes_dao import OrdenesDAO
from sqlalchemy.orm import Session

class GestorOrdenes:
    @staticmethod
    def procesar_nueva_comanda(db: Session, datos_pedido: dict) -> dict:
        """
        Aplica reglas de negocio omnicanal y valida la consistencia 
        de los datos antes de enviarlos a la persistencia en PostgreSQL.
        """
        origen = datos_pedido.get("origen")
        items = datos_pedido.get("pedido_items", [])

        # REGLA 1: Validaciones cruzadas de Origen (Filtro QA de consistencia)
        if origen == "salon" and not datos_pedido.get("id_mesa"):
            raise ValueError("Error de Negocio: Los pedidos de salón requieren un número de mesa válido.")
            
        if origen == "whatsapp" and not datos_pedido.get("id_cliente_remoto"):
            raise ValueError("Error de Negocio: Los pedidos de WhatsApp requieren identificador de cliente remoto.")

        # REGLA 2: El pedido debe contener obligatoriamente platos o bebidas
        if not items:
            raise ValueError("Error de Negocio: La orden debe contener al menos un producto.")

        # REGLA 3: Adaptación y mapeo estructural al modelo relacional de GitHub
        # Convertimos los datos planos que vienen de la web/mockup a lo que pide el DAO y PostgreSQL
        items_procesados = []
        for item in items:
            items_procesados.append({
                # Mapeamos 'id_producto' (o resolvemos a un id por defecto si viene SKU en el mockup)
                "id_producto": item.get("id_producto", 1), 
                "cantidad": item.get("cantidad"),
                "precio_unitario": item.get("precio_unitario"),
                "observaciones": item.get("observaciones")
            })

        # Estructuramos el payload de la orden adaptando 'origen' al campo 'canal' de tu base de datos
        orden_payload = {
            "id_mesa": datos_pedido.get("id_mesa"),
            "id_cliente_remoto": datos_pedido.get("id_cliente_remoto"),
            "origen": origen,  # Se guardará en la columna 'canal' de tu PedidoModelo
            "created_by": datos_pedido.get("created_by")
        }

        # 4. Invocamos la capa de acceso a datos (DAO) para realizar la inserción atómica
        resultado_dao = OrdenesDAO.insertar_orden_completa(db, orden_payload, items_procesados)
        return resultado_dao
