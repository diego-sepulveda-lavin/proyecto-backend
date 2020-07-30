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
        usuarios = self.usuarios
        usuarios = list(map(lambda usuario: usuario.serialize(), usuarios))
        return {
            "id" : self.id,
            "nombre" : self.nombre,
            "rut" : self.rut,
            "razon_social" : self.razon_social,
            "rubro" : self.rubro,
            "usuarios": usuarios
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
    def update(self):
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100), nullable = False)
    apellido = db.Column(db.String(100), nullable = False)
    codigo = db.Column(db.String(1000), unique = True)
    rut = db.Column(db.String(13), nullable = False, unique = True)
    rol = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False,  unique = True)
    password = db.Column(db.String(100), nullable = False)
    status = db.Column(db.Boolean, default = True, nullable = False)
    fecha_registro = db.Column(db.DateTime, nullable = False, default = datetime.now) #hora local
    foto = db.Column(db.String(100), default='without-photo.png')
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable = False)
    entradas = db.relationship('Entrada_Inventario', backref = 'usuario', lazy = True)
    salidas = db.relationship('Salida_Inventario', backref = 'usuario', lazy = True)
    cuadratura_usuario = db.relationship('Cuadratura_Caja', foreign_keys="[Cuadratura_Caja.usuario_id]", backref = 'usuario', lazy = True)
    cuadratura_admin = db.relationship('Cuadratura_Caja', foreign_keys="[Cuadratura_Caja.admin_id]", backref = 'admin', lazy = True)

    def serialize(self):
        return {
            "id" : self.id,
            "nombre" : self.nombre,
            "apellido" : self.apellido,
            "codigo" : self.codigo,
            "rut" : self.rut,
            "rol" : self.rol,
            "email" : self.email,
            #NO DEVOLVER PASSWORD AL FRONT END "password" : self.password,
            "status" : self.status,
            "fecha_registro" : self.fecha_registro.strftime("%Y-%m-%d"),
            "foto": self.foto,
            "empresa_id" : self.empresa_id,
            
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
    def update(self):
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def generaCodigo(self):
        return f"usr{self.id}"
        

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
    #facturaC = db.relationship("Factura_Compra", backref= "entradas", lazy = True)


    def serialize(self):
        return{
            "id" : self.id,
            "cantidad" : self.cantidad,
            "precio_costo_unitario" : self.precio_costo_unitario,
            "costo_total" : self.costo_total,
            "fecha_registro" : self.fecha_registro,
            "usuario_id" : self.usuario_id,
            "factura_compra_id" : self.factura_compra_id,
            "producto_id" : self.producto_id,
            "producto" : self.producto.serialize()
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
    def update(self):
        db.session.commit()
    def delete(self):
        pass
    def genera_costo_total(self):
        return self.cantidad*self.precio_costo_unitario

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


    def serialize(self):
        return {
            "id" : self.id,
            "cantidad" : self.cantidad,
            "precio_costo_unitario" : self.precio_costo_unitario,
            "costo_total" : self.costo_total,
            "fecha_registro" : self.fecha_registro,
            "usuario_id" : self.usuario_id,
            "producto_id" : self.producto_id,
            "documento_venta_id" : self.documento_venta_id
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
    def update(self):
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def genera_costo_total(self):
        return self.cantidad*self.precio_costo_unitario

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
    proveedor_id = db.Column(db.Integer, nullable = False)
    entradas_I = db.relationship("Entrada_Inventario", backref = "factura" , lazy = True)

    def serialize(self):
        return {
            "id" : self.id,
            "folio" : self.folio,
            "fecha_emision" : self.fecha_emision,
            "fecha_recepcion" : self.fecha_recepcion,
            "monto_neto" : self.monto_neto,
            "monto_iva" : self.monto_iva,
            "monto_otros_impuestos" : self.monto_otros_impuestos,
            "monto_total" : self.monto_total,
            "proveedor_id" : self.proveedor_id,
            "entradas_inventario": list(map(lambda entrada_I : entrada_I.serialize(), self.entradas_I))
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
    def update(self):
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()

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
    entradaI = db.relationship("Entrada_Inventario", foreign_keys="[Entrada_Inventario.producto_id]", backref = "producto", lazy = True, uselist= False)
    salidaI = db.relationship("Salida_Inventario", foreign_keys="[Salida_Inventario.producto_id]", backref = "producto", lazy = True, uselist = False)
    
    def serialize(self):
        return {
            "id" : self.id,
            "sku" : self.sku,
            "descripcion" : self.descripcion,
            "codigo_barra" : self.codigo_barra,
            "unidad_entrega" : self.unidad_entrega,
            "categoria_id" : self.categoria_id,
            "precio_venta_unitario" : self.precio_venta_unitario,
            "margen_contribucion" : self.margen_contribucion,
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
    def update(self):
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Documento_Venta(db.Model):
    __tablename__ = "documentos_ventas"
    id = db.Column(db.Integer, primary_key = True)
    tipo_documento = db.Column(db.String(100), nullable = False)
    numero_documento = db.Column(db.Integer, nullable = False)
    fecha_emision = db.Column(db.DateTime, nullable = False, default = datetime.now)
    monto_neto = db.Column(db.Float, nullable = False)
    monto_iva = db.Column(db.Float, nullable = False)
    monto_otros_impuestos = db.Column(db.Float, nullable = True)
    monto_total = db.Column(db.Float, nullable = False)
    forma_pago = db.Column(db.String(100), nullable = False)
    salidas_I = db.relationship("Salida_Inventario", backref = "documento_venta", lazy = True)

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
            "forma_pago":self.forma_pago,
            "salidas_inventario": list(map(lambda salida_I : salida_I.serialize(), self.salidas_I))
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
    def update(self):
        pass
    def delete(self):
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
    #facturaC = db.relationship("Factura_Compra", foreign_keys="[Factura_Compra.proveedor_id]", backref = "proveedor", lazy = True, uselist = False)

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
        db.session.add(self)
        db.session.commit()
    def update(self):
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Categoria(db.Model):
    __tablename__ = "categorias"
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100), nullable = False, unique = True)
    productos = db.relationship("Producto", backref = "categoria", lazy = True)

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre
            
        }
    def save(self):
        db.session.add(self)
        db.session.commit()
    def update(self):
        db.session.commit()
    def delete(self):
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

    def serialize(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "admin_id": self.admin_id,
            "fecha_apertura": self.fecha_apertura,
            "fecha_cierre": self.fecha_cierre,
            "monto_apertura": self.monto_apertura,
            "monto_transferencia": self.monto_transferencia,
            "monto_efectivo": self.monto_efectivo,
            "monto_tarjeta": self.monto_tarjeta,
            "monto_cierre": self.monto_cierre,
            "diferencia_en_caja": self.diferencia_en_caja
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    def update(self):
        pass
    def delete(self):
        pass

