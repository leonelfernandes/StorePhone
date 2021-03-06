# -*- coding: utf-8 -*-
@auth.requires_membership(role='Administrador')
def inicio_compras():
    # definir los campos a obtener desde la base de datos:
    campos = db.proveedor.id, db.proveedor.nombre
    # definir la condición que deben cumplir los registros:
    criterio = db.proveedor.id>0
    ##criterio &= db.cliente.condicion_frente_al_iva=="Responsable Inscripto"
    # ejecutar la consulta:
    lista_proveedor = db(criterio).select(*campos)
    # revisar si la consulta devolvio registros:
    if not lista_proveedor:
        mensaje = "No ha cargado proveedor"
    else:
        mensaje = "Seleccione un proveedor"
        ##primer_cliente = lista_clientes[0]
    return dict(message=mensaje, lista_proveedor=lista_proveedor)

@auth.requires_membership(role='Administrador')
def detalle_compras():
    # si el usuario completo el formulario, extraigo los valores de los campos:
    if request.vars["boton_enviar"]:
        # obtengo los valores completados en el formulario
        id_proveedor = request.vars["id_proveedor"]
        fecha = request.vars["fecha"]
        nro_comprobante = request.vars["numero_comprobante"]
        # guardo los datos elegidos en la sesión
        session["id_proveedor"] = id_proveedor
        session["fecha"] = fecha
        session["nro_comprobante"] = nro_comprobante
        session["items_venta"] = []
    if request.vars["agregar_item"]:
        # obtengo los valores del formulario
        id_articulo = request.vars["id_producto"]
        cantidad = int(request.vars["cantidad"])
        precio = float(request.vars["precio"])
        item = {"id": id_articulo, "cantidad": cantidad}
        # busco en la base de datos el registro del producto seleccionado
        reg_producto = db(db.articulo.id_articulo==id_articulo).select().first()
        item["nombre"] = reg_producto.nombre
        item["precio"] = precio #reg_producto.precio
        # guardo el item en la sesión
        session["items_venta"].append(item)
    # busco en la base de datos al cliente para mostrar su info
    registros = db(db.proveedor.id==session["id_proveedor"]).select()
    reg_proveedor = registros[0]
    lista_articulos = db(db.articulo.id_articulo>0).select()
    # le pasamos las variables a la vista para armar el html
    return dict(id_proveedor=session["id_proveedor"], fecha=session["fecha"], 
                nro_cbte=session["nro_comprobante"], 
                reg_proveedor=reg_proveedor, lista_productos=lista_articulos,
                items_venta=session["items_venta"])

@auth.requires_membership(role='Administrador')
def confirmar():
    reg_proveedor = db(db.proveedor.id==session["id_proveedor"]).select().first()
    total = 0
    for item in session["items_venta"]:
        total += item["precio"] * item["cantidad"]
    return dict (mensaje= "Finalizar venta", 
                id_proveedor=session["id_proveedor"], fecha=session["fecha"], 
                nro_cbte=session["nro_comprobante"], 
                reg_proveedor=reg_proveedor, total=total)

@auth.requires_membership(role='Administrador')
def guardado():
    # Agregar los registros a la base de datos:
    for item in session ["items_venta"]:
        db.compras.insert(
            N_Factura=session["nro_comprobante"],
            #fecha=session["fecha"],
            p_unitario= item["precio"],
            proveedor= session["id_proveedor"],
            id_articulo=item["id"],
            cantidad= item["cantidad"],
            total= item ["precio"] * item["cantidad"]
            )
    # encabezado:
    nuevo_id_venta = db.compras.insert(
        cliente=session["id_cliente"],
        N_Factura=session["nro_comprobante"],
        fecha=session["fecha"],
        )
    # detalle (productos)
    for item in session["items_venta"]:
        db.compras_por_articulo.insert(
            venta=nuevo_id_venta,
            articulo=item["id"],
            cantidad=item["cantidad"],
            subtotal=item["precio"]
            )
        # descontar el stock
        articulo = db(db.articulo.id==item["id"]).select().first()
        stock_actual = articulo.stock
        db(db.articulo.id==item["id"]).update(stock=stock_actual-item["cantidad"])
    return dict (mensaje= "Se guardo con exito el comprobante id=%s" % nuevo_id_venta,
                 id_venta=nuevo_id_venta)

@auth.requires_membership(role='Administrador')
def listado():
    "Listado de las compras que se realizo"
    datos_compras=db().select(db.compras.ALL)
    return dict (c=datos_compras)
