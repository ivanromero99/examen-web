from flask import Flask, request, jsonify, Response, send_from_directory, send_file
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import pymongo, os

UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER']  = UPLOAD_FOLDER

#El usuario de Atlas se llama grafiti ya que es el mismo que usé en el proyecto
url_mongo_atlas = "mongodb+srv://grafiti:12345@cluster0.qecwv.mongodb.net/examen?retryWrites=true&w=majority"
client = pymongo.MongoClient(url_mongo_atlas)
mongo = client.get_database('examen')

########################  Usuario  ########################

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = mongo.db.usuarios.find()
    response = json_util.dumps(usuarios)
    return Response(response, mimetype='application/json')

@app.route('/usuarios/<id>', methods=['GET'])
def get_usuario(id):
    usuario = mongo.db.usuarios.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(usuario)
    return Response(response, mimetype='application/json')

@app.route('/usuarios/<id>', methods=['DELETE'])
def delete_usuario(id):
    mongo.db.usuarios.delete_one({'_id': ObjectId(id)})
    response = {'mensaje': 'Usuario eliminado correctamente'}
    return response

@app.route('/usuarios/<id>', methods=['PUT'])
def update_usuario(id):
    nombre = request.json['nombre']
    direccion = request.json['direccion']
    password = request.json['password']
    email = request.json['email']

    if nombre and direccion and password and email:
        mongo.db.usuarios.update_one({'_id': ObjectId(id)}, {'$set': {
            'nombre': nombre, 
            'email': email, 
            'password': password,
            'direccion': direccion
        }})
        response = jsonify({'mensaje': 'Usuario actualizado correctamente'})
        return response
    else: 
        return not_found()

@app.route('/usuarios', methods=['POST'])
def create_usuario():
    nombre = request.json['nombre']
    password = request.json['password']
    email = request.json['email']
    direccion = request.json['direccion']

    if nombre and password and email and direccion:
        id = mongo.db.usuarios.insert(
            {'nombre': nombre, 'email': email, "password": password, 'direccion': direccion}
        )
        response = {
            'id': str(id),
            'nombre': nombre,
            'email': email,
            'password': password,
            'direccion': direccion
        }
        return response
    else: 
        return not_found()

@app.route('/usuarios/findByNombre/<nombre>', methods=['GET'])
def get_usuario_byNombre(nombre):
    myquery = { "nombre": { '$regex': ".*" + nombre + ".*" } }
    usuario = mongo.db.usuarios.find(myquery)
    response = json_util.dumps(usuario)
    return Response(response, mimetype='application/json')

@app.route('/usuarios/findByEmail/<email>', methods=['GET'])
def get_usuario_byEmail(email):
    myquery = { "email": email }
    usuario = mongo.db.usuarios.find(myquery)
    response = json_util.dumps(usuario)
    return Response(response, mimetype='application/json')

@app.route('/usuarios/login/<email>/<nombre>', methods=['GET'])
def login(email, nombre):
    myquery = { "email": email }
    usuario = mongo.db.usuarios.find_one(myquery)
    if not usuario:
        mongo.db.usuarios.insert(
            {'nombre': nombre, 'email': email, 'password': 'Desconocida', 'direccion': 'Desconocida'}
        )
    else:
        response = json_util.dumps(usuario)
        return Response(response, mimetype='application/json')

    responsee = jsonify({'mensaje': 'Usuario nuevo añadido correctamente'})
    return responsee



########################  Comentario  ########################

@app.route('/comentarios', methods=['GET'])
def get_comentarios():
    comentarios = mongo.db.comentarios.find()
    response = json_util.dumps(comentarios)
    return Response(response, mimetype='application/json')

@app.route('/comentarios/<id>', methods=['GET'])
def get_comentario(id):
    comentario = mongo.db.comentarios.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(comentario)
    return Response(response, mimetype='application/json')

@app.route('/comentarios/<id>', methods=['DELETE'])
def delete_comentario(id):
    mongo.db.comentarios.delete_one({'_id': ObjectId(id)})
    response = {'mensaje': 'Comentario eliminado correctamente'}
    return response

@app.route('/comentarios/<id>', methods=['PUT'])
def update_comentario(id):
    contenido = request.json['contenido']
    usuario_nombre = request.json['usuario_nombre']
    grafiti_id = request.json['grafiti_id']

    if contenido and usuario_nombre and grafiti_id:
        mongo.db.comentarios.update_one({'_id': ObjectId(id)}, {'$set': {
            'contenido': contenido, 
            'usuario_nombre': usuario_nombre,
            'grafiti_id': grafiti_id
        }})
        response = jsonify({'mensaje': 'comentario actualizado correctamente'})
        return response
    else: 
        return not_found()

@app.route('/comentarios', methods=['POST'])
def create_comentario():
    contenido = request.json['contenido']
    usuario_nombre = request.json['usuario_nombre']
    grafiti_id = request.json['grafiti_id']

    if contenido and usuario_nombre and grafiti_id:
        id = mongo.db.comentarios.insert(
            {'contenido': contenido, 'usuario_nombre': usuario_nombre, "grafiti_id": grafiti_id}
        )
        response = {
            'id': str(id),
            'contenido': contenido,
            'usuario_nombre': usuario_nombre,
            'grafiti_id': grafiti_id
        }
        return response
    else: 
        return not_found()

@app.route('/comentarios/findByGrafiti/<id>', methods=['GET'])
def get_comentario_byGrafiti(id):
    myquery = { "grafiti_id": id }
    comentario = mongo.db.comentarios.find(myquery)
    response = json_util.dumps(comentario)
    return Response(response, mimetype='application/json')



########################  Media  ########################

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/media', methods=['POST'])
def guardar_imagen():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        response = jsonify({'foto': filename})
        return response
    return not_found()

@app.route('/media/<filename>', methods=['GET'])
def devolver_imagen(filename):
    return send_file(filename, as_attachment=True)




@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'mensaje': 'Recurso no encontrado',
        'estado': 404
    })
    response.status_code = 404
    return response

if __name__ == "__main__":
    app.run(debug=True)
