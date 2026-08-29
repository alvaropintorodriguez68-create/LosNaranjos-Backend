from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uuid
from schemas import IngestaPedidoSchema

app = FastAPI(
    title="Sistema de Gestión Los Naranjos - API I+D",
    version="1.0.0",
    description="Endpoint Unificado para Ingesta Omnicanal con Auditoría QA"
)

# Permitir que nuestro mockup HTML interactúe con el Backend sin problemas de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/pedidos", status_code=status.HTTP_201_CREATED)
async def crear_pedido_universal(pedido: IngestaPedidoSchema):
    # Simulación QA: Validar consistencia del origen antes de la inserción lógica
    if pedido.origen == "salon" and not pedido.id_mesa:
        raise HTTPException(
            status_code=400, 
            detail="Error QA: Los pedidos de origen 'salon' deben incluir un 'id_mesa'."
        )
    if pedido.origen == "whatsapp" and not pedido.id_cliente_remoto:
        raise HTTPException(
            status_code=400, 
            detail="Error QA: Los pedidos de origen 'whatsapp' deben incluir un 'id_cliente_remoto'."
        )

    # Simulación de la inserción en PostgreSQL (Generación de UUIDs y cálculo de totales)
    id_orden_generado = uuid.uuid4()
    total_neto = sum(item.cantidad * item.precio_unitario for item in pedido.pedido_items)
    
    # Respuesta estructurada forense para el cliente o frontend
    return {
        "status": "success",
        "message": "JSON validado e insertado exitosamente en el ciclo operacional.",
        "data": {
            "id_orden": id_orden_generado,
            "origen": pedido.origen,
            "estado": "pendiente",
            "total_neto": total_neto,
            "creado_por": pedido.created_by,
            "items_insertados": len(pedido.pedido_items)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
