from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
import db

class Rol(db.Base):

    __tablename__ = "roles" # Minuscula y en singular
    __table_args__ = {'sqlite_autoincrement': True} # Forzamos que en la tabla haya un valor autoincrementable (ID)
    id_rol = Column(Integer, primary_key=True)
    name_rol = Column(String(200), nullable=False) # Esto hace que el campo nombre no pueda estar vacio

    def __init__(self, name_rol):
        self.name_rol = name_rol

    def __str__(self):
        return "Rol {}: {}".format(self.id_rol, self.name_rol)

class Producto(db.Base):

    __tablename__ = "productos" # Minuscula y en singular
    # Info para configurar la table, cosas particulares
    __table_args__ = {'sqlite_autoincrement': True} # Forzamos que en la tabla haya un valor autoincrementable (ID)
    id_producto = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False) # Esto hace que el campo nombre no pueda estar vacio
    stock = Column(Integer)
    precio = Column(Float)
    ean = Column(Integer)
    color = Column(String(20))
    max_stock = Column(Integer)

    def __init__(self, nombre, stock, precio, ean, color, max_stock):
        self.nombre = nombre
        self.stock = stock
        self.precio = precio
        self.ean = ean
        self.color = color
        self.max_stock = max_stock

    def __str__(self):
        return "Producto: {} con ID: {}".format(self.nombre, self.id_producto)


class Cliente(db.Base):

    __tablename__ = "clientes" # Minuscula y en singular
    # Info para configurar la table, cosas particulares
    __table_args__ = {'sqlite_autoincrement': True} # Forzamos que en la tabla haya un valor autoincrementable (ID)
    id_cliente= Column(Integer, primary_key=True)
    dni = Column(String(10))
    nombre = Column(String(200), nullable=False)
    apellidos = Column(String(200))
    direccion = Column(String(200))
    provincia = Column(String(20))
    cp = Column(Integer)
    email = Column(String(200))
    telf = Column(Integer)
    password = Column(String(200))
    rol = Column(Integer, ForeignKey("roles.id_rol"))

    def __init__(self, dni, nombre, apellidos, direccion, provincia, cp, email, telf, password, rol):
        self.dni = dni
        self.nombre = nombre
        self.apellidos = apellidos
        self.direccion = direccion
        self.provincia = provincia
        self.cp = cp
        self.email = email
        self.telf = telf
        self.password = password
        self.rol = rol

    def __str__(self):
        return "Cliente: {} con ID: {}".format(self.nombre, self.id_cliente)

class VentaCliente(db.Base):
    __tablename__ = "ventaclientes"  # Minuscula y en singular
    # Info para configurar la table, cosas particulares
    __table_args__ = {'sqlite_autoincrement': True}  # Forzamos que en la tabla haya un valor autoincrementable (ID)
    id_ventacliente = Column(Integer, primary_key=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"))
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"))
    cantidad = Column(Integer)
    precio = Column(Float)
    fecha_compra = Column(String(10))
    iva = Column(Float)
    total = Column(Float)

    def __init__(self, id_producto, id_cliente, cantidad, precio, fecha_compra, iva, total):
        self.id_producto = id_producto
        self.id_cliente = id_cliente
        self.cantidad = cantidad
        self.precio = precio
        self.fecha_compra = fecha_compra
        self.iva = iva
        self.total = total

    def __str__(self):
        return "Tabla Asocida de ventas"

class Proveedor(db.Base):
    __tablename__ = "proveedores"  # Minuscula y en singular
    # Info para configurar la table, cosas particulares
    __table_args__ = {'sqlite_autoincrement': True}  # Forzamos que en la tabla haya un valor autoincrementable (ID)
    id_proveedor = Column(Integer, primary_key=True)
    cif = Column(String(10), nullable=False)
    nombre_empresa = Column(String(200), nullable=False)
    telf = Column(Integer)
    direccion = Column(String(200))
    provincia = Column(String(20))
    cp = Column(Integer)
    email = Column(String(200))
    iva = Column(Integer)
    descuento = Column(Float)

    def __init__(self, cif, nombre_empresa, telf, direccion, provincia, cp, email, iva, descuento):
        self.cif = cif
        self.nombre_empresa = nombre_empresa
        self.telf = telf
        self.direccion = direccion
        self.provincia = provincia
        self.cp = cp
        self.email = email
        self.iva = iva
        self.descuento = descuento

    def __str__(self):
        return "Proveedor: {} con ID: {}".format(self.nombre_empresa, self.id_proveedor)

class CompraProveedor(db.Base):
    __tablename__ = "compraproveedores"  # Minuscula y en singular
    # Info para configurar la table, cosas particulares
    __table_args__ = {
        'sqlite_autoincrement': True}  # Forzamos que en la tabla haya un valor autoincrementable (ID)
    id_compraproveedor = Column(Integer, primary_key=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"))
    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"))
    cantidad = Column(Integer)
    precio = Column(Float)
    descuento = Column(Float)
    iva = Column(Integer)
    total = Column(Float)
    fecha_compra = Column(String(10))


    def __init__(self, id_producto, id_proveedor, cantidad, precio, descuento, iva, total, fecha_compra):
        self.id_producto = id_producto
        self.id_proveedor = id_proveedor
        self.cantidad =cantidad
        self.precio = precio
        self.descuento = descuento
        self.iva = iva
        self.total = total
        self.fecha_compra = fecha_compra

    def __str__(self):
        return "Tabla Asocida de ventas"

class ProductoProveedor(db.Base):
    __tablename__ = "productoproveedor"  # Minuscula y en singular
    # Info para configurar la table, cosas particulares
    __table_args__ = {
        'sqlite_autoincrement': True}  # Forzamos que en la tabla haya un valor autoincrementable (ID)
    id_pp = Column(Integer, primary_key=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"))
    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"))
    precio = Column(Float)

    def __init__(self, id_producto, id_proveedor, precio):
        self.id_producto = id_producto
        self.id_proveedor = id_proveedor
        self.precio = precio

    def __str__(self):
        return "Tabla que asocia a un prodcuto con un proveedor"