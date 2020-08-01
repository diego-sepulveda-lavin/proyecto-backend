import datetime
import os
import time

from flask import Flask, request, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_mail import Mail, Message
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from werkzeug.utils import secure_filename

from config import Development
from models import db, Empresa, Usuario, Producto, Categoria, Proveedor, Factura_Compra, Entrada_Inventario, \
    Salida_Inventario, Documento_Venta, Cuadratura_Caja

ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.url_map.strict_slashes = False

app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
mail = Mail(app)

app.config.from_object(Development)
db.init_app(app)
Migrate(app, db)
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg'}

# Using the expired_token_loader decorator, we will now call
# this function whenever an expired but otherwise valid access
# token attempts to access an endpoint


@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'msg': 'La sesión ha caducado, por favor Logearse.'.format(token_type)
    }), 401


def allowed_images_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_IMG


@app.route('/api/email', methods=['POST'])
def email():
    nombre = request.json.get('nombre', None)
    email = request.json.get('email', None)
    consulta = request.json.get('consulta', None)

    if not nombre:
        return jsonify({"msg": "Por favor ingresa tu nombre"}), 400
    if not email:
        return jsonify({"msg": "Por favor ingresa tu email"}), 400
    if not consulta:
        return jsonify({"msg": "Por favor ingresa tu constulta"}), 400
    
    msg = Message('Consulta desde Formulario Landing Page', recipients=[os.environ.get('MAIL_DEFAULT_RECIPIENT')])
    msg.body = f"Nombre: {nombre}\nEmail de contacto: {email}\nConsulta: {consulta}"
    mail.send(msg)
    return jsonify({"msg": "Muchas gracias por contactarte con nosotros"}), 200


@app.route('/api/recuperar-email', methods=['POST'])
def recuperar_email():
    email = request.json.get('email', None)

    if not email:
        return jsonify({"msg": "Debes ingresar un email"}), 400
    
    check_email = Usuario.query.filter_by(email=email).first()

    if not check_email:
        return jsonify({"msg": "El email ingresado no es correcto"}), 400

    if check_email:
        expires = datetime.timedelta(hours=1)
        access_token = create_access_token(identity=check_email.email, expires_delta=expires)
        url = "http://localhost:3000/nueva-password/"
        msg = Message('Email de recuperación de contraseña DSHL', recipients=[email])
        msg.html = f"""<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    </head>
                    <body>
                        <p>Este correo se autogeneró, debido a que solicitaste un cambio de contraseña</p>
                        <p>El link para recuperar tu contraseña es el siguiente: <a href="{url}{access_token}">Click aqui</a></p>
                    </body>
                    </html>"""
        mail.send(msg)

        return jsonify({"msg": "Se ha enviado un correo para recuperar la contraseña"}), 200


@app.route('/api/nueva-password/', methods=['PUT'])
@jwt_required
def nueva_password():
    
    current_user = get_jwt_identity()
    password = request.json.get('password', None)
    repassword = request.json.get('repassword', None)

    if not password or not repassword:
        return jsonify({"msg": "Los campos no pueden estar vacios"}), 400
    
    if len(password) < 6:
        return jsonify({"msg": "Contraseña debe contener más de 5 caracteres"}), 400

    if password != repassword:
        return jsonify({"msg": "Ambas contraseñas deben ser iguales"}), 400
    
    usuario = Usuario.query.filter_by(email=current_user).first()
    usuario.password = bcrypt.generate_password_hash(password).decode("utf-8")
    usuario.update()

    return jsonify({"msg": "Su contraseña ha sido modificada, redireccionando..."}), 200
    

@app.route('/api/images/<filename>')
def uploaded_file(filename):
    # Se le indica en que carpeta guardará la foto, en este caso "static/images" donde static se definio en el config.py
    # en la variable upload_folder
    return send_from_directory(app.config['UPLOAD_FOLDER']+"/images", filename)


@app.route("/api/login/", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if not email:
        return jsonify({"msg": "Email no puede estar vacío"}), 400
    if not password:
        return jsonify({"msg": "Contraseña no puede estar vacía"}), 400

    user = Usuario.query.filter_by(email=email).first()
    # Revisa si existe el usuario en DB y compara contraseñas
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"msg": "Email o contraseña inválidos"}), 401
    
    expires = datetime.timedelta(days=1)
    access_token = create_access_token(identity=user.email, expires_delta=expires)

    data = {
        "access_token": access_token,
        "user": user.serialize()
    }

    return jsonify(data), 200


@app.route('/api/empresas', methods=['GET', "POST"])
@app.route('/api/empresas/<int:id>', methods=['GET', "PUT", "DELETE"])
@jwt_required
def empresas(id=None):

    # Ver Empresas
    if request.method == 'GET':
        if not id:
            empresas = Empresa.query.all()
            if not empresas:
                return jsonify({"msg": "No hay empresas registradas."})
            empresas = list(map(lambda empresa: empresa.serialize(), empresas))
            return jsonify(empresas), 200

    # Ver Empresa por ID
        empresa = Empresa.query.get(id)
        if empresa:
            return jsonify(empresa.serialize()), 200
        return jsonify({"msg": "Empresa no se encuentra en el sistema"}), 400

    # Eliminar Empresa por ID
    if request.method == "DELETE":
        if id:
            empresa = Empresa.query.get(id)
            if empresa:
                empresa.delete()
                return jsonify({"msg": f"Empresa <{empresa.nombre}> eliminada exitosamente!"}), 200
            else:
                return jsonify({"msg": "Empresa no se encuentra en el sistema"}), 400

    # Ingresar Empresa
    if request.method == "POST":
        nombre = request.json.get("nombre", None)
        rut = request.json.get("rut", None)
        razon_social = request.json.get("razon_social", None)
        rubro = request.json.get("rubro", None)

        if not nombre:
            return jsonify({"msg": "Nombre de empresa no puede estar vacío"}), 400
        if not rut:
            return jsonify({"msg": "Rut de empresa no puede estar vacío"}), 400
        if not razon_social:
            return jsonify({"msg": "Razon Social de empresa no puede estar vacío"}), 400
        if not rubro:
            return jsonify({"msg": "Rubro de empresa no puede estar vacío"}), 400
        
        valida_rut_existente = Empresa.query.filter_by(rut=rut).first()
        if valida_rut_existente:
            return jsonify({"msg": "Rut de empresa ya se encuentra registrado"}), 400

        valida_razon_social_existente = Empresa.query.filter_by(razon_social=razon_social).first()
        if valida_razon_social_existente:
            return jsonify({"msg": "Razon social de empresa ya se encuentra registrado"}), 400

        empresa = Empresa()
        empresa.nombre = nombre
        empresa.rut = rut
        empresa.razon_social = razon_social
        empresa.rubro = rubro
        empresa.save()

        return jsonify(empresa.serialize()), 200

    # Actualizar Empresa by ID
    if request.method == "PUT":
        if id:
            empresa_actualizar = Empresa.query.get(id)
            if not empresa_actualizar:
                return jsonify({"msg": "Empresa no se encuentra en el sistema"}), 400

            nombre = request.json.get("nombre", None)
            rut = request.json.get("rut", None)
            razon_social = request.json.get("razon_social", None)
            rubro = request.json.get("rubro", None)

            rut_ocupado = Empresa.query.filter_by(rut=rut).first()
            if rut_ocupado and rut_ocupado.id != id:
                return jsonify({"msg": "Rut ya se encuentra registrado."}), 400

            razon_social_ocupado = Empresa.query.filter_by(razon_social=razon_social).first()
            if razon_social_ocupado and razon_social_ocupado != id:
                return jsonify({"msg": "Razon social ya se encuentra registrada."}), 400

            if nombre is not None:
                if not nombre:
                    return jsonify({"msg": "Nombre no puede ir vacío"}), 400
                empresa_actualizar.nombre = nombre
            
            if rut is not None:
                if not rut:
                    return jsonify({"msg": "Rut no puede ir vacío"}), 400
                empresa_actualizar.rut = rut
            
            if razon_social is not None:
                if not razon_social:
                    return jsonify({"msg": "Razon social no puede ir vacío"}), 400
                empresa_actualizar.razon_social = razon_social
            
            if rubro is not None:
                if not rubro:
                    return jsonify({"msg": "Rubro no puede ir vacío"}), 400
                empresa_actualizar.rubro = rubro

            empresa_actualizar.update()
            return jsonify(empresa_actualizar.serialize()), 200


@app.route("/api/valida-Caja", methods=["POST"])
@jwt_required
def valida_caja():
    administrador = request.json.get("administrador", None)
    password = request.json.get("password", None)

    if not administrador or not password:
        return jsonify({"msg": "Faltan campos de Administrador"}), 400

    admin_valido = Usuario.query.filter_by(codigo=administrador).first()
    if not admin_valido:
        return jsonify({"msg": "Administrador inválido"}), 400
    if admin_valido.rol != "Admin":
        return jsonify({"msg": "Dato ingresado no figura como Administrador"}), 400
    if bcrypt.check_password_hash(admin_valido.password, password):
        return jsonify({"msg": "Apertura Exitosa"}), 200
    else:
        return jsonify({"msg": "Validación Administrador incorrecta"}), 400


@app.route("/api/usuarios", methods=["GET", "POST"])
@app.route("/api/usuarios/<int:id>", methods=["GET", "DELETE", "PUT"])
@jwt_required
def usuarios(id=None):

    # Ver Usuarios
    if request.method == "GET":
        if id is None:
            usuarios = Usuario.query.all()
            if not usuarios:
                return jsonify({"msg": "No hay usuarios"})
            usuarios = list(map(lambda usuario: usuario.serialize(), usuarios))
            return jsonify(usuarios), 200

        # Ver Usuario by ID
        else:
            usuario = Usuario.query.get(id)
            if not usuario:
                return jsonify({"msg": "No se encuentra usuario."}), 400
            return jsonify(usuario.serialize()), 200

    # Eliminar Usuario
    if request.method == "DELETE":
        if id:
            usuario = Usuario.query.get(id)
            if usuario:
                usuario.delete()
                return jsonify({"msg": f"Usuario <{usuario.nombre}> eliminado exitosamente."}), 200
            else:
                return jsonify({"msg": "Usuario no se encuentra registrado."}), 400

    # Insertar Usuario
    if request.method == "POST":        
        nombre = request.form.get("nombre", None)
        apellido = request.form.get("apellido", None)
        rut = request.form.get("rut", None)
        rol = request.form.get("rol", None)
        email = request.form.get("email", None)
        password = request.form.get("password", None)
        # foto = request.form.get("foto", None)

        if not nombre:
            return jsonify({"msg": "Nombre no puede estar vacío"}), 400
        if not apellido:
            return jsonify({"msg": "Apellido no puede estar vacío"}), 400
        if not rut:
            return jsonify({"msg": "Rut no puede estar vacío"}), 400
        if not rol:
            return jsonify({"msg": "Rol no puede estar vacío"}), 400
        if not email:
            return jsonify({"msg": "Email no puede estar vacío"}), 400
        if not password:
            return jsonify({"msg": "Password no puede estar vacío"}), 400
        # if not data["empresa_id"]:
        #    return jsonify({"msg":"Empresa_id no puede estar vacío"}),400
        
        rut_ocupado = Usuario.query.filter_by(rut=rut).first()
        if rut_ocupado:
            return jsonify({"msg": "Rut ya se encuentra registrado."}), 400
        email_ocupado = Usuario.query.filter_by(email=email).first()
        if email_ocupado:
            return jsonify({"msg": "Email ya se encuentra registrado."}), 400

        filename = "without-photo.png"
        if 'foto' in request.files:
            file = request.files['foto']    
            if file and allowed_images_file(file.filename):
                filename = secure_filename(file.filename)
                timestr = time.strftime("%Y%m%d-%H%M%S")
                filename = timestr+"-"+filename
                filename = filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER']+"/images", filename))
            else:
                return jsonify({"msg": "File Not Allowed!"}), 400 

        usuario = Usuario()
        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.rut = rut
        usuario.rol = rol
        usuario.email = email
        usuario.password = bcrypt.generate_password_hash(password).decode("utf-8")
        usuario.empresa_id = 1 
        usuario.foto = filename
        usuario.save()
        usuario.codigo = usuario.generaCodigo()
        usuario.update()

        return jsonify(usuario.serialize()), 200

    # Actualizar Usuario
    if request.method == "PUT":
        if id:
            usuario_actualizar = Usuario.query.get(id)
            if not usuario_actualizar:
                return jsonify({"msg": "Usuario no se encuentra registrado"}), 400
            
            nombre = request.form.get("nombre", None)
            apellido = request.form.get("apellido", None)
            rut = request.form.get("rut", None)
            rol = request.form.get("rol", None)
            email = request.form.get("email", None)
            password = request.form.get("password", None)
            status = request.form.get("status", None)
        
            if status == "true":
                status = True
            elif status == "false":
                status = False

            rut_ocupado = Usuario.query.filter_by(rut=rut).first()
            if rut_ocupado and rut_ocupado.id != id:
                return jsonify({"msg": "Rut ya se encuentra registrado."}), 400

            email_ocupado = Usuario.query.filter_by(email=email).first()
            if email_ocupado and email_ocupado.id != id:
                return jsonify({"msg": "Correo ya se encuentra registrado."}), 400

            if nombre is not None:
                if nombre == "":
                    return jsonify({"msg": "Nombre no puede ir vacío."}), 400
                usuario_actualizar.nombre = nombre

            if apellido is not None:
                if apellido == "":
                    return jsonify({"msg": "Apellido no puede ir vacío."}), 400
                usuario_actualizar.apellido = apellido 
                
            if rut is not None:
                if rut == "":
                    return jsonify({"msg": "Rut no puede ir vacío."}), 400
                usuario_actualizar.rut = rut

            if rol is not None:
                if rol == "":
                    return jsonify({"msg": "Rol no puede ir vacío."}), 400
                usuario_actualizar.rol = rol

            if email is not None:
                if email == "":
                    return jsonify({"msg": "Email no puede ir vacío"}), 400
                usuario_actualizar.email = email

            if password is not None:
                if password == "":
                    return jsonify({"msg": "Password no puede ir vacío."}), 400
                usuario_actualizar.password = bcrypt.generate_password_hash(password).decode("utf-8")
            if status is not None:
                if status != False and status != True:
                    return jsonify("Status debe ser true o false"), 400
                usuario_actualizar.status = status

            # filename = "without-photo.png"
            if 'foto' in request.files:
                file = request.files['foto']    
                if file and allowed_images_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestr = time.strftime("%Y%m%d-%H%M%S")
                    filename = timestr+"-"+filename
                    file.save(os.path.join(app.config['UPLOAD_FOLDER']+"/images", filename))
                    usuario_actualizar.foto = filename
                else:
                    return jsonify({"msg": "File Not Allowed!"}), 400
            
            usuario_actualizar.update()
            
            return jsonify(usuario_actualizar.serialize()), 200


@app.route("/api/entradas-inventario", methods=["GET", "POST"])
@app.route("/api/entradas-inventario/<int:id>", methods=["GET", "PUT"])
@jwt_required
def entrada_inventario(id=None):

    # VER TODAS LAS ENTRADAS DE INVENTARIO
    if request.method == "GET":
        if id is None:
            entradas = Entrada_Inventario.query.all()
            if entradas:
                entradas = list(map(lambda entrada: entrada.serialize(), entradas))
                return jsonify(entradas), 200
            else:
                return jsonify({"msg": "No hay entradas disponibles."}), 400

    # VER UNA ENTRADA DE INVENTARIO POR ID
        entrada = Entrada_Inventario.query.get(id)
        if entrada:
            return jsonify(entrada.serialize()), 200
        else:
            return jsonify({"msg": "No existe registro asociado."}), 400
    
    # INSERTAR UNA ENTRADA DE INVENTARIO POR ID
    if request.method == "POST":
        data = request.get_json()

        if data["cantidad"] <= 0:
            return jsonify({"msg": "Cantidad debe ser mayor a 0"}), 400
        if data["precio_costo_unitario"] <= 0:
            return jsonify({"msg": "Precio costo debe ser mayor a 0"}), 400

        entrada_inventario = Entrada_Inventario()
        entrada_inventario.cantidad = data["cantidad"]
        entrada_inventario.precio_costo_unitario = data["precio_costo_unitario"]
        entrada_inventario.costo_total = entrada_inventario.genera_costo_total()
        entrada_inventario.usuario_id = 1  # Cambiar
        entrada_inventario.producto_id = 1  # Cambiar
        entrada_inventario.factura_compra_id = 1  # Cambiar
        entrada_inventario.save()
        return jsonify({"msg": "Entrada guardada exitosamente."}), 200

    # ACTUALIZAR UNA ENTRADA DE INVENTARIO POR ID
    if request.method == "PUT":
        entrada_actualizar = Entrada_Inventario.query.get(id)
        if not entrada_actualizar:
            return jsonify({"msg": "No existe registro."})
        
        cantidad = request.json.get("cantidad", None)
        precio_costo_unitario = request.json.get("precio_costo_unitario", None)

        if cantidad is not None:
            if cantidad < 0:
                return jsonify({"msg": "Cantidad no puede ser menor a 0"}), 400
            entrada_actualizar.cantidad = cantidad
        if precio_costo_unitario is not None:
            if precio_costo_unitario <= 0:
                return jsonify({"msg": "Precio costo unitario no puede ser menor a 0"}), 400
            entrada_actualizar.precio_costo_unitario = precio_costo_unitario
            
        entrada_actualizar.costo_total = entrada_actualizar.genera_costo_total() 
        entrada_actualizar.update() 
        return jsonify({"msg": "Producto modificado."}), 200


@app.route('/api/salidas-inventario', methods=['GET', "POST"])
@app.route("/api/salidas-inventario/<int:id>", methods=["GET", "PUT"])
@jwt_required
def salidas_inventario(id=None):

    # Devuelve listado de todas las salidas de inventario por ventas
    if request.method == 'GET':
        if id is None:
            salidas_inventario = Salida_Inventario.query.all()
            if salidas_inventario:
                salidas_inventario = list(map(lambda salida_inventario: salida_inventario.serialize(), salidas_inventario))
                return jsonify(salidas_inventario), 200
            else:
                return jsonify({"msg": "No hay registro de ventas"}), 400
        if id is not None:
            salida_inventario = Salida_Inventario.query.get(id)
            if salida_inventario:
                return jsonify(salida_inventario.serialize()), 200
            else:
                return jsonify({"msg": "Registro de venta no encontrado"}), 400

    # Registro de salida de producto por venta
    if request.method == 'POST':
        data = request.get_json()
        if not data["cantidad"]:
            return jsonify({"msg": "Cantidad del producto no puede estar vacía"}), 400
        
        if not data["precio_costo_unitario"]:
            return jsonify({"msg": "Precio Costo Unitario del producto no puede estar vacío"}), 400
        
        if not data["usuario_id"]:
            return jsonify({"msg": "Usuario Id no puede estar vacío"}), 400
        
        if not data["producto_id"]:
            return jsonify({"msg": "Producto Id no puede estar vacío"}), 400
        
        if not data["documento_venta_id"]:
            return jsonify({"msg": "Documento de Venta Id no puede estar vacío"}), 400

        salida_inventario = Salida_Inventario()
        salida_inventario.cantidad = data["cantidad"]
        salida_inventario.precio_costo_unitario = data["precio_costo_unitario"]
        salida_inventario.costo_total = salida_inventario.genera_costo_total()  # MULTIPLICACION DE CANTIDAD POR COSTO
        salida_inventario.usuario_id = data["usuario_id"]  # revisar porque es una FK
        salida_inventario.producto_id = data["producto_id"]  # revisar porque es una FK
        salida_inventario.documento_venta_id = data["documento_venta_id"]  # revisar porque es una FK
        salida_inventario.save()

        return jsonify({"msg": "Venta efectuada exitosamente"}), 201

    if request.method == 'PUT':
        salida_inventario = Salida_Inventario.query.get(id)
        if not salida_inventario:
            return jsonify({"msg": "Salidad de inventario no encontrada"}), 400
        else:
            valor_cantidad = request.json.get("cantidad", None)
            
            salida_inventario.cantidad = valor_cantidad
            salida_inventario.update()

            return jsonify({"msg": "Salida de inventario modificada exitosamente"}), 201


@app.route('/api/facturas-compras', methods=['GET', "POST"])
@app.route("/api/facturas-compras/<int:id>", methods=["GET", 'PUT'])
@jwt_required
def facturas_compras(id=None):

    # Devuelve todas las facturas registradas
    if request.method == 'GET':
        if id is None:
            facturas_compras = Factura_Compra.query.all()
            if facturas_compras:
                facturas_compras = list(map(lambda factura_compra: factura_compra.serialize(), facturas_compras))
                return jsonify(facturas_compras), 200
            else:
                return jsonify({"msg": "No hay datos de facturas"}), 400
        if id is not None:
            factura_compra = Factura_Compra.query.get(id)
            if factura_compra:
                return jsonify(factura_compra.serialize()), 200
            else:
                return jsonify({"msg": "Factura no encontrada"}), 400

    # Ingreso de nueva factura
    if request.method == 'POST':
        data = request.get_json()

        if not data["factura"]["folio"]:
            return jsonify({"msg": "Folio de nueva factura no puede estar vacío"}), 400
        
        if not data["factura"]["fecha_emision"]:
            return jsonify({"msg": "Fecha de emisión de nueva factura no puede estar vacía"}), 400
        
        if not data["factura"]["fecha_recepcion"]:
            return jsonify({"msg": "Fecha de recepción de nueva factura no puede estar vacía"}), 400
        
        if not float(data["factura"]["monto_neto"]):
            return jsonify({"msg": "Monto Neto de nueva factura no puede estar vacío"}), 400
        
        if not float(data["factura"]["monto_iva"]):
            return jsonify({"msg": "Monto IVA de nueva factura no puede estar vacío"}), 400
        
        if not float(data["factura"]["monto_otros_impuestos"]) >= 0:
            return jsonify({"msg": "Monto de otros Impuestos de nueva factura no puede estar vacío"}), 400
        
        if not float(data["factura"]["monto_total"]):
            return jsonify({"msg": "Monto Total de nueva factura no puede estar vacío"}), 400
        
        if not data["factura"]["proveedor_id"]:
            return jsonify({"msg": "Id proveedor no puede estar vacío"}), 400

        facturas_compras = Factura_Compra.query.filter_by(folio=data["factura"]["folio"]).all()  # Se debe verificar
        # forma de no repetir ingreso de factura
        facturas_compras = list(map(lambda factura_compra: factura_compra.serialize(), facturas_compras))
        for factura in facturas_compras:
            if factura["folio"] == data["factura"]["folio"] and factura["proveedor_id"] == data["facturas"]["proveedor_id"]:
                return jsonify({"msg": "Factura ya existe"})

        timestr = time.strftime(" %H:%M:%S")
        factura_compra = Factura_Compra()
        factura_compra.folio = int(data["factura"]["folio"])
        factura_compra.fecha_emision = data["factura"]["fecha_emision"]+timestr
        factura_compra.fecha_recepcion = data["factura"]["fecha_recepcion"]+timestr
        factura_compra.monto_neto = float(data["factura"]["monto_neto"])
        factura_compra.monto_iva = float(data["factura"]["monto_iva"])
        factura_compra.monto_otros_impuestos = float(data["factura"]["monto_otros_impuestos"])
        factura_compra.monto_total = float(data["factura"]["monto_total"])
        factura_compra.proveedor_id = int(data["factura"]["proveedor_id"])
        
        for entrada_inv in data["factura"]["entradas_inventario"]:
            entrada_inventario = Entrada_Inventario()
            entrada_inventario.cantidad = entrada_inv["cantidad"]
            entrada_inventario.precio_costo_unitario = entrada_inv["precio_costo_unitario"]
            entrada_inventario.costo_total = entrada_inv["costo_total"]
            entrada_inventario.usuario_id = entrada_inv["usuario_id"]
            # entrada_inventario.factura_compra_id = factura_compra.id
            entrada_inventario.producto_id = entrada_inv["producto_id"]

            factura_compra.entradas_I.append(entrada_inventario)

        factura_compra.save()

        return jsonify({"msg": "Factura creada exitosamente."}), 201

    # Modificacion factura
    if request.method == 'PUT':
        data = request.get_json()

        if not data["folio"]:
            return jsonify({"msg": "Folio de factura no puede estar vacío"}), 400

        if not data["fecha_emision"]:
            return jsonify({"msg": "Fecha de emisión de factura no puede estar vacía"}), 400

        if not data["fecha_recepcion"]:
            return jsonify({"msg": "Fecha de recepción de factura no puede estar vacía"}), 400

        if not data["monto_neto"]:
            return jsonify({"msg": "Monto Neto de factura no puede estar vacío"}), 400

        if not data["monto_iva"]:
            return jsonify({"msg": "Monto IVA de factura no puede estar vacío"}), 400
        
        if not data["monto_otros_impuestos"] and data["monto_otros_impuestos"] != 0:
            return jsonify({"msg": "Monto de otros Impuestos de factura no puede estar vacío"}), 400
        
        if not data["monto_total"]:
            return jsonify({"msg": "Monto Total de factura no puede estar vacío"}), 400

        if not data["proveedor_id"]:
            return jsonify({"msg": "Id proveedor no puede estar vacío"}), 400

        factura_a_modificar = Factura_Compra.query.get(id)  # Se busca factura a modificar en DB
        if not factura_a_modificar:
            return jsonify({"msg": "Factura no encontrada"}), 400
        if factura_a_modificar:
            factura_a_modificar.folio = data["folio"]
            factura_a_modificar.fecha_emision = data["fecha_emision"]+time.strftime(" %H:%M:%S")
            factura_a_modificar.fecha_recepcion = data["fecha_recepcion"]+time.strftime(" %H:%M:%S")
            factura_a_modificar.monto_neto = data["monto_neto"]
            factura_a_modificar.monto_iva = data["monto_iva"]
            factura_a_modificar.monto_otros_impuestos = data["monto_otros_impuestos"]
            factura_a_modificar.monto_total = data["monto_total"]
            factura_a_modificar.proveedor_id = data['proveedor_id']

            entradas_inventario = Entrada_Inventario.query.filter_by(factura_compra_id=id).all()
            for entrada_inventario in entradas_inventario:
                db.session.delete(entrada_inventario)

            for entrada_inv_enviada in data['entradas_inventario']:
                entrada_inventario = Entrada_Inventario()
                entrada_inventario.cantidad = entrada_inv_enviada["cantidad"]
                entrada_inventario.precio_costo_unitario = entrada_inv_enviada["precio_costo_unitario"]
                entrada_inventario.costo_total = entrada_inv_enviada["costo_total"]
                entrada_inventario.usuario_id = entrada_inv_enviada["usuario_id"]
                entrada_inventario.producto_id = entrada_inv_enviada["producto_id"]
                factura_a_modificar.entradas_I.append(entrada_inventario)

            factura_a_modificar.update()
            return jsonify({"msg": "Factura modificada"}), 200
            

@app.route('/api/productos', methods=['GET', "POST", "PUT"])
@app.route("/api/productos/<int:id>", methods=["GET", "DELETE"])
@jwt_required
def productos(id=None):

    # Devuelve listado de todos los productos
    if request.method == 'GET':
        if id is None:
            productos = Producto.query.all()
            if productos:
                productos = list(map(lambda producto: producto.serialize(), productos))
                return jsonify(productos), 200
            else:
                return jsonify({"msg": "No hay datos de productos"}), 400
        if id is not None:
            producto = Producto.query.get(id)
            if producto:
                return jsonify(producto.serialize()), 200
            else:
                return jsonify({"msg": "Producto no encontrado"}), 400

    # Creación de un nuevo producto
    if request.method == 'POST':
        data = request.get_json()
        if not str(data["sku"]):
            return jsonify({"msg": "SKU del producto nuevo no puede estar vacío"}), 400
        
        if not data["descripcion"]:
            return jsonify({"msg": "Descripción del producto nuevo no puede estar vacía"}), 400
        
        if not data["codigo_barra"]:
            return jsonify({"msg": "Código de Barra del producto nuevo no puede estar vacío"}), 400
        
        if not data["unidad_entrega"]:
            return jsonify({"msg": "Unidad de Entrega del producto nuevo no puede estar vacía"}), 400
        
        if not data["categoria_id"]:
            return jsonify({"msg": "Seleccione Categoría"}), 400

        producto_cb = Producto.query.filter_by(codigo_barra=data["codigo_barra"]).first()
        producto_desc = Producto.query.filter_by(descripcion=data["descripcion"]).first()
        producto_sku = Producto.query.filter_by(sku=data["sku"]).first()

        if producto_cb:
            return jsonify({"msg": "Código de barra ya existe"}), 400
  
        if producto_sku:
            return jsonify({"msg": "SKU ya existe"}), 400
        
        producto = Producto()
        producto.sku = data["sku"]
        producto.descripcion = data["descripcion"]
        producto.codigo_barra = data["codigo_barra"]
        producto.unidad_entrega = data["unidad_entrega"]
        producto.precio_venta_unitario = data["precio_venta_unitario"]
        producto.categoria_id = data["categoria_id"]  # revisar porque es una FK
        producto.save()
       
        return jsonify(producto.serialize()), 200

    # Actualización de un producto
    if request.method == 'PUT':

        data = request.get_json()

        if not data:
            return jsonify({"msg": f"La solicitud no puede estar vacía"}), 400

        for producto in data:
            id = producto.get("id", None)
            sku = producto.get("sku", None)
            descripcion = producto.get("descripcion", None)
            codigo_barra = producto.get("codigo_barra", None)
            unidad_entrega = producto.get("unidad_entrega", None)
            categoria_id = producto.get("categoria_id", None)
            precio_venta_unitario = producto.get("precio_venta_unitario", None)
            

            if not sku:
                return jsonify({"msg": f"SKU del producto id {id} no puede estar vacío"}), 400

            if not descripcion:
                return jsonify({"msg": f"Descripción del producto id {id} no puede estar vacía"}), 400

            if not codigo_barra:
                return jsonify({"msg": f"Código de barra del producto id {id} no puede estar vacío"}), 400

            if not unidad_entrega:
                return jsonify({"msg": f"Unidad de entrega del producto id {id} no puede estar vacía"}), 400

            if not categoria_id:
                return jsonify({"msg": f"Categoría del producto id {id} no puede estar vacía"}), 400

            if not precio_venta_unitario:
                return jsonify({"msg": f"Precio venta unitario del producto id {id} no puede estar vacío"}), 400

            producto_a_modificar = Producto.query.get(id)
            if producto_a_modificar:
                producto_a_modificar.descripcion = descripcion
                producto_a_modificar.codigo_barra = codigo_barra
                producto_a_modificar.unidad_entrega = unidad_entrega
                producto_a_modificar.categoria_id = categoria_id
                producto_a_modificar.precio_venta_unitario = precio_venta_unitario
                
                db.session.add(producto_a_modificar)
                
            else:
                continue
        
        db.session.commit() 

        return jsonify("msg": "Productos modificados exitosamente"), 200

    # Elimina un producto
    if request.method == 'DELETE':
        producto = Producto.query.get(id)
        if producto:
            producto.delete()
            return jsonify({"msg": "Producto eliminado exitosamente"}), 200
        else:
            return jsonify({"msg": "Producto no encontrado"}), 400


@app.route("/api/documentos-venta", methods=['GET', 'POST'])
@app.route("/api/documentos-venta/<int:id>", methods=['GET'])
@jwt_required
def documentos_venta(id=None):

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
        data = request.get_json()

        if not data['datosVenta']["tipo_documento"]:
            return jsonify({"msg": "Tipo de Documento no puede estar vacío"}), 400
        if not data['datosVenta']["numero_documento"]:
            return jsonify({"msg": "Numero de Documento no puede estar vacío"}), 400
        if not data['datosVenta']["monto_neto"]:
            return jsonify({"msg": "Monto Neto no puede estar vacío"}), 400
        if not data['datosVenta']["monto_iva"]:
            return jsonify({"msg": "Monto IVA no puede estar vacío"}), 400
        if not data['datosVenta']["monto_total"]:
            return jsonify({"msg": "Monto Total no puede estar vacío"}), 400
        if not data['datosVenta']["forma_pago"]:
            return jsonify({"msg": "Forma de Pago no puede estar vacío"}), 400
        
        documentos_venta = Documento_Venta.query.filter_by(numero_documento=data['datosVenta']["numero_documento"]).all()

        documentos_venta = list(map(lambda documento_venta: documento_venta.serialize(), documentos_venta))  # DEVUELVE
        # LISTA DE DICCIONARIOS CON MATCHES DE DOCUMENTOS DE VENTA

        for documento in documentos_venta:
            if documento['numero_documento'] == int(data['datosVenta']["numero_documento"]) and documento['tipo_documento'] == data['datosVenta']["tipo_documento"]:
                return jsonify({"msg": "Numero de Documento y Tipo de Documento ya se encuentra ingresado"}), 400       

        documento_venta = Documento_Venta()
        documento_venta.tipo_documento = data['datosVenta']["tipo_documento"]
        documento_venta.numero_documento = data['datosVenta']["numero_documento"]
        documento_venta.monto_neto = data['datosVenta']["monto_neto"]
        documento_venta.monto_iva = data['datosVenta']["monto_iva"]
        documento_venta.monto_total = data['datosVenta']["monto_total"]
        documento_venta.forma_pago = data['datosVenta']["forma_pago"]

        for detalle_producto in data['detalleProductos']:
            salida_inventario = Salida_Inventario()
            salida_inventario.cantidad = detalle_producto['cantidad']
            salida_inventario.precio_costo_unitario = 1  # FALTA INGRESAR COSTO UNITARIO REAL
            salida_inventario.precio_venta_unitario = detalle_producto['precio_venta_unitario'] / 1.19  # ELIMINAR DECIMALES?
            salida_inventario.costo_total = 1  # FALTA INGRESAR COSTO TOTAL REAL
            salida_inventario.venta_total = detalle_producto['total'] / 1.19  # ELIMINAR DECIMALES?
            salida_inventario.usuario_id = 1  # FALTA CAPTURAR USUARIO REAL
            salida_inventario.producto_id = detalle_producto['producto_id']

            documento_venta.salidas_I.append(salida_inventario)

        tipo_documento = data['datosVenta']["tipo_documento"]
        documento_venta.save()    
        return jsonify({"msg": f"{tipo_documento.capitalize()} creada exitosamente."}), 201


@app.route("/api/proveedores", methods=['GET', 'POST'])
@app.route("/api/proveedores/<int:id>", methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def proveedores(id=None):

    if request.method == 'GET':
        # DEVUELVE LISTADO CON TODOS LOS PROVEEDORES
        if not id:
            proveedores = Proveedor.query.all()
            if not proveedores:
                return jsonify({"msg": "No hay proveedores."})
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
        
        check_rut = Proveedor.query.filter_by(rut=rut).first()
        if check_rut:
            return jsonify({"msg": "Rut de empresa ya se encuentra registrado"}), 400
        check_razon_social = Proveedor.query.filter_by(razon_social=razon_social).first()
        if check_razon_social:
            return jsonify({"msg": "Razon social de empresa ya se encuentra registrado"}), 400

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

        check_rut = Proveedor.query.filter_by(rut=rut).first()
        if check_rut and check_rut.id != id:
            return jsonify({"msg": "Rut de empresa ya se encuentra registrado"}), 400

        check_razon_social = Proveedor.query.filter_by(razon_social=razon_social).first()
        if check_razon_social and check_razon_social.id != id:
            return jsonify({"msg": "Razon social de empresa ya se encuentra registrada"}), 400

        # check_razon_social = Proveedor.query.filter_by(razon_social = razon_social).first()
        # if check_razon_social and razon_social is not None:
        #    return jsonify({"msg":"Razon social de empresa ya se encuentra registrada"}), 400

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
                return jsonify({"msg": "Razon Social no puede estar vacía"}), 400
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
         
        return jsonify(proveedor.serialize()), 200

    # PERMITE ELIMINAR PROVEEDOR
    if request.method == 'DELETE':
        proveedor = Proveedor.query.get(id)
        if proveedor:
            proveedor.delete()
            return jsonify({"msg": f"Proveedor <{proveedor.nombre}> eliminado exitosamente."}), 200
        else:
            return jsonify({"msg": "Proveedor no se encuentra registrado."}), 400


@app.route('/api/categorias', methods=['GET', "POST"])
@app.route('/api/categorias/<int:id>', methods=["GET", "PUT", "DELETE"])
@jwt_required
def categorias(id=None):
    if request.method == 'GET':
        if not id:
            categorias = Categoria.query.all()
            if categorias:
                categorias = list(map(lambda categoria: categoria.serialize(), categorias))
                return jsonify(categorias), 200
            return jsonify({"msg": "Actualmente no hay categorías"}), 400
        categoria = Categoria.query.get(id)
        if id:
            categoria = Categoria.query.get(id)
            if categoria:
                return (categoria.serialize()), 200
            else:
                return jsonify({"msg": "Categoría no encontrada"}), 400
    
    if request.method == 'POST':
        nombre = request.json.get("nombre", None)
        if not nombre:
            return jsonify({"msg": "por favor ingresar nombre de categoría válido"})
        name_overlapped = Categoria.query.filter_by(nombre=nombre).first()
        if name_overlapped:
            return jsonify({"msg": "Categoría ya existe"})

        categoria = Categoria()
        categoria.nombre = nombre
        
        categoria.save()    
        return jsonify(categoria.serialize()), 200
    
    if request.method == 'PUT':
        
        nombre = request.json.get("nombre", None)
        
        if not nombre:
            return jsonify({"msg": "Categoría no puede estar vacío"}), 400
                    
        categoria_update = Categoria.query.get(id)
        if not categoria_update:
            return jsonify({"msg": "Categoría no se encuentra en el sistema"}), 400
        
        categoria_update.nombre = nombre
        categoria_update.update()
        
        return jsonify(categoria_update.serialize()), 200


@app.route("/api/cuadratura-caja", methods=['GET', 'POST'])
@app.route("/api/cuadratura-caja/<int:id>", methods=['GET'])
@jwt_required
def cuadratura_caja(id=None):

    if request.method == 'GET':
        if not id:
            cuadraturas_cajas = Cuadratura_Caja.query.all()
            cuadraturas_cajas = list(map(lambda cuadratura_caja: cuadratura_caja.serialize(), cuadraturas_cajas))
            return jsonify(cuadraturas_cajas), 200

        if id:
            cuadratura_caja = Cuadratura_Caja.query.get(id)
            if cuadratura_caja:
                return jsonify(cuadratura_caja.serialize()), 200
            else:
                return jsonify({"msg": "id asociado a cuadratura de caja no encontrada"}), 400

    if request.method == 'POST':
        data = request.get_json()
        if not data["usuario_id"]:
            return jsonify({"msg": "por favor ingresar user_id"}), 400
        
        if not data["admin_id"]:
            return jsonify({"msg": "por favor ingresar admin_id"}), 400
        
        if not data["fecha_apertura"]:
            return jsonify({"msg": "por favor ingresar fecha apertura"}), 400
        
        if not data["fecha_cierre"]:
            return jsonify({"msg": "por favor ingresar fecha de cierre"}), 400
        
        if not data["monto_apertura"]:
            return jsonify({"msg": "por favor ingresar monto de apertura"}), 400

        if not data["monto_transferencia"]:
            return jsonify({"msg": "por favor ingresar monto efectuado por transferencia"}), 400
        
        if not data["monto_efectivo"]:
            return jsonify({"msg": "por favor ingresar monto efectuado en efectivo"}), 400
        
        if not data["monto_tarjeta"]:
            return jsonify({"msg": "por favor ingresar monto efectuado por tarjeta"}), 400
        
        if not data["monto_cierre"]:
            return jsonify({"msg": "por favor ingresar monto de cierre"}), 400
        
        if not data["diferencia_en_caja"]:
            return jsonify({"msg": "por favor ingresar diferencia en caja"}), 400

        cuadratura_caja = Cuadratura_Caja()
        cuadratura_caja.usuario_id = data["usuario_id"]
        cuadratura_caja.admin_id = data["admin_id"]
        cuadratura_caja.fecha_apertura = datetime.strptime(data["fecha_apertura"], '%Y-%m-%d %H:%M:%S')
        cuadratura_caja.fecha_cierre = datetime.strptime(data["fecha_cierre"], '%Y-%m-%d %H:%M:%S')
        cuadratura_caja.monto_apertura = data["monto_apertura"]
        cuadratura_caja.monto_transferencia = data["monto_transferencia"]
        cuadratura_caja.monto_efectivo = data["monto_efectivo"]
        cuadratura_caja.monto_tarjeta = data["monto_tarjeta"]
        cuadratura_caja.monto_cierre = data["monto_cierre"]
        cuadratura_caja.diferencia_en_caja = data["diferencia_en_caja"]

        cuadratura_caja.save()
       
        return jsonify({"msg": "cuadratura de caja creada exitosamente"}), 201


@app.route('/api/stock', methods=['GET'])
@jwt_required
def stock():
    productos = Producto.query.all()
    productos = list(map(lambda producto: producto.serialize_stock(), productos))

    return jsonify(productos), 200


if __name__ == "__main__":
    manager.run()
