from flask import Flask, request, jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from models import db, Empresa
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


if __name__ == "__main__":
    manager.run()
