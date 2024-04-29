from flask import Flask, render_template, request, session
from datetime import datetime, timedelta
import db
from models import Producto, Cliente, VentaCliente, Proveedor, Rol, ProductoProveedor, CompraProveedor
from flask_wtf import Form
from wtforms.fields import DateField
import matplotlib.pyplot as plt
from sqlalchemy import func, cast, Float, case

from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = '12345aA'

@app.route("/")
def home():
    session.clear() #Limipieza de sesion si salimos
    return render_template("index.html")


@app.route('/bitsbytes', methods=['POST'])
def login():
    usuario = request.form['user'].upper()
    #Consulta que nos devulve el usuario que han introducido por pantalla
    usertrue = db.session.query(Cliente).filter(Cliente.dni == usuario).first()
    password = request.form['password']

    if usertrue != None and usertrue.password == password:
        #Inicializamos una variable de sesion para saber siempre el ususario que esta activo
        session['usuario'] = request.form['user'].upper()
        #Consulta que nos dice si tenemos un stock más bajo de 90%
        aviso_stock = db.session.query(Producto).filter(Producto.stock < 0.9 * Producto.max_stock).all()
        return render_template("bitsbytes.html",
                               aviso_stock=aviso_stock,
                               admin=admin(usertrue.rol),
                               usuario=usertrue.nombre)
    else:
        mensaje = "Usuario o contraseña incorrectos."

    return render_template('index.html', mensaje=mensaje)

#------------------------------------------------------------
#-----Apartado Redireccón Producto/Cliente/Proveedor--------
#------------------------------------------------------------
'''
Explicación de lo que se ve siempre en los return de cada función

Llamamos a la función y nos devuelve el usuario conectado, de ese usuario cogemos el dato del Rol,
entonces si es 1, se pasara al hmtl como valor 1 y se reconocera como admin, si lo contrario será Básico.
------> admin=admin(usuarioactivo().rol)

Llamamos a la función y nos devuelve el usuario conectado, cogemos el nombre del usuario y se lo añadimos 
a la variable para que pase al html para que se vea siempre el nombre del usuario conectado.
------> usuario=usuarioactivo().nombre

Le pasamos a la variable el nombre de la sección del menu para que este activo cuando entremos
------> activo='productos'


Estas variables lo que hacen es llamar a la función -- mostrartodo("nombre de la lista") -- y le pasamos 
el nombre de la tabla de la cual queremos todos los datos.
------> lista_productos
------> lista_proveedor
------> lista_cliente
------> roles
'''

@app.route('/inicio')
def inicio():
    # Consulta que nos dice si tenemos un stock más bajo de 90%
    aviso_stock = db.session.query(Producto).filter(Producto.stock < 0.9 * Producto.max_stock).all()
    return render_template('bitsbytes.html',
                           aviso_stock=aviso_stock,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre)

@app.route('/productos')
def productos():
    return render_template('productos.html',
                           lista_productos=mostrartodo("Producto"),
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='productos')

@app.route('/for-crear-producto')
def forCrearProducto():
    return render_template('crearproducto.html',
                           lista_productos=mostrartodo("Producto"),
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           proveedor=mostrartodo("Proveedor"),
                           activo='productos')

@app.route('/asociar')
def asociarProductoProveedor():
    return render_template('asociarproductoproveedor.html',
                           lista_productos=mostrartodo("Producto"),
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           lista_proveedor=mostrartodo("Proveedor"),
                           activo='productos')

@app.route('/cliente')
def cliente():
    return render_template('anadircliente.html',
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           roles=mostrartodo("Rol"),
                           activo='clientes')

@app.route('/for-editar-cliente')
def forEditarCliente():
    return render_template('editarcliente.html',
                           lista_cliente=mostrartodo("Cliente"),
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           roles=mostrartodo("Rol"),
                           activo='clientes')

@app.route('/editar-proveedor')
def editarProveedor():
    return render_template('editarproveedor.html',
                           lista_proveedor=mostrartodo("Proveedor"),
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='proveedor')

@app.route('/perfil')
def perfil():
    return render_template('perfil.html',
                           admin=admin(usuarioactivo().rol),
                           user=usuarioactivo(),
                           usuario=usuarioactivo().nombre,
                           activo='perfil')

@app.route('/proveedor')
def proveedor():
    return render_template('crearproveedor.html',
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='proveedor')

@app.route('/lista-proveedor')
def listaProveedor():
    return render_template('listadoproveedor.html',
                           lista_proveedor=mostrartodo("Proveedor"),
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='proveedor')

@app.route('/lista-cliente')
def listaCliente():
    return render_template('listadoclientes.html',
                           lista_cliente=mostrartodo("Cliente"),
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           roles=mostrartodo("Rol"),
                           activo='clientes')
@app.route('/password')
def password():
    return render_template('modificarpassword.html',
                           lista_cliente=mostrartodo("Cliente"),
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='perfil')

@app.route('/tarifas-proveedor/<id_producto>')
def tarifasProveedor(id_producto):
    # Consulta que devuelve el nombre de la empresa del proveedor, el precio del producto que suministra y
    # el ID del proveedor para todos los productos que coinciden con el ID proporcionado
    proveedores = db.session.query(Proveedor.nombre_empresa, ProductoProveedor.precio, Proveedor.id_proveedor). \
                    join(ProductoProveedor).filter(ProductoProveedor.id_producto == int(id_producto)).all()
    # Consulta un producto específico en la BD por su ID y devuelve ese producto si existe, o si no existe None.
    producto = db.session.query(Producto).filter(Producto.id_producto == int(id_producto)).first()
    return render_template('tarifasproductos.html',
                           lista_proveedor=proveedores,
                           producto=producto,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='productos')

@app.route("/for-pedido-proveedor/<id_proveedor>/<id_producto>/<precio>", methods=["POST"])
def forPedidoProveedor(id_proveedor, id_producto, precio):
    # Consulta un proveedor específico en la BD por su ID y devuelve ese proveedor si existe, o si no existe None.
    proveedor = db.session.query(Proveedor).filter(Proveedor.id_proveedor == int(id_proveedor)).first()
    # Consulta un producto específico en la BD por su ID y devuelve ese producto si existe, o si no existe None.
    producto = db.session.query(Producto).filter(Producto.id_producto == int(id_producto)).first()

    return render_template('entradapedidoproveedor.html',
                           precio_producto=precio,
                           proveedor=proveedor,
                           producto=producto,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='productos')

@app.route("/lista-pedidos-proveedor")
def listaPedidosProveedor():
    consulta = db.session.query(Producto, Proveedor, CompraProveedor). \
        select_from(Producto). \
        join(CompraProveedor, Producto.id_producto == CompraProveedor.id_producto). \
        join(Proveedor, Proveedor.id_proveedor == CompraProveedor.id_proveedor). \
        all()

    form = FechaForm()  # Instanciamos la clase
    return render_template('listapedidosproveedor.html',
                           lista_pedido_proveedor=consulta,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           form=form,
                           activo='proveedor')

@app.route("/pedido-cliente/<id>")
def pedidoCliente(id):
    producto = db.session.query(Producto).filter(Producto.id_producto == id).first()
    return render_template('pedidocliente.html',
                           producto=producto,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='productos')

@app.route("/lista-pedido-cliente")
def listaPedidoCliente():
    lista_pedidos = db.session.query(Producto, Cliente, VentaCliente). \
                     select_from(Producto). \
                     join(VentaCliente, Producto.id_producto == VentaCliente.id_producto). \
                     join(Cliente, Cliente.id_cliente == VentaCliente.id_cliente).\
                     filter(Cliente.id_cliente == usuarioactivo().id_cliente).all()

    form = FechaForm()  # Instanciamos la clase

    return render_template('listapedidocliente.html',
                           lista_pedido_cliente=lista_pedidos,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           form=form,
                           activo='perfil')

@app.route("/todos-pedidos-clientes")
def todosPedidosClientes():
    lista_pedidos = db.session.query(Producto, Cliente, VentaCliente). \
                     select_from(Producto). \
                     join(VentaCliente, Producto.id_producto == VentaCliente.id_producto). \
                     join(Cliente, Cliente.id_cliente == VentaCliente.id_cliente).all()

    form = FechaForm()  # Instanciamos la clase

    return render_template('todospedidosclientes.html',
                           lista_pedido_cliente=lista_pedidos,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           form=form,
                           activo='clientes')

@app.route("/graficas-ventas")
def graficasVentas():
    # Consulta SQLAlchemy para obtener los datos de ventas por producto
    ventas_por_producto = db.session.query(
        Producto.nombre,
        func.sum(VentaCliente.cantidad).label('total_ventas')
    ). \
        join(VentaCliente, Producto.id_producto == VentaCliente.id_producto). \
        group_by(Producto.nombre).all()

    # Procesar los datos para la gráfica
    nombres_productos = [venta[0] for venta in ventas_por_producto]
    total_ventas = [venta[1] for venta in ventas_por_producto]

    # Crear una lista de colores para las barras
    colores = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta', 'yellow', 'brown', 'gray']

    # Crear la gráfica de ventas
    plt.figure(figsize=(10, 6))
    plt.bar(nombres_productos, total_ventas, color=colores)
    #plt.xlabel('Producto')
    plt.ylabel('Total Ventas')
    #plt.title('Total de Ventas por Producto')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    # Guardar la gráfica en un archivo temporal
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Convertir la imagen en formato base64
    grafica_base64 = base64.b64encode(img.getvalue()).decode()

    return render_template('graficaventasmensuales.html',
                           grafica_base64=grafica_base64,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='grafico')


@app.route("/graficas-beneficios")
def graficasBeneficios():
    # Consulta SQLAlchemy para obtener los datos de ventas por producto
    ventas_producto = db.session.query(
        Producto.nombre,
        func.sum(VentaCliente.cantidad).label('total_ventas')). \
        join(VentaCliente, Producto.id_producto == VentaCliente.id_producto). \
        group_by(Producto.nombre).all()

    # Consulta SQLAlchemy para obtener los datos de beneficios por proveedor
    beneficios_proveedor = db.session.query(
        Proveedor.nombre_empresa,
        func.round(
            func.sum(
                Producto.precio -
                    (ProductoProveedor.precio * (1 - Proveedor.descuento / 100) * (1 + Proveedor.iva / 100))
            ), 2
        ).label('beneficio')
    ). \
        join(ProductoProveedor, Proveedor.id_proveedor == ProductoProveedor.id_proveedor). \
        join(Producto, Producto.id_producto == ProductoProveedor.id_producto). \
        group_by(Proveedor.nombre_empresa).all()

     # Procesar los datos para las gráficas
    nombres_productos = [venta[0] for venta in ventas_producto]
    total_ventas = [round(venta[1],2) for venta in ventas_producto]

    nombres_proveedores = [beneficio[0] for beneficio in beneficios_proveedor]
    beneficios = [round(beneficio[1],2) for beneficio in beneficios_proveedor]

    # Crear las gráficas
    fig, graficos = plt.subplots(1, 2, figsize=(12, 6))

    # Gráfico de ventas por producto
    graficos[0].bar(nombres_productos, total_ventas, color='blue')
    #graficos[0].set_xlabel('Producto')
    graficos[0].set_ylabel('Total Ventas')
    graficos[0].set_title('Ventas por Producto')
    graficos[0].tick_params(axis='x', rotation=45)

    # Agregar texto a las barras del gráfico de ventas por producto
    for i, valor in enumerate(total_ventas):
        graficos[0].text(i, valor, f'{valor}', ha='center', va='bottom')

    # Gráfico de beneficios por proveedor
    graficos[1].bar(nombres_proveedores, beneficios, color='green')
    #agraficos[1].set_xlabel('Proveedor')
    graficos[1].set_ylabel('Beneficio')
    graficos[1].set_title('Beneficios por Proveedor')
    graficos[1].tick_params(axis='x', rotation=45)

    # Agregar texto a las barras del gráfico de beneficios por proveedor
    for i, valor in enumerate(beneficios):
        graficos[1].text(i, valor, f'{valor} €', ha='center', va='bottom')

    # Ajustes de diseño
    plt.tight_layout()

    # Guardar la gráfica en un archivo temporal
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Convertir la imagen en formato base64
    grafica_base64 = base64.b64encode(img.getvalue()).decode()

    return render_template('graficobeneficios.html',
                           grafica_base64=grafica_base64,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='grafico')

@app.route("/estadisticas")
def estadisticas():
    # Calcular estadísticas de ventas
    total_ventas = db.session.query(func.sum(VentaCliente.total)).scalar()
    numero_ventas = db.session.query(func.count(VentaCliente.id_ventacliente)).scalar()

    ventas_por_producto = db.session.query(
        Producto.nombre, func.sum(VentaCliente.cantidad), func.sum(VentaCliente.total)). \
        join(VentaCliente, Producto.id_producto == VentaCliente.id_producto). \
        group_by(Producto.nombre).all()

    ventas_por_cliente = db.session.query(
        Cliente.nombre, func.count(VentaCliente.id_ventacliente), func.sum(VentaCliente.total)). \
        join(VentaCliente, Cliente.id_cliente == VentaCliente.id_cliente). \
        group_by(Cliente.nombre).all()

    # Calcular estadísticas de compras
    total_compras = db.session.query(func.round(func.sum(CompraProveedor.total)), 2).scalar()
    numero_compras = db.session.query(func.round(func.count(CompraProveedor.id_compraproveedor)),2).scalar()

    compras_por_proveedor = db.session.query(
        Proveedor.nombre_empresa, func.sum(CompraProveedor.cantidad), func.round(func.sum(CompraProveedor.total),2)). \
        join(CompraProveedor, Proveedor.id_proveedor == CompraProveedor.id_proveedor). \
        group_by(Proveedor.nombre_empresa).all()

    compras_por_producto = db.session.query(
            Producto.nombre,
            func.sum(CompraProveedor.cantidad),
            func.round(func.sum(CompraProveedor.total), 2)). \
        join(CompraProveedor, Producto.id_producto == CompraProveedor.id_producto). \
        group_by(Producto.nombre).all()


    return render_template('estadisticas.html',
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='grafico',
                           total_ventas=total_ventas,
                           numero_ventas=numero_ventas,
                           ventas_por_producto=ventas_por_producto,
                           total_compras=total_compras,
                           numero_compras=numero_compras,
                           compras_por_proveedor=compras_por_proveedor,
                           compras_por_producto=compras_por_producto,
                           ventas_por_cliente =ventas_por_cliente)


#------------------------------------------------------------
#-----Apartado Creación de Producto/Cliente/Proveedor--------
#------------------------------------------------------------

@app.route("/crear-producto", methods=["POST"])
def crearProducto():
    if request.form["nombre"] != "": #No se guarda una tarea que no tenga nada
        product = Producto(nombre=request.form["nombre"],
                           stock =request.form["stock"],
                           precio = request.form["precio"],
                           ean = request.form["ean"],
                           color = request.form["color"],
                           max_stock=request.form["stock_re"])

        db.session.add(product)
        db.session.commit()
        mensaje = ""
    else:
        mensaje = "Es necesario que tenga un nombre el producto."

    return render_template("productos.html",
                           lista_productos=mostrartodo("Producto"),
                           mensaje=mensaje,
                           admin=admin(usuarioactivo().rol),
                           usuario=session.get('usuario'),
                           activo='productos')

@app.route("/crear-cliente", methods=["POST"])
def crearCliente():
    rol = db.session.query(Rol).filter(Rol.name_rol == request.form["select_rol"]).first()

    dni = False
    for cli in mostrartodo("Cliente"):
        if cli.dni == request.form["dni"].upper():
            dni = True

    if request.form["nombre"] != "": #No se guarda una tarea que no tenga nada
        if dni == False:
            cliente = Cliente(nombre=request.form["nombre"],
                                dni =request.form["dni"].upper(),
                                apellidos = request.form["apellidos"],
                                direccion = request.form["direccion"],
                                provincia = request.form["provincia"],
                                cp = request.form["cp"],
                                email = request.form["email"],
                                telf=request.form["telf"],
                                password=request.form["password"],
                                rol=rol.id_rol)
            db.session.add(cliente)
            db.session.commit()
            mensaje = "Cliente Creado Correctamente"
        else:
            mensaje = "¡ERROR! - Este cliente ya existe."
    else:
        mensaje = "Es necesario que tenga un nombre el producto."

    return render_template("anadircliente.html",
                           mensaje=mensaje,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='clientes',
                           roles=mostrartodo("Rol"))

@app.route("/crear-proveedor", methods=["POST"])
def crearProveedor():
    if request.form["nombreEmpresa"] != "": #No se guarda una tarea que no tenga nada
        proveedor = Proveedor( nombre_empresa=request.form["nombreEmpresa"],
                                cif =request.form["cif"],
                                telf = request.form["telf"],
                                direccion = request.form["direccion"],
                                provincia = request.form["provincia"],
                                cp = request.form["cp"],
                                email = request.form["email"],
                                iva = request.form["iva"],
                                descuento = request.form["descuento"])
        db.session.add(proveedor)
        db.session.commit()
        mensaje = "El proveedor {} creado correctamente.".format(request.form["nombreEmpresa"])
    else:
        mensaje = "Es necesario que tenga el nomnbre de la empresa."

    return render_template("crearproveedor.html",
                           mensaje=mensaje,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='proveedor')

#Función que añade una compra de un producto con un proveedor
@app.route("/pedido-proveedor/<id_proveedor>/<id_producto>", methods=["POST"])
def pedidoProveedor(id_proveedor, id_producto):
    #Comprovamos que la cantidad del pedido no este en blanco(porque sin cantidad no hay pedido)
    if request.form["undcompra"] != "":
        iva = int(request.form["iva"]) /100 #Pasamos el IVA para luego hacer la formula
        #Calculamos el total con el iva incluildo para añadirlo al pedido
        total_descuento = float(request.form["precio"])*(1-(float(request.form["descuento"])/100))
        total = int(request.form["undcompra"]) * total_descuento * (1 + iva)
        fecha_hora_actual = datetime.now()  # Guardamos la fcha y la hora del pedido

        #Crearemos un nuevo regitro en la BD de la tabla que contecta el proveedor con el producto y añadimos los campos
        pedido = CompraProveedor(   id_producto=int(id_producto),
                                    id_proveedor=int(id_proveedor),
                                    cantidad=request.form["undcompra"],
                                    precio=request.form["precio"],
                                    descuento=request.form["descuento"],
                                    iva=request.form["iva"],
                                    total=total,
                                    fecha_compra=fecha_hora_actual.strftime("%Y-%m-%d %H:%M:%S"))

        #Hacemos la Actualizacion del stock del prodctuo ya que hemos hechoe un nuevo pedido de proveedor
        #Hacemos la consulta para que nos de el producto al que queremos actualizarle el stock
        actualizacion_stock = db.session.query(Producto).filter(Producto.id_producto == id_producto).first()
        #En esta liena sumanos el stock que ya teniamos con la cantidad que ha se ha pedido al proveedor
        actualizacion_stock.stock= int(actualizacion_stock.stock) + int(request.form["undcompra"])

        db.session.add(pedido)
        db.session.commit()
        mensaje = "Entrada Generado correctamente"
    else:
        mensaje = "Es necesario poner una cantidad de producto"

    return render_template("productos.html",
                           lista_productos=mostrartodo("Producto"),
                           mensaje=mensaje,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='productos')


@app.route("/crear-pedido-cliente/<id_producto>", methods=["POST"])
def crearPedidoCliente(id_producto):
    producto = db.session.query(Producto).filter(Producto.id_producto == id_producto).first()

    #Comprobamos que el campo cantidad no este vacio y que sea solo número y que la cantidad sea mayor que 0
    if request.form["cantidad"] != "" and request.form["cantidad"].isdigit() and int(request.form["cantidad"]) > 0:
        total = producto.precio * float(request.form["cantidad"]) #Calculamos el total del pedido
        iva = total * 0.21  # Sacamos el IVA del pedido
        fecha_hora_actual = datetime.now() #Guardamos la fcha y la hora del pedido

        venta = VentaCliente( id_cliente=usuarioactivo().id_cliente,
                              id_producto= id_producto,
                              cantidad= request.form["cantidad"],
                              precio= producto.precio,
                              fecha_compra= fecha_hora_actual.strftime("%Y-%m-%d %H:%M:%S"),
                              iva = round(iva, 2),
                              total =  round(total, 2))

        # Hacemos la Actualización del stock del producto, ya que hemos hecho un nuevo pedido de proveedor
        # Hacemos la consulta para que nos de el producto al que queremos actualizarle el stock
        actualizacion_stock = db.session.query(Producto).filter(Producto.id_producto == id_producto).first()
        # En esta liena sumamos el stock que ya teníamos con la cantidad que a se ha pedido al proveedor
        actualizacion_stock.stock = int(actualizacion_stock.stock) - int(request.form["cantidad"])

        db.session.add(venta)
        db.session.commit()
        form = FechaForm()
        lista_pedido_cliente = db.session.query(Producto, Cliente, VentaCliente). \
                                select_from(Producto). \
                                join(VentaCliente, Producto.id_producto == VentaCliente.id_producto). \
                                join(Cliente, Cliente.id_cliente == VentaCliente.id_cliente). \
                                filter(Cliente.id_cliente == usuarioactivo().id_cliente).all()
        return render_template("listapedidocliente.html",
                                admin=admin(usuarioactivo().rol),
                                lista_pedido_cliente=lista_pedido_cliente,
                                usuario=usuarioactivo().nombre,
                                form=form,
                                activo='perfil')
    else: #Sino Guardamos un mensaje de error para retornarlo
        mensaje = "¡CAMPO CANTIDAD INCORRECTO!"

    return render_template("pedidocliente.html",
                           mensaje=mensaje,
                           producto=producto,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='productos')


@app.route("/crear-asociar/<id>", methods=["POST"])
def crearAsociar(id):
    idProveedor = db.session.query(Proveedor).filter(Proveedor.nombre_empresa == request.form["select_proveedor"]).first()
    relacion_existente = db.session.query(Proveedor). \
                         join(ProductoProveedor). \
                         filter(ProductoProveedor.id_producto == id, ProductoProveedor.id_proveedor == idProveedor.id_proveedor).first()
    mensaje=""
    if request.form["precioproveedor"] != "":
        # Verificar si la relación existe
        if relacion_existente: #Si la relación ya existe, solo hacemos la actualizacion de precip
            actulizar_precio = db.session.query(ProductoProveedor).filter(
                ProductoProveedor.id_producto == int(id),
                ProductoProveedor.id_proveedor == idProveedor.id_proveedor).first()

            actulizar_precio.precio = request.form["precioproveedor"]
            db.session.commit()
            db.session.close()
        else:
            asociar = ProductoProveedor(id_producto=int(id),
                                        id_proveedor=idProveedor.id_proveedor,
                                        precio = request.form["precioproveedor"])

            db.session.add(asociar)
            db.session.commit()
            mensaje = "Producto asociado correctamente"
    else:
        mensaje = "Es necesario que tenga un Precio Proveedor."

    return render_template('asociarproductoproveedor.html',
                           lista_productos=mostrartodo("Producto"),
                           mensaje=mensaje,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           lista_proveedor=mostrartodo("Proveedor"),
                           activo='productos')

#------------------------------------------------------------
#-----Apartado Editar Producto/Cliente/Proveedor--------
#------------------------------------------------------------

@app.route("/editar-producto/<id>", methods=["POST"])
def editarProducto(id):
    producto = db.session.query(Producto).filter(Producto.id_producto == id).first()
    if request.form["nombre"] != "":
        producto.nombre = request.form["nombre"]
    if request.form["stock"] != "":
        producto.stock = request.form["stock"]
    if request.form["precio"] != "":
        producto.precio = request.form["precio"]
    if request.form["ean"] != "":
        producto.ean = request.form["ean"]
    if request.form["color"] != "":
        producto.color = request.form["color"]
    if request.form["maxstock"] != "":
        producto.max_stock = request.form["maxstock"]

    msg_correcto = "¡Producto " + producto.nombre + " modificado con éxito!"
    db.session.commit()
    db.session.close()

    return render_template("productos.html",
                           lista_productos=mostrartodo("Producto"),
                           msg_correcto=msg_correcto,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre)

@app.route('/editar-cliente/<id>', methods=["POST"])
def editarCliente(id):
    cliente = db.session.query(Cliente).filter(Cliente.id_cliente == id).first()
    lista_sin_dni_cliente = db.session.query(Cliente).filter(Cliente.dni != request.form["dni"].upper() ).all()
    rol = db.session.query(Rol).filter(Rol.name_rol == request.form["select_rol"]).first()
    dni = False

    for listadni in lista_sin_dni_cliente:
        if listadni.dni == request.form["dni"].upper():
            dni = True

    if request.form["nombre"] != "":  # No se guarda una tarea que no tenga nada
        if dni == False:
            cliente.nombre=request.form["nombre"]
            cliente.dni=request.form["dni"].upper()
            cliente.apellidos=request.form["apellidos"]
            cliente.direccion=request.form["direccion"]
            cliente.provincia=request.form["provincia"]
            cliente.cp=request.form["cp"]
            cliente.email=request.form["email"]
            cliente.telf=request.form["telf"]
            cliente.rol=rol.id_rol

            db.session.add(cliente)
            db.session.commit()
            mensaje = "¡Cliente modificado correctamente!"
        else:
            mensaje = "¡ERROR! - Este cliente ya existe."
    else:
        mensaje = "Es necesario que tenga un nombre de cliente."

    return render_template('editarcliente.html',
                           lista_cliente=mostrartodo("Cliente"),
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           roles=mostrartodo("Rol"),
                           activo='clientes')

@app.route('/editar-proveedor/<id>', methods=["POST"])
def modificarProveedor(id):
    proveedor = db.session.query(Proveedor).filter(Proveedor.id_proveedor == id).first()
    lista_sin_cif = db.session.query(Proveedor).filter(Proveedor.cif != request.form["cif"].upper()).all()
    cif = False

    for lista_cif in lista_sin_cif:
        if lista_cif.cif == request.form["cif"].upper():
            cif = True

    if request.form["nombre"] != "":  # No se guarda una tarea que no tenga nada
        if cif == False:
            proveedor.nombre_empresa=request.form["nombre"]
            proveedor.cif=request.form["cif"].upper()
            proveedor.direccion=request.form["direccion"]
            proveedor.provincia=request.form["provincia"]
            proveedor.cp=request.form["cp"]
            proveedor.email=request.form["email"]
            proveedor.telf=request.form["telf"]
            proveedor.iva=request.form["iva"]
            proveedor.descuento=request.form["descuento"]

            db.session.add(proveedor)
            db.session.commit()
            mensaje = "¡Proveedor modificado correctamente!"
        else:
            mensaje = "¡ERROR! - Este cliente ya existe."
    else:
        mensaje = "Es necesario que tenga un nombre de cliente."

    return render_template('editarproveedor.html',
                           lista_proveedor=mostrartodo("Proveedor"),
                           admin=admin(usuarioactivo().rol),
                           mensaje=mensaje,
                           usuario=usuarioactivo().nombre,
                           activo='proveedor')


@app.route('/editar-perfil', methods=["POST"])
def editarPerfil():
    perfil = db.session.query(Cliente).filter(Cliente.id_cliente == usuarioactivo().id_cliente).first()

    perfil.nombre = request.form["nombre"]
    perfil.apellidos = request.form["apellidos"]
    perfil.dni = request.form["dni"]
    perfil.direccion = request.form["direccion"]
    perfil.provincia = request.form["provincia"]
    perfil.cp = request.form["cp"]
    perfil.email = request.form["email"]
    perfil.telf = request.form["telf"]

    msg_correcto = "¡Perfil modificado correctamente!"
    db.session.commit()
    db.session.close()

    return render_template('perfil.html',
                           admin=admin(usuarioactivo().rol),
                           user=usuarioactivo(),
                           usuario=usuarioactivo().nombre,
                           activo='perfil',
                           msg_correcto=msg_correcto)


@app.route('/modificar-password', methods=["POST"])
def modificarPassword():

    antigua = request.form["oldpassword"]
    nueva = request.form["newpassword"]
    nueva1 = request.form["newpassword1"]

    if usuarioactivo().password == antigua:
        if nueva == nueva1 and nueva != '':
            info = 1
            usuarioactivo().password = request.form["newpassword"]
            db.session.commit()
            db.session.close()
        else:
            info = 2
    else:
        info = 3

    return render_template('modificarpassword.html',
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='perfil',
                           info=info)

#------------------------------------------------------------
#-----Apartado Eliminar Producto/Cliente/Proveedor--------
#------------------------------------------------------------

@app.route("/eliminar-producto/<id>")
def eliminarProducto(id):
    producto = db.session.query(Producto).filter_by(id_producto=int(id))
    msg_correcto = "¡Producto eliminado con éxito!"
    producto.delete()
    db.session.commit()

    return render_template("productos.html",
                           lista_productos=mostrartodo("Producto"),
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           msg_correcto=msg_correcto,
                           activo="productos")

@app.route("/eliminar-cliente/<id_cliente>")
def eliminarCliente(id_cliente):

    cliente = db.session.query(Cliente).filter_by(id_cliente=int(id_cliente)).first()

    if cliente.id_cliente != usuarioactivo().id_cliente:
        cliente.delete()
        db.session.commit()

    return render_template("listadoclientes.html",
                           lista_cliente=mostrartodo("Cliente"),
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           roles=mostrartodo("Rol"),
                           activo="clientes")

@app.route("/eliminar-proveedor/<id_proveedor>")
def eliminarproveedor(id_proveedor):
    proveedor = db.session.query(Proveedor).filter_by(id_proveedor=int(id_proveedor))
    msg_correcto = "¡Proveedor eliminado con éxito!"
    proveedor.delete()
    db.session.commit()

    return render_template("listadoproveedor.html",
                           lista_proveedor=mostrartodo("Proveedor"),
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           msg_correcto=msg_correcto,
                           activo="proveedor")

#------------------------------------------------------------
#-----Apartado Filtro Producto/Cliente/Proveedor--------
#------------------------------------------------------------

@app.route("/filtro-producto", methods=["POST"])
def filtrarProductos():

    filtro_id = request.form['filtro_id']
    filtro_nombre = request.form['filtro_nombre']
    filtro_precio_min = request.form['filtro_precio_min']
    filtro_precio_max = request.form['filtro_precio_max']

    if filtro_precio_max == "":
        filtro_precio_max = 100000000000

    productos = db.session.query(Producto)

    if filtro_id:
        productos = productos.filter(Producto.id_producto == int(filtro_id))

    if filtro_nombre:
        productos = productos.filter(Producto.nombre.contains(filtro_nombre))

    if filtro_precio_min and filtro_precio_max:
        if filtro_precio_min == "":
            productos = productos.filter(Producto.precio.between(0, float(filtro_precio_max)))
        else:
            productos = productos.filter(Producto.precio.between(float(filtro_precio_min), float(filtro_precio_max)))


    return render_template('productos.html',
                           lista_productos=productos,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='productos')


@app.route("/filtro-editar-cliente", methods=["POST"])
def filtroEditarCliente():

    filtro_id = request.form['filtro_id']
    filtro_dni = request.form['filtro_dni']
    filtro_nombre = request.form['filtro_nombre']

    cliente = db.session.query(Cliente)

    if filtro_id:
        cliente = cliente.filter(Cliente.id_cliente == int(filtro_id))

    if filtro_dni:
        cliente = cliente.filter(Cliente.dni.contains(filtro_dni))

    if filtro_nombre:
        cliente = cliente.filter(Cliente.nombre.contains(filtro_nombre))

    cliente = cliente.all()
    return render_template('editarcliente.html',
                           lista_cliente=cliente,
                           admin=admin(usuarioactivo().rol),
                           roles=mostrartodo("Rol"),
                           usuario=usuarioactivo().nombre,
                           activo="clientes")

@app.route("/filtro-editar-proveedor", methods=["POST"])
def filtroEditarProveedor():

    filtro_id = request.form['filtro_id']
    filtro_dni = request.form['filtro_dni']
    filtro_nombre = request.form['filtro_nombre']

    proveedor = db.session.query(Proveedor)

    print(filtro_id)
    if filtro_id:
        proveedor = proveedor.filter(Proveedor.id_proveedor == int(filtro_id))

    if filtro_dni:
        proveedor = proveedor.filter(Proveedor.cif.contains(filtro_dni))

    if filtro_nombre:
        proveedor = proveedor.filter(Proveedor.nombre_empresa.contains(filtro_nombre))

    proveedor = proveedor.all()
    return render_template('editarproveedor.html',
                           lista_proveedor=proveedor,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           activo='proveedor')

@app.route("/filtro-asociar", methods=["POST"])
def filtroAsociar():

    filtro_id = request.form['filtro_id']
    filtro_nombre = request.form['filtro_nombre']

    producto = db.session.query(Producto)

    print(filtro_id)
    if filtro_id:
        producto = producto.filter(Producto.id_producto == int(filtro_id))

    if filtro_nombre:
        producto = producto.filter(Producto.nombre.contains(filtro_nombre))

    return render_template('asociarproductoproveedor.html',
                           lista_productos=producto,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           lista_proveedor=mostrartodo("Proveedor"),
                           activo='productos')

@app.route("/filtro-lista-pedidos", methods=["POST"])
def filtroListaPedido():
    filtro_nombre = request.form['filtro_nombre']

    lista_pedidos = db.session.query(Producto, Cliente, VentaCliente). \
        select_from(Producto). \
        join(VentaCliente, Producto.id_producto == VentaCliente.id_producto). \
        join(Cliente, Cliente.id_cliente == VentaCliente.id_cliente). \
        filter(Cliente.id_cliente == usuarioactivo().id_cliente)

    if filtro_nombre:
        lista_pedidos = lista_pedidos.filter(Producto.nombre.contains(filtro_nombre))

    if request.form["dt"]:
        fecha_seleccionada = datetime.strptime(request.form["dt"], '%Y-%m-%d')
        lista_pedidos = lista_pedidos.filter(VentaCliente.fecha_compra >= fecha_seleccionada). \
                                    filter(VentaCliente.fecha_compra < fecha_seleccionada + timedelta(days=1))

    lista_pedidos = lista_pedidos.all()
    form = FechaForm()  # Instanciamos la clase
    return render_template('listapedidocliente.html',
                           lista_pedido_cliente=lista_pedidos,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           form=form,
                           activo='perfil')

@app.route("/filtro-todos-pedidos-clientes", methods=["POST"])
def filtroTodosPedidosClientes():
    filtro_cliente = request.form['filtro_cliente']
    filtro_producto = request.form['filtro_producto']

    lista_pedidos = db.session.query(Producto, Cliente, VentaCliente). \
        select_from(Producto). \
        join(VentaCliente, Producto.id_producto == VentaCliente.id_producto). \
        join(Cliente, Cliente.id_cliente == VentaCliente.id_cliente)

    if filtro_cliente:
        lista_pedidos = lista_pedidos.filter(Cliente.nombre.contains(filtro_cliente))

    if filtro_producto:
        lista_pedidos = lista_pedidos.filter(Producto.nombre.contains(filtro_producto))

    if request.form["dt"]:
        fecha_seleccionada = datetime.strptime(request.form["dt"], '%Y-%m-%d')
        lista_pedidos = lista_pedidos.filter(VentaCliente.fecha_compra >= fecha_seleccionada). \
                                    filter(VentaCliente.fecha_compra < fecha_seleccionada + timedelta(days=1))

    lista_pedidos = lista_pedidos.all()
    form = FechaForm()  # Instanciamos la clase
    return render_template('todospedidosclientes.html',
                           lista_pedido_cliente=lista_pedidos,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           form=form,
                           activo='clientes')

@app.route("/filtro-pedidos-proveedor", methods=["POST"])
def filtroPedidosProveedor():
    filtro_nombre = request.form['filtro_nombre']
    filtro_proveedor = request.form['filtro_proveedor']

    lista_pedidos = db.session.query(Producto, Proveedor, CompraProveedor). \
                    select_from(Producto). \
                    join(CompraProveedor, Producto.id_producto == CompraProveedor.id_producto). \
                    join(Proveedor, Proveedor.id_proveedor == CompraProveedor.id_proveedor)

    if filtro_nombre:
        lista_pedidos = lista_pedidos.filter(Producto.nombre.contains(filtro_nombre))

    if filtro_proveedor:
        lista_pedidos = lista_pedidos.filter(Proveedor.nombre_empresa.contains(filtro_proveedor))

    if request.form["dt"]:
        fecha_seleccionada = datetime.strptime(request.form["dt"], '%Y-%m-%d')
        lista_pedidos = lista_pedidos.filter(CompraProveedor.fecha_compra >= fecha_seleccionada). \
                        filter(CompraProveedor.fecha_compra < fecha_seleccionada + timedelta(days=1))

    lista_pedidos = lista_pedidos.all()
    form = FechaForm()  # Instanciamos la clase
    return render_template('listapedidosproveedor.html',
                           lista_pedido_proveedor=lista_pedidos,
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           form=form,
                           activo='proveedor')

@app.route("/restablecer-password/<id>")
def restablecerContra(id):
    cliente = db.session.query(Cliente).filter(Cliente.id_cliente == id).first()

    #Contraseña por defecto que se pone al restablecerla
    cliente.password = "12345aA"
    msg_correcto = "¡La contraseña de "+cliente.nombre+" se ha restablecido con éxito!"
    db.session.commit()
    db.session.close()

    return render_template("listadoclientes.html",
                           lista_cliente=mostrartodo("Cliente"),
                           admin=admin(usuarioactivo().rol),
                           usuario=usuarioactivo().nombre,
                           msg_correcto=msg_correcto,
                           activo='clientes')

class FechaForm(Form):
    dt = DateField('DatePicker', format='%d-%m-%Y')

#Función que determina si es Administrador o no
def admin(user):
    if user == 1:
        return True
    else:
        return False

#Función que te devuelve el usuario que esta activo con todos sus parametros.
def usuarioactivo():
    usertrue = db.session.query(Cliente).filter(Cliente.dni == session.get('usuario')).first()
    return usertrue

#Función que hace una consulta de toda la tabla dependiento la tabla que le pases
def mostrartodo(tabla):
    lista_tabla=""
    if tabla == "Producto":
        lista_tabla = db.session.query(Producto).all()
    elif tabla == "Proveedor":
        lista_tabla = db.session.query(Proveedor).all()
    elif tabla == "Cliente":
        lista_tabla = db.session.query(Cliente).all()
    elif tabla == "Rol":
        lista_tabla = db.session.query(Rol).all()

    return lista_tabla

if __name__ == "__main__":
    # Reseteamos la base de datos si existe
    # db.Base.metadata.drop_all(bind=db.engine, checkfirst=True)

    # En la siguiente linea estamos indicando a SQLAlchemy que cree, si no existen, las tablas
    # de todos los modelos que encuentre en models.py

    db.Base.metadata.create_all(db.engine)

    app.run(debug=True)
