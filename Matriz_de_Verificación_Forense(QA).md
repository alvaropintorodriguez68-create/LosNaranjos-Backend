Fase de Cierre: Matriz de Verificación Forense (QA)Para dejar el proyecto listo para pasar a producción, el rol de QA debe certificar el comportamiento del sistema mediante pruebas controladas. Estas son las tres consultas SQL clave que utilizaremos en tu panel de pgAdmin para validar que la inyección de datos sea perfecta:Métrica 1: Verificación de Ingesta Omnicanal (Tiempos de Respuesta)Para medir la velocidad con la que entran los pedidos desde la interfaz o el webhook de WhatsApp, ejecuta este comando para auditar la creación:sqlSELECT id_orden, origen, estado, created_at, created_by 
FROM public.ordenes 
ORDER BY created_at DESC;
Usa el código con precaución.Métrica 2: Auditoría Forense de Trazabilidad (Campos QA)Para certificar que ningún registro sea alterado de forma anónima o fraudulenta en la caja o cocina, usaremos esta consulta sobre los detalles:sqlSELECT sku_producto, nombre_producto, cantidad, created_by, updated_by 
FROM public.detalle_orden 
WHERE id_orden = 'ID_DE_PRUEBA';
Usa el código con precaución.Métrica 3: Control de Borrado Lógico (Soft Delete)Para validar que la aplicación no elimine filas físicas del disco duro de Los Naranjos, asegurando la consistencia de los reportes de Excel, comprobaremos el estado lógico:sqlSELECT username, is_active FROM public.usuarios;
-- Si un usuario es dado de baja, is_active cambiará a FALSE, pero el registro permanecerá para auditoría.
Usa el código con precaución.