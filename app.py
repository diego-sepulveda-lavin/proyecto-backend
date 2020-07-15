from flask import Flask, request, jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from models import db, Empresa, Usuario, Proveedor, Producto
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

@app.route('/api/empresas', methods = ['GET', "POST"])
@app.route('/api/empresas/<int:id>', methods = ['GET', "PUT","DELETE"])
#@jwt_required
def empresas(id=None):
    ### Ver Empresas ###
    if request.method == 'GET':
        if not id:
            empresas = Empresa.query.all()
            empresas = list(map(lambda empresa: empresa.serialize(),empresas))
            print(empresas)
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
            
            empresaActualizar = Empresa.query.get(id)
            if not empresaActualizar:
                return jsonify({"msg": "Empresa no se encuentra en el sistema"}),401

            rutOcupado = Empresa.query.filter_by(rut = rut).first()
            if rutOcupado and empresaActualizar.rut==rut:
                return jsonify({"msg": "Rut ya se encuentra registrado."}),401
            razonSocialOcupado = Empresa.query.filter_by(razon_social = razon_social).first()
            if razonSocialOcupado and empresaActualizar.razon_social == razon_social:
                return jsonify({"msg" : "Razon social ya se encuentra registrada."}), 401

            empresaActualizar.nombre = nombre
            empresaActualizar.rut = rut
            empresaActualizar.razon_social = razon_social
            empresaActualizar.rubro = rubro

            empresaActualizar.update()
            data = {
                "msg": "Empresa Modificada",
                "user": empresaActualizar.serialize()
            }
            return jsonify(data),200

    

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

@app.route("/api/proveedores", methods = ['GET', 'POST'])
@app.route("/api/proveedores/<int:id>", methods = ['GET', 'PUT', 'DELETE'])
def proveedores(id = None):
    
    if request.method == 'GET':
        # DEVUELVE LISTADO CON TODOS LOS PROVEEDORES
        if not id:
            proveedores = Proveedor.query.all()
            proveedores = list(map(lambda proveedor: proveedor.serialize(), proveedores))
            return jsonify(proveedores), 200

        # DEVUELVE DETALLE DE EMPRESA POR ID
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
            return jsonify({"msg": "Rut de empresa ya se encuentra registrado"}), 401
        check_razon_social = Proveedor.query.filter_by(razon_social = razon_social).first()
        if check_razon_social:
            return jsonify({"msg":"Razon social de empresa ya se encuentra registrado"}), 401

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
    
    if request.method == 'PUT':
        proveedor = Proveedor.query.get(id)
        if not proveedor:
            return jsonify({"msg": "Empresa no se encuentra en el sistema"}), 401
        
        
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
        if check_rut and check_rut.rut != rut:
            return jsonify({"msg": "Rut de empresa ya se encuentra registrado"}), 401

        check_razon_social = Proveedor.query.filter_by(razon_social = razon_social).first()
        if check_razon_social and check_razon_social.razon_social != razon_social:
            return jsonify({"msg":"Razon social de empresa ya se encuentra registrado"}), 401
             
        proveedor.nombre = nombre
        proveedor.rut = rut
        proveedor.razon_social = razon_social
        proveedor.rubro = rubro
        proveedor.direccion = direccion
        proveedor.cuenta_corriente = cuenta_corriente
        proveedor.banco = banco

        proveedor.update()

        data = {
            "msg": "Proveedor Modificado",
            "data": proveedor.serialize()
        }
        return jsonify(data), 200

@app.route('/api/productos', methods = ['GET', "POST"])
@app.route("/api/productos/<int:id>", methods=["GET", "PUT", "DELETE"])
def productos(id=None):
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

    if request.method == 'DELETE':
        producto = Producto.query.get(id)
        if producto:
            return jsonify({"msg" : "Producto eliminado exitosamente"})
        else:
            return jsonify({"msg" : "Producto no encontrado"}), 200
            producto.delete()

if __name__ == "__main__":
    manager.run()
