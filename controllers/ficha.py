# -*- coding: utf-8 -*-
# try something like

def index():
    "pagina de inicio del catalogo"
    datos_articulo=db(db.articulo.id==request.args[0]).select()
    return dict (da=datos_articulo)

def caracteristicas():
    "pagina caracteristicas de celulares"
    datos_articulos=db(db.articulo.id==request.args[0]).select(db.articulo.ALL)
    return dict(da = datos_articulos)

def comparacion():
    if not session.id_articulo1:
        #seleccionamos el primer articulo
        session.id_articulo1=request.args[0]
        #para que aparezca un mensaje 
        session.flash="Seleccione el segundo articulo que desea comparar"
        #redireccionamos hacia el catalogo
        redirect(URL(c="default", f="index"))
    else:
        #seleccionamos el segundo articulo
        session.id_articulo2=request.args[0]
        #Comparamos el id de ssesion con el de la base de datos y lo GUARDAMOS EN q
    q = db.articulo.id==session.id_articulo1    
    datos_articulo1 = db(q).select().first()
    q = db.articulo.id==session.id_articulo2
    datos_articulo2 = db(q).select().first()
    return dict(d1=datos_articulo1, d2=datos_articulo2,)

def volver():
    #borramos los articulos seleccionados, para realizar una nueva comparacion
    del session.id_articulo1
    del session.id_articulo2
    redirect(URL(c="default", f="index"))
