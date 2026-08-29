# negocios/logica.py
import io
import jwt
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from datos import datos  
from datos.config_bd import logger_negocio

# Modelos del nuevo ecosistema relacional de 10 tablas
# En negocios/logica.py - Asegúrate de que la importación de modelos sea esta:

from datos.modelos import PedidoModelo, DetallePedidoModelo, ProductoModelo, UsuarioModelo

from negocios.dtos import PedidoCrearDTO

SECRET_KEY = "MI_CLAVE_SECRETA_SUPER_SEGURA_PARA_LOS_NARANJOS"
ALGORITHM = "HS256"

# =====================================================================
#        PATRÓN FACTORY: CONSTRUCTOR SEGURO DE ENTIDADES RELACIONALES
# =====================================================================
class PedidoFactory:
    @staticmethod
    def crear_estructura_pedido(dto: PedidoCrearDTO, usuario_auditoria: str) -> PedidoModelo:
        """Instancia la cabecera del pedido aplicando reglas base y metadatos de auditoría."""
        return PedidoModelo(
            id_sucursal=dto.id_sucursal,
            id_mesa=dto.id_mesa,
            id_cliente=dto.id_cliente,
            id_usuario=dto.id_usuario,
            canal=dto.canal,
            estado="Pendiente",
            fecha_hora=datetime.now(timezone.utc),
            UsuarioCreacion=usuario_auditoria,
            EstadoTupla=True
        )

# =====================================================================
#                      NUEVA LÓGICA DE PEDIDOS RELACIONALES
# =====================================================================
def procesar_apertura_pedido(db: Session, dto: PedidoCrearDTO, usuario_auditoria: str):
    """Valida existencias, calcula totales, inserta en Postgres de forma atómica y audita."""
    if not dto.detalles:
        logger_negocio.warning(f"OPERACIÓN RECHAZADA | El usuario '{usuario_auditoria}' intentó abrir un pedido sin artículos.")
        raise ValueError("Un pedido debe contener al menos un producto en su detalle.")

    try:
        nuevo_pedido = PedidoFactory.crear_estructura_pedido(dto, usuario_auditoria)
        db.add(nuevo_pedido)
        db.flush()  # Envía a Postgres para obtener el id_pedido sin confirmar commit

        total_neto = 0.0

        for item in dto.detalles:
            producto = db.query(ProductoModelo).filter(
                ProductoModelo.id_producto == item.id_producto, 
                ProductoModelo.EstadoTupla == True
            ).first()

            if not producto:
                raise ValueError(f"El artículo con ID {item.id_producto} no existe o está inactivo.")

            total_neto += (producto.precio * item.cantidad)

            nuevo_detalle = DetallePedidoModelo(
                id_pedido=nuevo_pedido.id_pedido,
                id_producto=item.id_producto,
                cantidad=item.cantidad,
                precio_unitario=producto.precio,
                observaciones=item.observaciones,
                UsuarioCreacion=usuario_auditoria,
                EstadoTupla=True
            )
            db.add(nuevo_detalle)

        db.commit()
        db.refresh(nuevo_pedido)

        total_con_iva = round(total_neto * 1.19, 2)
        logger_negocio.info(
            f"TRANSACCIÓN EXITOSA | Pedido N°{nuevo_pedido.id_pedido} registrado por '{usuario_auditoria}'. "
            f"Total Neto: ${total_neto} | Total con IVA: ${total_con_iva}"
        )
        
        return {
            "id_pedido": nuevo_pedido.id_pedido,
            "estado": nuevo_pedido.estado,
            "total_neto": total_neto,
            "total_con_iva": total_con_iva,
            "mensaje": "Pedido y detalles grabados atómicamente en PostgreSQL"
        }

    except Exception as e:
        db.rollback()
        logger_negocio.error(f"SISTEMA CRÍTICO | Error al procesar pedido. Rollback ejecutado: {str(e)}")
        raise e

# ==========================================
#          LÓGICA DE PRODUCTOS (HISTÓRICO)
# ==========================================
# En negocios/logica.py - Asegúrate de reemplazar esta función por completo:

def listar_productos_procesados(db: Session):
    """Recibe la sesión de la BD, obtiene los objetos y procesa el IVA."""
    logger_negocio.info("CONEXIÓN POOL | Consulta masiva de productos ejecutada desde el Singleton.")
    
    # IMPORTANTE: Forzamos la consulta sobre el nuevo ProductoModelo expandido de 10 tablas
    productos_orm = db.query(ProductoModelo).filter(ProductoModelo.EstadoTupla == True).all()
    
    lista_procesada = []
    for p in productos_orm:
        lista_procesada.append({
            "id_producto": p.id_producto, # Mapeamos 'id_producto' (Clave primaria en tu pgAdmin)
            "nombre": p.nombre,
            "precio": p.precio,           # Mapeamos 'precio' (Columna de tu pgAdmin)
            "precio_con_iva": round(p.precio * 1.19, 2) # Cálculo dinámico con el IVA de Chile
        })
    return lista_procesada


# En negocios/logica.py - Reemplaza estas dos funciones:

def registrar_nuevo_producto(db: Session, nombre: str, precio: float, usuario_auditoria: str):
    """
    Registra o reactiva un producto (Upsert). 
    Si ya existe inactivo (EstadoTupla=False), lo enciende y actualiza metadatos.
    """
    nombre_limpio = nombre.strip()
    if not nombre_limpio:
        logger_negocio.warning(f"Intento fallido de creación de producto por '{usuario_auditoria}': Nombre vacío.")
        raise ValueError("El nombre del producto no puede estar vacío.")
    if precio <= 0:
        logger_negocio.warning(f"Intento fallido de creación de producto '{nombre_limpio}' por '{usuario_auditoria}': Precio inválido (${precio}).")
        raise ValueError("El precio debe ser mayor a cero.")
        
    # VERIFICACIÓN DE EXISTENCIA PREVIA (Incluso los ocultos lógicamente)
    producto_existente = db.query(ProductoModelo).filter(
        ProductoModelo.nombre == nombre_limpio
    ).first()

    if producto_existente:
        if producto_existente.EstadoTupla == True:
            # Si ya está activo, no permitimos duplicarlo
            raise ValueError("El producto ya se encuentra registrado y activo en el inventario.")
        else:
            # ¡REACTIVACIÓN TRANSACCIONAL! (Resuelve el error de inserción repetida)
            producto_existente.EstadoTupla = True
            producto_existente.precio = precio
            producto_existente.UsuarioModificacion = usuario_auditoria
            db.commit()
            logger_negocio.info(f"FINANZAS | Producto '{nombre_limpio}' reactivado con nuevo precio de ${precio} por '{usuario_auditoria}'.")
            return

    # Si el producto es genuinamente nuevo, se inserta en Postgres
    nuevo_prod = ProductoModelo(
        nombre=nombre_limpio,
        precio=precio,
        categoria="General",
        UsuarioCreacion=usuario_auditoria,
        EstadoTupla=True
    )
    db.add(nuevo_prod)
    db.commit()
    logger_negocio.info(f"OPERACIÓN exitosa | Usuario: '{usuario_auditoria}' creó el producto '{nombre_limpio}' con precio de ${precio}.")


def procesar_eliminacion(db: Session, id_producto: int, usuario_auditoria: str):
    """Valida y procesa el borrado lógico usando la columna id_producto del MVP."""
    if id_producto <= 0:
        logger_negocio.warning(f"Intento de eliminación inválido por '{usuario_auditoria}' con ID: {id_producto}.")
        raise ValueError("El ID del producto no es válido.")
        
    # CORRECCIÓN CLAVE: Buscamos explícitamente por 'id_producto' en lugar de 'id'
    producto = db.query(ProductoModelo).filter(ProductoModelo.id_producto == id_producto).first()
    
    if not producto:
        raise ValueError("El producto seleccionado no existe en la base de datos.")

    # Ejecutamos la mutación de estado a nivel de base de datos
    producto.EstadoTupla = False
    producto.UsuarioModificacion = usuario_auditoria
    db.commit()
    logger_negocio.info(f"OPERACIÓN de baja lógica | Usuario: '{usuario_auditoria}' desactivó el producto ID: {id_producto}.")

def generar_csv_productos(db, usuario_auditoria: str):
    """Genera el reporte gerencial extrayendo los datos y la metadata de auditoría completa."""
    from datos.modelos import ProductoModelo as PM
    productos_orm = db.query(PM).all()
    
    output = io.StringIO()
    output.write("ID;Nombre;Precio Neto;Precio con IVA (19%);Creado Por;Fecha Creacion;Modificado Por;Fecha Modificacion;Estado Registro\n")
    
    for p in productos_orm:
        precio_iva = round(p.precio * 1.19, 2)
        fecha_c = p.FechaCreacion.strftime("%Y-%m-%d %H:%M:%S") if p.FechaCreacion else ""
        fecha_m = p.FechaModificacion.strftime("%Y-%m-%d %H:%M:%S") if p.FechaModificacion else "Sin modificaciones"
        usuario_m = p.UsuarioModificacion if p.UsuarioModificacion else "N/A"
        estado_texto = "ACTIVO" if p.EstadoTupla else "ELIMINADO LÓGICO"
        
        output.write(f"{p.id_producto};{p.nombre};{p.precio};{precio_iva};{p.UsuarioCreacion};{fecha_c};{usuario_m};{fecha_m};{estado_texto}\n")
    
    output.seek(0)
    logger_negocio.info(f"REPORTE GENERAL | Usuario: '{usuario_auditoria}' exportó la auditoría completa a CSV corporativo.")
    return output.getvalue()

# ==========================================
#      LOGICA DE USUARIOS / SEGURIDAD (HISTÓRICO)
# ==========================================
# En negocios/logica.py - Reemplaza las funciones de autenticación por estas:

def registrar_nuevo_usuario(db: Session, username: str, contrasena: str):
    """Procesa e inscribe un nuevo usuario adaptado al modelo PostgreSQL."""
    if len(contrasena) < 6:
        logger_negocio.warning(f"REGISTRO fallido | Clave muy corta para: '{username}'.")
        raise ValueError("La contraseña debe tener al menos 6 caracteres.")
    
    # Verificamos si ya existe el nombre de usuario único
    existe = db.query(UsuarioModelo).filter(UsuarioModelo.username == username).first()
    if existe:
        logger_negocio.error(f"REGISTRO duplicado | El usuario '{username}' ya existe.")
        raise ValueError("El nombre de usuario ya existe en el sistema.")
        
    password_hashed = hashlib.sha256(contrasena.encode('utf-8')).hexdigest()
    
    nuevo_usuario = UsuarioModelo(
        username=username,
        password_hashed=password_hashed,
        UsuarioCreacion="sistema",
        EstadoTupla=True
    )
    db.add(nuevo_usuario)
    db.commit()
    logger_negocio.info(f"SEGURIDAD | Nuevo usuario registrado: '{username}'.")

# En negocios/logica.py - Asegúrate de que este bloque final esté bien alineado a la izquierda:

def autenticar_usuario(db: Session, username: str, contrasena: str):
    """Compara hashes y firma el JWT consultando directamente sobre el nuevo modelo."""
    usuario = db.query(UsuarioModelo).filter(
        UsuarioModelo.username == username,
        UsuarioModelo.EstadoTupla == True
    ).first()
    
    if not usuario:
        logger_negocio.warning(f"AUTENTICACIÓN fallida | Usuario inexistente: '{username}'.")
        raise ValueError("Usuario o contraseña incorrectos.")
        
    hash_ingresado = hashlib.sha256(contrasena.encode('utf-8')).hexdigest()
    if hash_ingresado != usuario.password_hashed:
        logger_negocio.warning(f"AUTENTICACIÓN fallida | Clave errónea para: '{username}'.")
        raise ValueError("Usuario o contraseña incorrectos.")
        
    tiempo_expiracion = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {"sub": username, "exp": tiempo_expiracion}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    logger_negocio.info(f"SEGURIDAD | Acceso concedido a '{username}'. JWT firmado con éxito.")
    return token


def verificar_token_jwt(token: str):
    """Valida la firma criptográfica enviada por el navegador web."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        logger_negocio.warning("SEGURIDAD | Se rechazó una petición de API: El token JWT ha expirado.")
        raise ValueError("El token ha expirado. Inicia sesión nuevamente.")
    except jwt.InvalidTokenError:
        logger_negocio.error("SEGURIDAD Alerta | Intento de acceso con Token JWT inválido.")
        raise ValueError("Token inválido o corrupto.")

# Agregar al final de negocios/logica.py
from datos.modelos import CuentaCreditoModelo, MovimientoCreditoModelo, ClienteModelo

def procesar_movimiento_credito(db: Session, dto: MovimientoCreditoCrearDTO, usuario_auditoria: str):
    """
    Controlador Financiero: Gestiona consumos y abonos sobre la línea de crédito.
    Aplica reglas estrictas de límite de saldo y guarda traza total en Postgres.
    """
    # 1. Buscamos si el cliente tiene una cuenta de crédito activa
    cuenta = db.query(CuentaCreditoModelo).filter(
        CuentaCreditoModelo.id_cliente == dto.id_cliente,
        CuentaCreditoModelo.EstadoTupla == True
    ).first()

    if not cuenta:
        # Si no existe, la Factory la autogenera en el momento (Inscripción flexible)
        cuenta = CuentaCreditoModelo(
            id_cliente=dto.id_cliente,
            saldo=0.0,
            limite_credito=100000.0, # Límite por defecto chileno ($100.000)
            UsuarioCreacion=usuario_auditoria,
            EstadoTupla=True
        )
        db.add(cuenta)
        db.flush()

    # 2. Aplicamos reglas de negocio contables según el tipo de movimiento
    monto_operacion = dto.monto
    tipo = dto.tipo_movimiento.strip().capitalize()

    if tipo in ["Consumo"]:
        # Validación de riesgo: No puede sobrepasar el límite de crédito aprobado
        if (cuenta.saldo + monto_operacion) > cuenta.limite_credito:
            logger_negocio.warning(f"CRÉDITO RECHAZADO | Cliente ID {dto.id_cliente} sobrepasó límite. Intento: ${monto_operacion}")
            raise ValueError(f"Operación rechazada: Supera el límite de crédito disponible. Límite: ${cuenta.limite_credito}")
        
        cuenta.saldo += monto_operacion

    elif tipo in ["Abono", "Prepago"]:
        # Los abonos disminuyen la deuda del cliente
        cuenta.saldo -= monto_operacion
    else:
        raise ValueError("Tipo de movimiento inválido. Use: Consumo, Abono o Prepago.")

    # 3. Registramos la línea histórica en la tabla de movimientos para la auditoría de Raúl
    nuevo_movimiento = MovimientoCreditoModelo(
        id_cuenta_credito=cuenta.id_cuenta_credito,
        tipo_movimiento=tipo,
        monto=monto_operacion,
        referencia=dto.referencia,
        UsuarioCreacion=usuario_auditoria,
        EstadoTupla=True
    )
    
    try:
        db.add(nuevo_movimiento)
        db.commit()
        
        logger_negocio.info(
            f"FINANZAS | Movimiento {tipo} procesado por '{usuario_auditoria}' para Cliente ID {dto.id_cliente}. "
            f"Monto: ${monto_operacion} | Nuevo Saldo Deuda: ${cuenta.saldo}"
        )
        return {
            "id_movimiento": nuevo_movimiento.id_movimiento,
            "tipo": tipo,
            "monto": monto_operacion,
            "saldo_deuda_actual": cuenta.saldo,
            "cupo_disponible": cuenta.limite_credito - cuenta.saldo,
            "estado": "Confirmado"
        }
    except Exception as e:
        db.rollback()
        logger_negocio.error(f"CRÍTICO FINANZAS | Fallo al asentar movimiento de crédito: {str(e)}")
        raise e
# En negocios/logica.py - Asegúrate de pegar esto al final absoluto alineado al margen izquierdo:

def registrar_nuevo_cliente(db: Session, dto: ClienteCrearDTO, usuario_auditoria: str):
    """Valida la unicidad del RUT y guarda el cliente mapeando la auditoría."""
    from datos.modelos import ClienteModelo
    rut_limpio = dto.rut.strip()
    
    # Evitamos duplicidad transaccional del mismo RUT
    existe = db.query(ClienteModelo).filter(ClienteModelo.rut == rut_limpio).first()
    if existe:
        if existe.EstadoTupla:
            raise ValueError("El RUT ya se encuentra registrado en el sistema ERP.")
        else:
            # Upsert: Reactivamos la fila histórica si estaba oculta lógico
            existe.EstadoTupla = True
            existe.nombre = dto.nombre.strip()
            existe.telefono = dto.telefono
            existe.UsuarioModificacion = usuario_auditoria
            db.commit()
            return {"mensaje": "Cliente reactivado con éxito en PostgreSQL"}

    # Inserción pura de entidad del MVP gastronómico
    nuevo_cliente = ClienteModelo(
        nombre=dto.nombre.strip(),
        rut=rut_limpio,
        telefono=dto.telefono,
        email=dto.email,
        direccion=dto.direccion,
        tipo_cliente=dto.tipo_cliente,
        observaciones=dto.observaciones,
        UsuarioCreacion=usuario_auditoria,
        EstadoTupla=True
    )
    db.add(nuevo_cliente)
    db.commit()
    logger_negocio.info(f"MANTENCIÓN | Cliente '{dto.nombre}' dado de alta exitosamente por {usuario_auditoria}.")
    return {"mensaje": "Cliente registrado de forma exitosa"}


def listar_clientes_activos(db: Session):
    """Consulta masiva de clientes vivos para la grilla analítica del ERP."""
    from datos.modelos import ClienteModelo
    return db.query(ClienteModelo).filter(ClienteModelo.EstadoTupla == True).all()
