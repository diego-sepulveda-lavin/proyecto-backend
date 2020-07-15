from datetime import datetime
from flask import Flask, request, jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from models import db, Empresa, Usuario, Producto, Categoria, Proveedor, Factura_Compra, Entrada_Inventario, Salida_Inventario, Documento_Venta
from config import Development

ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg'}


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.from_object(Development)
db.init_app(app)
Migrate(app, db)
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Using the expired_token_loader decorator, we will now call
# this function whenever an expired but otherwise valid access
# token attempts to access an endpoint
@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'msg': 'The {} token has expired. Please Login Again'.format(token_type)
    }), 401

@app.route('/')
def home():
    return 'Hola mundo'


@app.route("/api/login/", methods = ["POST"])
def login():
    rut = request.json.get("rut", None)
    password = request.json.get("password", None)

    if not rut:
        return jsonify({"msg": "Rut no puede estar vacío"}),400
    if not password:
        return jsonify({"msg": "Password no puede estar vacío"}),400

    userR = Usuario.query.filter_by(rut = rut).first()
    if not userR:
        return jsonify({"msg":"Rut o contraseña inválido."}),401
    if not bcrypt.check_password_hash(userR.password, password):
        return jsonify({"msg":"Rut o contraseña inválido."}), 401

    expires = datetime.timedelta(hour=24)
    access_token = create_access_token(identity=userR.rut, expires_delta=expires)

    data = {
        "access_token": access_token,
        "user": userR.serialize()
    }

    return jsonify(data), 200


@app.route('/api/empresas', methods = ['GET', "POST"])
@app.route('/api/empresas/<int:id>', methods = ['GET', "PUT","DELETE"])
#@jwt_required
def empresas(id=None):
    ### Ver Empresas ###
    if request.method == 'GET':
        if not id:
            empresas = Empresa.query.all()
            empresas = list(map(lambda empresa: empresa.serialize(),empresas))
            return jsonify(empresas),200

    ### Ver Empresa por ID ###
        empresa = Empresa.query.get(id)
        if empresa:
            return jsonify(empresa.serialize()),200
        return jsonify({"msg": "Empresa no se encuentra en el sistema"}),400

    ### Eliminar Empresa por ID ###
    if request.method == "DELETE":
        if id:
            empresa= Empresa.query.get(id)
            if empresa:
                empresa.delete()
                return jsonify({"msg": f"Empresa <{empresa.nombre}> eliminada exitosamente!"}),200
            else:
                return jsonify({"msg": "Empresa no se encuentra en el sistema"}),400

    ### Ingresar Empresa ###
    if request.method == "POST":
        nombre = request.json.get("nombre", None)
        rut = request.json.get("rut", None)
        razon_social = request.json.get("razon_social", None)
        rubro = request.json.get("rubro", None)

        if not nombre:
            return jsonify({"msg": "Nombre de empresa no puede estar vacío"}),400
        if not rut:
            return jsonify({"msg": "Rut de empresa no puede estar vacío"}),400
        if not razon_social:
            return jsonify({"msg": "Razon Social de empresa no puede estar vacío"}),400
        if not rubro:
            return jsonify({"msg": "Rubro de empresa no puede estar vacío"}),400
        
        validaRutExistente = Empresa.query.filter_by(rut = rut).first()
        if validaRutExistente:
            return jsonify({"msg": "Rut de empresa ya se encuentra registrado"}),401

        validaRazonSocialExistente = Empresa.query.filter_by(razon_social = razon_social).first()
        if validaRazonSocialExistente:
            return jsonify({"msg": "Razon social de empresa ya se encuentra registrado"}),401

        empresa = Empresa()
        empresa.nombre = nombre
        empresa.rut = rut
        empresa.razon_social = razon_social
        empresa.rubro = rubro
        empresa.save()

        return jsonify(empresa.serialize()),200
    ### Actualizar Empresa by ID ###
    if request.method == "PUT":
        if id:
            empresaActualizar = Empresa.query.get(id)
            if not empresaActualizar:
                return jsonify({"msg": "Empresa no se encuentra en el sistema"}),401

            nombre = request.json.get("nombre", None)
            rut = request.json.get("rut", None)
            razon_social = request.json.get("razon_social", None)
            rubro = request.json.get("rubro", None)

            rutOcupado = Empresa.query.filter_by(rut = rut).first()
            if rutOcupado and rut is not None:
                return jsonify({"msg": "Rut ya se encuentra registrado."}),401
            razonSocialOcupado = Empresa.query.filter_by(razon_social = razon_social).first()
            if razonSocialOcupado and razon_social is not None:
                return jsonify({"msg" : "Razon social ya se encuentra registrada."}),401

            if nombre is not None:
                if not nombre:
                    return jsonify({"msg": "Nombre no puede ir vacío"}),401
                empresaActualizar.nombre = nombre
            
            if rut is not None:
                if not rut:
                    return jsonify({"msg": "Rut no puede ir vacío"}),401
                empresaActualizar.rut = rut
            
            if razon_social is not None:
                if not razon_social:
                    return jsonify({"msg": "Razon social no puede ir vacío"}),401
                empresaActualizar.razon_social = razon_social
            
            if rubro is not None:
                if not rubro:
                    return jsonify({"msg": "Rubro no puede ir vacío"}),401
                empresaActualizar.rubro = rubro


            empresaActualizar.update()
            data = {
                "msg": "Empresa Modificada",
                "empresa": empresaActualizar.serialize()
            }
            return jsonify(data),200

@app.route("/api/usuarios", methods = ["GET","POST"])
@app.route("/api/usuarios/<int:id>", methods = ["GET","DELETE", "PUT"])
def usuarios(id = None):
    ### Ver Usuarios ###
    if request.method == "GET":
        if id is None:
            usuarios = Usuario.query.all()
            if not usuarios:
                return jsonify({"msg": "No hay usuarios"})
            usuarios = list(map(lambda usuario: usuario.serialize(), usuarios))
            return jsonify(usuarios),200

    ### Ver Usuario by ID ###
        else:
            usuario = Usuario.query.get(id)
            if not usuario:
                return jsonify({"msg": "No se encuentra usuario."}),401
            return jsonify(usuario.serialize()),200

    ### Eliminar Usuario ###
    if request.method == "DELETE":
        if id:
            usuario = Usuario.query.get(id)
            if usuario:
                usuario.delete()
                return jsonify({"msg": f"Usuario <{usuario.nombre}> eliminado exitosamente."}),200
            else:
                return jsonify({"msg": "Usuario no se encuentra registrado."}),401

    ### Insertar Usuario ###
    if request.method == "POST":
        data = request.get_json()
        if not data["nombre"]:
            return jsonify({"msg":"Nombre no puede estar vacío"}),401
        if not data["apellido"]:
            return jsonify({"msg":"Apellido no puede estar vacío"}),401
        if not data["rut"]:
            return jsonify({"msg":"Rut no puede estar vacío"}),401
        if not data["rol"]:
            return jsonify({"msg":"Rol no puede estar vacío"}),401
        if not data["email"]:
            return jsonify({"msg":"Email no puede estar vacío"}),401
        if not data["password"]:
            return jsonify({"msg":"Password no puede estar vacío"}),401
        if not data["empresa_id"]:
            return jsonify({"msg":"Empresa_id no puede estar vacío"}),401
        
        rut_ocupado = Usuario.query.filter_by(rut = data["rut"]).first()
        if rut_ocupado:
            return jsonify({"msg": "Rut ya se encuentra registrado."}),401
        email_ocupado= Usuario.query.filter_by(email = data["email"]).first()
        if email_ocupado:
            return jsonify({"msg": "Email ya se encuentra registrado."}),401
        
        usuario = Usuario()
        usuario.nombre = data["nombre"]
        usuario.apellido = data["apellido"]
        usuario.rut = data["rut"]
        usuario.rol = data["rol"]
        usuario.email = data["email"]
        usuario.password = bcrypt.generate_password_hash(data["password"])
        usuario.empresa_id = data["empresa_id"] 
        usuario.save()
        usuario.codigo = usuario.generaCodigo()
        usuario.update()

        return jsonify(usuario.serialize()),200
    
    ### Actualizar Usuario ###
    if request.method == "PUT":
        if id:
            usuario_actualizar = Usuario.query.get(id)
            if not usuario_actualizar:
                return jsonify({"msg": "Usuario no se encuentra registrado"}),401
            
            nombre = request.json.get("nombre", None)
            apellido = request.json.get("apellido", None)
            rut = request.json.get("rut", None)
            rol = request.json.get("rol", None)
            email = request.json.get("email", None)
            password = request.json.get("password", None)
            status = request.json.get("status", None)
        

            rut_ocupado = Usuario.query.filter_by(rut = rut)
            if rut_ocupado and rut is not None:
                return jsonify({"msg": "Rut ya se encuentra registrado."}),401
            email_ocupado = Usuario.query.filter_by(email = email)
            if email_ocupado and email is not None:
                return jsonify({"msg": "Correo ya se encuentra registrado."}),401

            if nombre is not None:
                if not nombre:
                    return jsonify({"msg": "Nombre no puede ir vacío."}),401
                usuario_actualizar.nombre = nombre

            if apellido is not None:
                if not apellido:
                    return jsonify({"msg": "Apellido no puede ir vacío."}),401
                usuario_actualizar.apellido = apellido 
                
            if rut is not None:
                if not rut:
                    return jsonify({"msg": "Rut no puede ir vacío."}),401
                usuario_actualizar.rut = rut

            if rol is not None:
                if not rol:
                    return jsonify({"msg": "Rol no puede ir vacío."}),401
                usuario_actualizar.rol = rol

            if email is not None:
                if not email:
                    return jsonify({"msg": "Email no puede ir vacío"}),401
                usuario_actualizar.email = email

            if password is not None:
                if not password:
                    return jsonify({"msg": "Password no puede ir vacío."}),401
                usuario_actualizar.password = password
            if status is not None:
                if status != False and status != True:
                    return jsonify("Status debe ser true o false"),401
                usuario_actualizar.status = status
            
            usuario_actualizar.update()
            data = {
                "msg": "Usuario Modificado",
                "usuario": usuario_actualizar.serialize()
            }
            return jsonify(data),200
 
@app.route("/api/entrada-inventario", methods =["GET", "POST"])
@app.route("/api/entrada-inventario/<int:id>", methods=["GET", "PUT"])
def entrada_inventario(id = None):
    ### VER TODAS LAS ENTRADAS DE INVENTARIO ###
    if request.method =="GET":        
        if id is None:
            entradas = Entrada_Inventario.query.all()
            if entradas:
                entradas = list(map(lambda entrada: entrada.serialize(),entradas))
                return jsonify(entradas),200
            else:
                return jsonify({"msg": "No hay entradas disponibles."}),401

    ### VER UNA ENTRADA DE INVENTARIO POR ID ###
        entrada = Entrada_Inventario.query.get(id)
        if entrada:
            return jsonify(entrada.serialize()),200
        else:
            return jsonify({"msg": "No existe registro asociado."}),401
    
    ### INSERTAR UNA ENTRADA DE INVENTARIO POR ID ###
    if request.method == "POST":
        data = request.get_json()

        if data["cantidad"] <= 0:
            return jsonify({"msg": "Cantidad debe ser mayor a 0"}),401
        if data["precio_costo_unitario"] <= 0:
            return jsonify({"msg": "Precio costo debe ser mayor a 0"}),401

        entradaI = Entrada_Inventario()
        entradaI.cantidad = data["cantidad"]
        entradaI.precio_costo_unitario = data["precio_costo_unitario"]
        entradaI.costo_total = entradaI.genera_costo_total()
        entradaI.usuario_id = 1 #Cambiar
        entradaI.producto_id = 1 #cambiar
        entradaI.factura_compra_id = 1 #Cambiar
        entradaI.save()
        return jsonify({"msg": "Entrada guardada exitosamente."}),200

    ### ACTUALIZAR UNA ENTRADA DE INVENTARIO POR ID ###
    if request.method == "PUT":
        entrada_actualizar = Entrada_Inventario.query.get(id)
        if not entrada_actualizar:
            return jsonify({"msg": "No existe registro."})
        
        cantidad = request.json.get("cantidad", None)
        precio_costo_unitario = request.json.get("precio_costo_unitario", None)

        if cantidad is not None:
            if cantidad < 0:
                return jsonify({"msg": "Cantidad no puede ser menor a 0"}),401
            entrada_actualizar.cantidad = cantidad
        if precio_costo_unitario is not None:
            if precio_costo_unitario <= 0:
                return jsonify({"msg": "Precio costo unitario no puede ser menor a 0"}),401
            entrada_actualizar.precio_costo_unitario = precio_costo_unitario
            
        entrada_actualizar.costo_total = entrada_actualizar.genera_costo_total() 
        entrada_actualizar.update() 
        return jsonify({"msg": "Producto modificado."}),200      

            

       
@app.route('/api/categoria', methods=['GET'])
@app.route('/api/categoria/<int:id>', methods=["GET", "POST", "PUT", "DELETE"])
def categorias(id = None):
    if request.method == 'GET':
        if not id:
            categorias = Categoria.query.all()
            if categorias:
                categorias = list(map(lambda categoria: categoria.serialize(), categorias))
                return jsonify (categorias),200
            return jsonify({"msg": "Categoria no existente"}),400
        categoria = Categoria.query.get(id)
        if categoria:
            return (categoria.serialize()),200
        return jsonify({"msg": "categoria no encontrada"}),400 
    
    if request.method == 'POST':
        nombre = request.json.get("nombre", None)
        if not nombre:
            return jsonify({"msg": "por favor ingresar nombre de categoria valido"})
        name_overlapped = Categoria.query.filter_by(nombre = nombre).first()
        if name_overlapped:
            return jsonify({"msg": "Categoria ya existe"})

    if request.method == 'DELETE':
        if id:
            categoria= Categoria.query.get(id)
            if Categoria:
                categoria.delete()
                return jsonify({"msg": f"Categoria {empresa.nombre} eliminada"}),200
            else:
                return jsonify({"msg": "categoria no encontrada"}),400 
            categoria = Categoria()
            categoria.nombre = nombre
            categoria.save()
    
    if request.method == 'PUT':
        if id:
            nombre = request.json.get("nombre", None)
            
            if not nombre:
                return jsonify({"msg": "Nombre de empresa no puede estar vacío"}),400
                        
            categoria_update = Empresa.query.get(id)
            if not categoria_update:
                return jsonify({"msg": "Empresa no se encuentra en el sistema"}),401

           
            categoria_update.nombre = nombre
                    
            categoria_update.update()
            data = {"msg": "Empresa Modificada", "user": categoria_update.serialize()}
            return jsonify(data),200



@app.route("/api/proveedores", methods = ['GET', 'POST'])
@app.route("/api/proveedores/<int:id>", methods = ['GET', 'PUT', 'DELETE'])
def proveedores(id = None):
    
    if request.method == 'GET':
        # DEVUELVE LISTADO CON TODOS LOS PROVEEDORES
        if not id:
            proveedores = Proveedor.query.all()
            proveedores = list(map(lambda proveedor: proveedor.serialize(), proveedores))
            return jsonify(proveedores), 200

        # DEVUELVE DETALLE DE PROVEEDOR POR ID
        if id:
            proveedor = Proveedor.query.get(id)
            if proveedor:
                return jsonify(proveedor.serialize()), 200
            else:
                return jsonify({"msg": "Empresa no se encuentra en el sistema"}), 400

    # PERMITE CREAR NUEVO PROVEEDOR
    if request.method == 'POST':
        nombre = request.json.get("nombre", None)
        rut = request.json.get("rut", None)
        razon_social = request.json.get("razon_social", None)
        rubro = request.json.get("rubro", None)
        direccion = request.json.get("direccion", None)
        cuenta_corriente = request.json.get("cuenta_corriente", None)
        banco = request.json.get("banco", None)

        if not nombre:
            return jsonify({"msg": "Nombre no puede estar vacío"}), 400
        if not rut:
            return jsonify({"msg": "Rut no puede estar vacío"}), 400
        if not razon_social:
            return jsonify({"msg": "Razon Social no puede estar vacío"}), 400
        if not rubro:
            return jsonify({"msg": "Rubro no puede estar vacío"}), 400
        if not direccion:
            return jsonify({"msg": "Dirección no puede estar vacío"}), 400
        
        check_rut = Proveedor.query.filter_by(rut = rut).first()
        if check_rut:
            return jsonify({"msg": "Rut de empresa ya se encuentra registrado"}), 400
        check_razon_social = Proveedor.query.filter_by(razon_social = razon_social).first()
        if check_razon_social:
            return jsonify({"msg":"Razon social de empresa ya se encuentra registrado"}), 400

        proveedor = Proveedor()
        proveedor.nombre = nombre
        proveedor.rut = rut
        proveedor.razon_social = razon_social
        proveedor.rubro = rubro
        proveedor.direccion = direccion
        proveedor.cuenta_corriente = cuenta_corriente
        proveedor.banco = banco

        proveedor.save()    
        return jsonify(proveedor.serialize()), 200
    
    # PERMITE MODIFICAR PROVEEDOR
    if request.method == 'PUT':
        proveedor = Proveedor.query.get(id)
        if not proveedor:
            return jsonify({"msg": "Empresa no se encuentra en el sistema"}), 400
        
        
        nombre = request.json.get("nombre", None)
        rut = request.json.get("rut", None)
        razon_social = request.json.get("razon_social", None)
        rubro = request.json.get("rubro", None)
        direccion = request.json.get("direccion", None)
        cuenta_corriente = request.json.get("cuenta_corriente", None)
        banco = request.json.get("banco", None)
        
        check_rut = Proveedor.query.filter_by(rut = rut).first()
        if check_rut and rut is not None:
            return jsonify({"msg": "Rut de empresa ya se encuentra registrado"}), 400

        check_razon_social = Proveedor.query.filter_by(razon_social = razon_social).first()
        if check_razon_social and razon_social is not None:
            return jsonify({"msg":"Razon social de empresa ya se encuentra registrado"}), 400

        if nombre is not None:
            if not nombre:
                return jsonify({"msg": "Nombre no puede estar vacío"}), 400
            proveedor.nombre = nombre

        if rut is not None:
            if not rut:
                return jsonify({"msg": "Rut no puede estar vacío"}), 400
            proveedor.rut = rut

        if razon_social is not None:
            if not razon_social:
                return jsonify({"msg": "Razon Social no puede estar vacío"}), 400
            proveedor.razon_social = razon_social
        
        if rubro is not None:
            if not rubro:
                return jsonify({"msg": "Rubro no puede estar vacío"}), 400
            proveedor.rubro = rubro
        
        if direccion is not None:
            if not direccion:
                return jsonify({"msg": "Dirección no puede estar vacío"}), 400
            proveedor.direccion = direccion

        if cuenta_corriente is not None:
            proveedor.cuenta_corriente = cuenta_corriente

        if banco is not None:
            proveedor.banco = banco

        proveedor.update()

        data = {
            "msg": "Proveedor Modificado",
            "data": proveedor.serialize()
        }
        return jsonify(data), 200

    # PERMITE ELIMINAR PROVEEDOR
    if request.method == 'DELETE':
        if id:
            proveedor = Proveedor.query.get(id)
            if proveedor:
                proveedor.delete()
                return jsonify({"msg": f"Proveedor <{proveedor.nombre}> eliminado exitosamente."}),200
            else:
                return jsonify({"msg": "Proveedor no se encuentra registrado."}),400

@app.route('/api/productos', methods = ['GET', "POST"])
@app.route("/api/productos/<int:id>", methods=["GET", "PUT", "DELETE"])
def productos(id=None):
    # Devuelve listado de todos los productos
    if request.method == 'GET':
        if id is None:
            productos = Producto.query.all()
            if productos:
                productos = list(map(lambda producto: producto.serialize(),productos))
                return jsonify(productos), 200
            else:
                return jsonify({"msg" : "No hay datos de productos"}), 400
        if id is not None:
            producto = Producto.query.get(id)
            if producto:
                return jsonify(producto.serialize()), 200
            else:
                return jsonify({"msg" : "Producto no encontrado"}), 400

    # Creación de un nuevo producto
    if request.method == 'POST':
        data = request.get_json()
        if not data["sku"]:
            return jsonify({"msg" : "SKU del producto nuevo no puede estar vacio"})
        
        if not data["descripcion"]:
            return jsonify({"msg" : "Descripcion del producto nuevo no puede estar vacio"})
        
        if not data["codigo_barra"]:
            return jsonify({"msg" : "Codigo de Barra del producto nuevo no puede estar vacio"})
        
        if not data["unidad_entrega"]:
            return jsonify({"msg" : "Unidad de Entrega del producto nuevo no puede estar vacio"})
        
        if not data["categoria_id"]:
            return jsonify({"msg" : "Categoría del producto nuevo no puede estar vacio"})

        producto = Producto.query.filter_by(descripcion = data["descripcion"]).first()
        if producto:
            return jsonify({"msg" : "Producto ya existe"})
        
        producto = Producto()
        producto.sku = data["sku"]
        producto.descripcion = data["descripcion"]
        producto.codigo_barra = data["codigo_barra"]
        producto.unidad_entrega = data["unidad_entrega"]
        producto.categoria_id = data["categoria_id"] #revisar porque es una FK
        producto.save()
       
        return jsonify({"msg": "Producto creado exitosamente"}), 201

    # Actualización de un producto
    if request.method == 'PUT':
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({"msg" : "Producto no encontrado"}), 400
        else:
            valor_descripcion = request.json.get("descripcion", None)
            valor_cantidad = request.json.get("cantidad", None)
            valor_precio_venta_unitario = request.json.get("precio_venta_unitario", None)

            producto.descripcion = valor_descripcion
            producto.precio_venta_unitario = valor_precio_venta_unitario
            producto.update()

            return jsonify({"msg": "Producto actualizado exitosamente"}), 201

    # Elimina un producto
    if request.method == 'DELETE':
        producto = Producto.query.get(id)
        if producto:
            return jsonify({"msg" : "Producto eliminado exitosamente"})
        else:
            return jsonify({"msg" : "Producto no encontrado"}), 200
            producto.delete()

@app.route('/api/facturas-compras', methods = ['GET', "POST"])
@app.route("/api/facturas-compras/<int:id>", methods=["GET"])
def facturas_compras(id=None):

    # Devuelve todas las facturas registradas
    if request.method == 'GET':
        if id is None:
            facturas_compras = Factura_Compra.query.all()
            if facturas_compras:
                facturas_compras = list(map(lambda factura_compra: factura_compra.serialize(),facturas_compras))
                return jsonify(facturas_compras), 200
            else:
                return jsonify({"msg" : "No hay datos de facturas"}), 400
        if id is not None:
            facturas_compras = Factura_Compra.query.get(id)
            if facturas_compras:
                return jsonify(factura_compra.serialize()), 200
            else:
                return jsonify({"msg" : "Factura no encontrada"}), 400

    # Ingreso de nueva factura
    if request.method == 'POST':
        data = request.get_json()
        if not data["folio"]:
            return jsonify({"msg" : "Folio de nueva factura no puede estar vacio"})
        
        if not data["fecha_emision"]:
            return jsonify({"msg" : "Fecha de emisión de nueva factura no puede estar vacio"})
        
        if not data["fecha_recepcion"]:
            return jsonify({"msg" : "Fecha de recepción de nueva factura no puede estar vacio"})
        
        if not data["monto_neto"]:
            return jsonify({"msg" : "Monto Neto de nueva factura no puede estar vacio"})
        
        if not data["monto_iva"]:
            return jsonify({"msg" : "Monto IVA de nueva factura no puede estar vacio"})
        
        if not data["monto_otros_impuestos"] >=0:
            return jsonify({"msg" : "Monto de otros Impuestos de nueva factura no puede estar vacio"})
        
        if not data["monto_total"]:
            return jsonify({"msg" : "Monto Total de nueva factura no puede estar vacio"})
        
        if not data["proveedor_id"]:
            return jsonify({"msg" : "Id proveedor no puede estar vacio"})

        factura_compra = Factura_Compra.query.get(id) # Se debe verificar forma de no repetir ingreso de factura
        if factura_compra:
            return jsonify({"msg" : "Factura ya existe"})

        factura_compra = Factura_Compra()
        factura_compra.folio = data["folio"]
        factura_compra.fecha_emision = datetime.strptime(data["fecha_emision"], '%Y-%m-%d %H:%M:%S') 
        factura_compra.fecha_recepcion = datetime.strptime(data["fecha_recepcion"], '%Y-%m-%d %H:%M:%S') 
        factura_compra.monto_neto = data["monto_neto"]
        factura_compra.monto_iva = data["monto_iva"]
        factura_compra.monto_otros_impuestos = data["monto_otros_impuestos"]
        factura_compra.monto_total = data["monto_total"]
        factura_compra.proveedor_id = data["proveedor_id"]
        factura_compra.save()
       
        return jsonify({"msg": "Factura ingresada exitosamente"}), 201

@app.route('/api/salidas-inventario', methods = ['GET', "POST"])
@app.route("/api/salidas-inventario/<int:id>", methods=["GET", "PUT"])
def salidas_inventario(id=None):

    # Devuelve listado de todas las salidas de inventario por ventas
    if request.method == 'GET':
        if id is None:
            salidas_inventario = Salida_Inventario.query.all()
            if salidas_inventario:
                salidas_inventario = list(map(lambda salida_inventario: salida_inventario.serialize(),salidas_inventario))
                return jsonify(salidas_inventario), 200
            else:
                return jsonify({"msg" : "No hay registro de ventas"}), 400
        if id is not None:
            salida_inventario = Salida_Inventario.query.get(id)
            if salida_inventario:
                return jsonify(salida_inventario.serialize()), 200
            else:
                return jsonify({"msg" : "Registro de venta no encontrado"}), 400

    # Registro de salida de producto por venta
    if request.method == 'POST':
        data = request.get_json()
        if not data["cantidad"]:
            return jsonify({"msg" : "Cantidad del producto no puede estar vacia"})
        
        if not data["precio_costo_unitario"]:
            return jsonify({"msg" : "Precio Costo Unitario del producto no puede estar vacio"})
        
        if not data["costo_total"]:
            return jsonify({"msg" : "Costo Total del producto no puede estar vacio"})
        
        if not data["fecha_registro"]:
            return jsonify({"msg" : "Fecha de registro no puede estar vacia"})
        
        if not data["usuario_id"]:
            return jsonify({"msg" : "Usuario Id no puede estar vacio"})
        
        if not data["producto_id"]:
            return jsonify({"msg" : "Producto Id no puede estar vacio"})
        
        if not data["documento_venta_id"]:
            return jsonify({"msg" : "Documento de Venta Id no puede estar vacio"})
 
        salida_inventario = Salida_Inventario()
        salida_inventario.cantidad = data["cantidad"]
        salida_inventario.precio_costo_unitario = data["precio_costo_unitario"]
        salida_inventario.costo_total = data["costo_total"]
        salida_inventario.fecha_registro = data["fecha_registro"]
        salida_inventario.usuario_id = data["usuario_id"] #revisar porque es una FK
        salida_inventario.producto_id = data["producto_id"] #revisar porque es una FK
        salida_inventario.documento_venta_id = data["documento_venta_id"] #revisar porque es una FK
        salida_inventario.save()
       
        return jsonify({"msg": "Venta efectuada exitosamente"}), 201

    if request.method == 'PUT':
        salida_inventario = Salida_Inventario.query.get(id)
        if not salida_inventario:
            return jsonify({"msg" : "Salidad de inventario no encontrada"}), 400
        else:
            valor_cantidad = request.json.get("cantidad", None)
            
            salida_inventario.cantidad = valor_cantidad
            salida_inventario.update()

            return jsonify({"msg": "Salida de inventario modificada exitosamente"}), 201
@app.route("/api/documentos-venta", methods = ['GET', 'POST'])
@app.route("/api/documentos-venta/<int:id>", methods = ['GET'])
def documentos_venta(id = None):
    if request.method == 'GET':
        # DEVUELVE LISTADO CON TODOS LOS DOCUMENTOS DE VENTA
        if not id:
            documentos_venta = Documento_Venta.query.all()
            documentos_venta = list(map(lambda documento_venta: documento_venta.serialize(), documentos_venta))
            return jsonify(documentos_venta), 200

        # DEVUELVE DETALLE DE EMPRESA POR ID
        if id:
            documento_venta = Documento_Venta.query.get(id)
            if documento_venta:
                return jsonify(documento_venta.serialize()), 200
            else:
                return jsonify({"msg": "Documento de venta no se encuentra en el sistema"}), 400
    
    # PERMITE CREAR NUEVO DOCUMENTO VENTA
    if request.method == 'POST':

        tipo_documento = request.json.get("tipo_documento", None)
        numero_documento = request.json.get("numero_documento", None)
        fecha_emision = request.json.get("fecha_emision", None)
        monto_neto = request.json.get("monto_neto", None)
        monto_iva = request.json.get("monto_iva", None)
        monto_otros_impuestos = request.json.get("monto_otros_impuestos", None)
        monto_total = request.json.get("monto_total", None)
        forma_pago = request.json.get("forma_pago", None)

        if not tipo_documento:
            return jsonify({"msg": "Tipo de Documento no puede estar vacío"}), 400
        if not numero_documento:
            return jsonify({"msg": "Numero de Documento no puede estar vacío"}), 400
        if not fecha_emision:
            return jsonify({"msg": "Fecha de Emisión no puede estar vacío"}), 400
        if not monto_neto:
            return jsonify({"msg": "Monto Neto no puede estar vacío"}), 400
        if not monto_iva:
            return jsonify({"msg": "Monto IVA no puede estar vacío"}), 400
        if not monto_otros_impuestos and monto_otros_impuestos != 0:
            return jsonify({"msg": "Monto otros Impuestos no puede estar vacío"}), 400
        if not monto_total:
            return jsonify({"msg": "Monto Total no puede estar vacío"}), 400
        if not forma_pago:
            return jsonify({"msg": "Forma de Pago no puede estar vacío"}), 400
        
        documentos_venta = Documento_Venta.query.filter_by(numero_documento = numero_documento).all()
        documentos_venta = list(map(lambda documento_venta: documento_venta.serialize(), documentos_venta)) #DEVUELVE LISTA DE DICCIONARIOS CON MATCHES DE DOCUMENTOS DE VENTA
        for documento in documentos_venta:
            if documento['numero_documento'] == numero_documento and documento['tipo_documento'] == tipo_documento:
                return jsonify({"msg": "Numero de Documento y Tipo de Documento ya se encuentra ingresado"}), 400        

        documento_venta = Documento_Venta()
        documento_venta.tipo_documento = tipo_documento
        documento_venta.numero_documento = numero_documento
        documento_venta.fecha_emision = fecha_emision
        documento_venta.monto_neto = monto_neto
        documento_venta.monto_iva = monto_iva
        documento_venta.monto_otros_impuestos = monto_otros_impuestos
        documento_venta.monto_total = monto_total
        documento_venta.forma_pago = forma_pago

        documento_venta.save()    
        return jsonify(documento_venta.serialize()), 200

if __name__ == "__main__":
    manager.run()

    