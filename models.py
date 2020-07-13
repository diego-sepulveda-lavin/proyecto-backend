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

    def serialize(self):
        return {
            "id" : self.id,
            "nombre" : self.nombre,
            "rut" : self.rut,
            "razon_social" : self.razon_social,
            "rubro" : self.rubro
        }

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

class Categoria(db.Model):
    __tablename__ = "categorias"
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100), nullable = False, unique = True)

class Cuadratura_Caja(db.Model):
    __tablename__ = "cuadraturas_cajas"
    id = db.Column(db.Integer, primary_key = True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable = False)
    administrador = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable = False)
    fecha_apertura = db.Column(db.DateTime, nullable = False, default = datetime.now) #hora local
    fecha_cierre = db.Column(db.DateTime, nullable = False, default = datetime.now) #hora local
    monto_apertura = db.Column(db.Float, nullable = False)
    monto_transferencia = db.Column(db.Float, nullable = False)
    monto_efectivo = db.Column(db.Float, nullable = False)
    monto_tarjeta = db.Column(db.Float, nullable = False)
    monto_cierre = db.Column(db.Float, nullable = False)
    diferencia_en_caja = db.Column(db.Float, nullable = False)