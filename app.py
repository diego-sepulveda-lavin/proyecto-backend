from flask import Flask, request, jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from models import db, Empresa, Usuario, Producto
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
                return jsonify({"msg": "Usuario no se encuentra registrado"})
            
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
                    return jsonify({"msg": "Nombre no puede ir vacío."})
                usuario_actualizar.nombre = nombre

            if apellido is not None:
                if not apellido:
                    return jsonify({"msg": "Apellido no puede ir vacío."})
                usuario_actualizar.apellido = apellido 
                
            if rut is not None:
                if not rut:
                    return jsonify({"msg": "Rut no puede ir vacío."})
                usuario_actualizar.rut = rut

            if rol is not None:
                if not rol:
                    return jsonify({"msg": "Rol no puede ir vacío."})
                usuario_actualizar.rol = rol

            if email is not None:
                if not email:
                    return jsonify({"msg": "Email no puede ir vacío"})
                usuario_actualizar.email = email

            if password is not None:
                if not password:
                    return jsonify({"msg": "Password no puede ir vacío."})
                usuario_actualizar.password = password
            if status is not None:
                if not status:
                    return jsonify({"msg": "Status no puede ir vacío"})
                usuario_actualizar.status = status
            
            usuario_actualizar.update()
            data = {
                "msg": "Usuario Modificado",
                "usuario": usuario_actualizar.serialize()
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

@app.route('/api/productos', methods = ['GET'])
@app.route("/api/productos/<nombre_producto>", methods=["GET", "POST", "PUT", "DELETE"])
def productos(nombre_producto = None):
    if request.method == 'GET':
        if nombre_producto is None:
            productos = Producto.query.all()
            if productos:
                productos = list(map(lambda producto: producto.serialize(),productos))
                return jsonify(productos),200
            else:
                return jsonify({"msg" : "No hay datos de productos"}),400
        if nombre_producto is not None:
            producto = Producto.query.filter(Producto.descripcion.ilike(f"%{nombre_producto}")).first()
            if producto:
                return jsonify(producto.serialize()),200
            else:
                return jsonify({"msg" : "Producto no encontrado"})
    if request.method == 'POST':
        data = request.get_json()
        if data["sku"]=="" or data["sku"] == None:
            return jsonify({"msg" : "SKU del producto nuevo no puede estar vacio"})
        
        if data["descripcion"]=="" or data["descripcion"] == None:
            return jsonify({"msg" : "Descripcion del producto nuevo no puede estar vacio"})
        
        if data["codigo_barra"]=="" or data["codigo_barra"] == None:
            return jsonify({"msg" : "Codigo de Barra del producto nuevo no puede estar vacio"})
        
        if data["unidad_entrega"]=="" or data["unidad_entrega"] == None:
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
        producto.categoria_id = data["categoria_id"]
        producto.save()
       

        return jsonify({"msg": "Producto creado exitosamente"}), 201

if __name__ == "__main__":
    manager.run()
