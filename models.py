from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class Empresa(db.Model):
    __tablename__ = "empresas"
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100), nullable = False)
    rut = db.Column(db.String(13), nullable = False, unique = True)
    razon_social = db.Column(db.String(100), nullable = False, unique = True)
    rubro = db.Column(db.String(100), nullable = False)
    usuarios = db.relationship('Usuario', backref = 'empresa',lazy = True)

    def serialize(self):
        return {
            "id" : self.id,
            "nombre" : self.nombre,
            "rut" : self.rut,
            "razon_social" : self.razon_social,
            "rubro" : self.rubro
        }

    def save(self):
        pass
    def update(self):
        pass
    def add(self):
        pass

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100), nullable = False)
    apellido = db.Column(db.String(100), nullable = False)
    codigo = db.Column(db.Integer, nullable = False, unique = True)
    rut = db.Column(db.String(13), nullable = False, unique = True)
    rol = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False,  unique = True)
    password = db.Column(db.String(100), nullable = False)
    status = db.Column(db.Boolean, default = True, nullable = False)
    fecha_registro = db.Column(db.DateTime, nullable = False, default = datetime.now) #hora local
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable = False)
    entradas = db.relationship('Entrada_Inventario', backref = 'usuario', lazy = True)
    salidas = db.relationship('Salida_Inventario', backref = 'usuario', lazy = True)
    cuadres_usuario = db.relationship('Cuadratura_Caja', backref = 'usuario', lazy = True)
    cuadres_admin = db.relationship('Cuadratura_Caja', backref = 'admin', lazy = True)

    def save(self):
        pass
    def update(self):
        pass
    def add(self):
        pass

class Entrada_Inventario(db.Model):
    __tablename__ = "entradas_inventario"
    id = db.Column(db.Integer, primary_key = True)
    cantidad = db.Column(db.Float, nullable = False)
    precio_costo_unitario = db.Column(db.Float, nullable = False)
    costo_total = db.Column(db.Float, nullable = False)
    fecha_registro = db.Column(db.DateTime, nullable = False, default = datetime.now) #hora local
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable = False)
    factura_compra_id = db.Column(db.Integer, db.ForeignKey("facturas_compras.id"), nullable = False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable = False)
    facturaC = db.relationship("Factura_Compra", backref= "entradas", lazy = True)
    producto = db.relationship("Producto", backref = "entradas", lazy = True)

    def save(self):
        pass
    def update(self):
        pass
    def add(self):
        pass

class Salida_Inventario(db.Model):
    __tablename__ = "salidas_inventario"
    id = db.Column(db.Integer, primary_key = True)
    cantidad = db.Column(db.Float, nullable = False)
    precio_costo_unitario = db.Column(db.Float, nullable = False)
    costo_total = db.Column(db.Float, nullable = False)
    fecha_registro = db.Column(db.DateTime, nullable = False, default = datetime.now) #hora local
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable = False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable = False)
    documento_venta_id = db.Column(db.Integer, db.ForeignKey("documentos_ventas.id"), nullable = False)
    documentoV = db.relationship("Documento_Venta", backref = "salidas", lazy = True)
    producto = db.relationship("Producto", backref = "salidas", lazy = True)

    def save(self):
        pass
    def update(self):
        pass
    def add(self):
        pass

class Factura_Compra(db.Model):
    __tablename__ = "facturas_compras"
    id = db.Column(db.Integer, primary_key = True)
    folio = db.Column(db.Integer, nullable = False)
    fecha_emision = db.Column(db.DateTime, nullable = False)
    fecha_recepcion = db.Column(db.DateTime, nullable = False)
    monto_neto = db.Column(db.Float, nullable = False)
    monto_iva = db.Column(db.Float, nullable = False)
    monto_otros_impuestos = db.Column(db.Float, nullable = False)
    monto_total = db.Column(db.Float, nullable = False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable = False)
    entradaI = db.relationship("Entrada_Inventario", backref = "factura" , lazy = True, uselist= False)
    proveedor = db.relationship("Proveedor", backref = "facturas", lazy = True)

    def save(self):
        pass
    def update(self):
        pass
    def add(self):
        pass

class Producto(db.Model):
    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key = True)
    sku = db.Column(db.String(100), nullable = False, unique = True)
    descripcion = db.Column(db.String(100), nullable = False)
    codigo_barra = db.Column(db.String(100), nullable = False, unique = True)
    unidad_entrega = db.Column(db.String(100), nullable = False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable = False)
    precio_venta_unitario = db.Column(db.Float, nullable = True)
    margen_contribucion = db.Column(db.Float, nullable = True)
    entradaI = db.relationship("Entrada_Inventario", backref = "producto", lazy = True, uselist= False)
    salidaI = db.relationship("Salida_Inventario", backref = "producto", lazy = True, uselist = False)
    categoria = db.relationship("Categoria", backref = "producto", lazy = True)
    
    def save(self):
        pass
    def update(self):
        pass
    def add(self):
        pass

class Documento_Venta(db.Model):
    __tablename__ = "documentos_ventas"
    id = db.Column(db.Integer, primary_key = True)
    tipo_documento = db.Column(db.String(100), nullable = False)
    numero_documento = db.Column(db.Integer, nullable = False)
    fecha_emision = db.Column(db.DateTime, nullable = False)
    monto_neto = db.Column(db.Float, nullable = False)
    monto_iva = db.Column(db.Float, nullable = False)
    monto_otros_impuestos = db.Column(db.Float, nullable = False)
    monto_total = db.Column(db.Float, nullable = False)
    forma_pago = db.Column(db.String(100), nullable = False)
    salidaI = db.relationship("Salida_Inventario", backref = "documentoV", lazy = True, uselist = False)

    def serialize(self):
        return {
            "id" : self.id,
            "tipo_documento":self.tipo_documento,
            "numero_documento":self.numero_documento,
            "fecha_emision":self.fecha_emision,
            "monto_neto":self.monto_neto,
            "monto_iva":self.monto_iva,
            "monto_otros_impuestos":self.monto_otros_impuestos,
            "monto_total":self.monto_total,
            "forma_pago":self.forma_pago
        }

    def save(self):
        pass
    def update(self):
        pass
    def add(self):
        pass

class Proveedor(db.Model):
    __tablename__ = "proveedores"
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100), nullable = False)
    rut = db.Column(db.String(13), nullable = False, unique = True)
    razon_social = db.Column(db.String(100), nullable = False, unique = True)
    rubro = db.Column(db.String(100), nullable = False)
    direccion = db.Column(db.String(100), nullable = False)
    cuenta_corriente = db.Column(db.String(100), nullable = True)
    banco = db.Column(db.String(100), nullable = True)
    facturaC = db.relationship("Factura_Compra", backref = "proveedor", lazy = True, uselist = False)

    def serialize(self):
        return {
            "id" : self.id,
            "nombre" : self.nombre,
            "rut" : self.rut,
            "razon_social" : self.razon_social,
            "rubro" : self.rubro,
            "direccion": self.direccion,
            "cuenta_corriente": self.cuenta_corriente,
            "banco" : self.banco
        }
        
    def save(self):
        pass
    def update(self):
        pass
    def add(self):
        pass

class Categoria(db.Model):
    __tablename__ = "categorias"
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100), nullable = False, unique = True)
    productos = db.relationship("Producto", backref = "categoria", lazy = True)

    def save(self):
        pass
    def update(self):
        pass
    def add(self):
        pass

class Cuadratura_Caja(db.Model):
    __tablename__ = "cuadraturas_cajas"
    id = db.Column(db.Integer, primary_key = True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable = False)
    admin_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable = False)
    fecha_apertura = db.Column(db.DateTime, nullable = False, default = datetime.now) #hora local
    fecha_cierre = db.Column(db.DateTime, nullable = False, default = datetime.now) #hora local
    monto_apertura = db.Column(db.Float, nullable = False)
    monto_transferencia = db.Column(db.Float, nullable = False)
    monto_efectivo = db.Column(db.Float, nullable = False)
    monto_tarjeta = db.Column(db.Float, nullable = False)
    monto_cierre = db.Column(db.Float, nullable = False)
    diferencia_en_caja = db.Column(db.Float, nullable = False)
    
    def save(self):
        pass
    def update(self):
        pass
    def add(self):
        pass

