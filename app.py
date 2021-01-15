from flask import Flask, request, jsonify, Response, send_from_directory, send_file
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import pymongo, os
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_cors import CORS

config = {
    "apiKey": "AIzaSyAAOx479AO6Pd82QmzJ5f5nAGVeIzex4ic",
    "authDomain": "cloud-imagenes.firebaseapp.com",
    "projectId": "cloud-imagenes",
    "storageBucket": "cloud-imagenes.appspot.com",
    "messagingSenderId": "65945789369",
    "appId": "1:65945789369:web:2c5f9109c89c9db9690c68",
    "measurementId": "G-ZSJ5LNV7NB"
}

UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER']  = UPLOAD_FOLDER
CORS(app)

url_mongo_atlas = "mongodb+srv://grafiti:12345@cluster0.qecwv.mongodb.net/examendb?retryWrites=true&w=majority"
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

@app.route('/usuarios', methods=['POST'])
def create_usuario():
    email = request.json['email']

    if email:
        id = mongo.db.usuarios.insert(
            {'email': email}
        )
        response = {
            'id': str(id),
            'email': email
        }
        return response
    else: 
        return not_found()

@app.route('/usuarios/findByEmail/<email>', methods=['GET'])
def get_usuario_byEmail(email):
    myquery = { "email": email }
    usuario = mongo.db.usuarios.find(myquery)
    response = json_util.dumps(usuario)
    return Response(response, mimetype='application/json')

@app.route('/usuarios/login/<email>/<nombre>/<token>', methods=['GET'])
def login(email, nombre, token):
    try:
        CLIENT_ID = '661567867815-mkf6bgra2bkv9qo93mleis627a39br64.apps.googleusercontent.com'
        id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

    except ValueError:
        error_response = jsonify({'Error': 'Error con el token'})
        return error_response

    myquery = { "email": email }
    usuario = mongo.db.usuarios.find_one(myquery)
    if not usuario:
        mongo.db.usuarios.insert(
            {'email': email}
        )
    else:
        response = json_util.dumps(usuario)
        return Response(response, mimetype='application/json')

    responsee = jsonify({'mensaje': 'Usuario nuevo añadido correctamente'})
    return responsee




########################  Imagen  ########################

@app.route('/imagenes', methods=['GET'])
def get_imagenes():
    imagenes = mongo.db.imagenes.find()
    response = json_util.dumps(imagenes)
    return Response(response, mimetype='application/json')

@app.route('/imagenes/<id>', methods=['GET'])
def get_imagen(id):
    imagen = mongo.db.imagenes.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(imagen)
    return Response(response, mimetype='application/json')

@app.route('/imagenes', methods=['POST'])
def create_imagen():
    email = request.json['email']
    likes = request.json['likes']
    descripcion = request.json['descripcion']
    nombre = request.json['nombre']

    if email:
        id = mongo.db.imagenes.insert(
            {'email': email, 'descripcion' : descripcion, 'likes' : likes, 'nombre' : nombre}
        )
        response = {
            'id': str(id),
            'email': email,
            'descripcion' : descripcion,
            'likes' : likes,
            'nombre' : nombre
        }
        return response
    else: 
        return not_found()

@app.route('/imagenes/<id>', methods=['DELETE'])
def delete_imagen(id):
    mongo.db.imagenes.delete_one({'_id': ObjectId(id)})
    response = {'mensaje': 'imagen eliminada correctamente'}
    return response

@app.route('/imagenes/<id>', methods=['PUT'])
def update_imagen(id):
    email = request.json['email']
    likes = request.json['likes']
    descripcion = request.json['descripcion']
    nombre = request.json['nombre']

    if descripcion and likes and email:
        mongo.db.imagenes.update_one({'_id': ObjectId(id)}, {'$set': {
            'email': email,
            'descripcion' : descripcion,
            'likes' : likes,
            'nombre' : nombre
        }})
        response = jsonify({'mensaje': 'Imagen actualizado correctamente'})
        return response
    else: 
        return not_found()

@app.route('/imagenes/filtrar/<filtro>', methods=['GET'])
def get_filtro(filtro):
    myquery = { "descripcion": { '$regex': ".*" + filtro + ".*" } }
    imagen = mongo.db.imagenes.find(myquery)
    response = json_util.dumps(imagen)
    return Response(response, mimetype='application/json')

@app.route('/imagenes/like/<id>', methods=['GET'])
def dar_like(id):
    imagen = mongo.db.imagenes.find_one({'_id': ObjectId(id)})
    numero_likes = int(imagen.likes)
    nuevo = numero_likes + 1
    mongo.db.imagenes.update_one({'_id': ObjectId(id)}, {'$set': {
            'email': imagen.email,
            'descripcion' : imagen.descripcion,
            'likes' : str(nuevo),
            'nombre' : imagen.nombre
    }})
    response = json_util.dumps(imagen)
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