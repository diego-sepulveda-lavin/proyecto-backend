from flask import Flask, request, jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from models import db, Empresa, Usuario, Proveedor
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

@app.route('/api/empresas', methods = ['GET'])
def empresas():
    if request.method == 'GET':
        empresas = Empresa.query.all()
        empresas = list(map(lambda empresa: empresa.serialize(),empresas))
        print(empresas)
        return jsonify(empresas),200

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
def proveedores():
    if request.method == 'GET':
        proveedores = Proveedor.query.all()
        proveedores = list(map(lambda proveedor: proveedor.serialize(), proveedores))
        return jsonify(proveedores), 200

    if request.method == 'POST':
        nombre = request.json.get("nombre",None)
        rut = request.json.get("rut",None)
        razon_social = request.json.get("razon_social",None)
        rubro = request.json.get("rubro",None)
        direccion = request.json.get("direccion",None)
        cuenta_corriente = request.json.get("cuenta_corriente",None)
        banco = request.json.get("banco",None)

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
        
        return jsonify({"msg":"ok"}),200

if __name__ == "__main__":
    manager.run()
