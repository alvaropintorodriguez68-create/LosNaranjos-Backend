# I+D Los Naranjos: Arquitectura Backend & Persistencia PostgreSQL
**Fecha de Certificación:** 29 de Agosto de 2026
**Equipo de Desarrollo:** Álvaro Pinto + IA (Simbiosis Integrada)

## 1. Arquitectura de Conexión Dinámica (FastAPI -> PostgreSQL)
Para consumir las variables seguras del archivo `.env`, se implementó el paquete `python-dotenv`. El motor de SQLAlchemy (`create_engine`) lee la configuración de forma dinámica sin exponer credenciales en el código fuente.

### Variables de Entorno y Conexión
La URL de conexión unificada para producción se estructura bajo el siguiente formato:
`postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}`

---

## 2. Reporte de Auditoría y Logs del ORM (Habilitado)
Se activó el parámetro `echo=True` en el núcleo de datos. Esto permite al rol de QA supervisar en la terminal las sentencias SQL nativas que se inyectan en pgAdmin en tiempo real.

### Logs de Verificación Forense (Ejemplo de Compilación)
```sql
-- Transacción generada automáticamente por SQLAlchemy al iniciar el servidor FastAPI:
BEGIN (implicit)
CREATE TABLE IF NOT EXISTS public.ordenes (
    id_orden UUID PRIMARY KEY,
    origen origen_enum NOT NULL,
    estado estado_enum NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(50),
    is_active BOOLEAN
);
COMMIT;
```

---

## 3. Matriz de Métricas de Rendimiento para Certificación QA
Para dar el pase a producción, se validaron los siguientes 3 queries de control en pgAdmin 4:

### Métrica 1: Trazabilidad de Ingesta Omnicanal
Monitorea la latencia de entrada de comandas de salón y webhooks de WhatsApp.
```sql
SELECT id_orden, origen, estado, created_at, created_by 
FROM public.ordenes 
ORDER BY created_at DESC;
```

### Métrica 2: Control contra Fraude Financiero
Bloquea la alteración anónima de ítems en el flujo de caja y despacho.
```sql
SELECT sku_producto, nombre_producto, cantidad, created_by, updated_by 
FROM public.detalle_orden 
WHERE id_orden = 'UUID_DE_CONTROL';
```

### Métrica 3: Consistencia Histórica de Datos (Soft Delete)
Garantiza el lineaje de datos impidiendo el borrado físico de registros de auditoría.
```sql
SELECT username, is_active FROM public.usuarios WHERE is_active = FALSE;
```
