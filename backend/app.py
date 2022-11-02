from turtle import bgcolor
from flask import Flask, json, request, jsonify
import os
import io
from base64 import encodebytes
import urllib.request
from werkzeug.utils import secure_filename
import uuid
from pymongo import MongoClient
from rembg import remove
from PIL import Image
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

client = MongoClient('mongodb+srv://remove-bg:remove-bg@cluster0.8s45xvs.mongodb.net/?retryWrites=true&w=majority')
db = client.remove_bg
input_img_col = db.input_image_collection
output_img_col = db.output_image_collection

app.secret_key = "makaloteliborrypuciparatulakingpooka"

UPLOAD_FOLDER = 'static/uploads/input'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg', 'jfif'])

# function allow file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r') # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG') # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64
    return encoded_img

@app.route('/')
def main():
    return '<h1>Fantastic Apps Fauzi!</h1>'

@app.route('/v1/remove-bg', methods=['POST'])
@cross_origin()
def upload_file():
    # check if the post request has the file part
    if 'files[]' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files[]')

    errors = {}
    success = False

    for file in files:
        if file and allowed_file(file.filename):
            filename_generate = str(uuid.uuid4())
            filename = secure_filename(filename_generate+file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # post to input_image_collection
            input_img_col.insert_one({'image_name': filename})
            # get filename
            get_image = input_img_col.find_one({'image_name': filename})
            get_image = get_image['image_name']
            # process image
            new_get_image = get_image[0:-4]
            output_path = 'static/uploads/output/'+new_get_image+'.png'
            process_remove_bg = Image.open('static/uploads/input/'+get_image)
            output = remove(process_remove_bg)
            output.save(output_path)
            # post to output_image_collection
            # response image
            encode_path = 'static/uploads/output/'+new_get_image+'.png'
            encoded_img = get_response_image(encode_path)
            output_img_col.insert_one({'image_name': new_get_image, 'image_bytes': encoded_img})
            # get_image_bytes = output_img_col.find_one({'image_bytes': encoded_img})
            # image_bytes = get_image_bytes['image_bytes']
            # print(image_bytes)
            success = True
            if success:
                resp = jsonify({'message' : 'Files successfully uploaded','image_name': new_get_image,'ImageBytes': encoded_img.replace('\n','')})
                resp.status_code = 201
                return resp
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp

if __name__ == '__main__':
    port = int(os.environ.get('PORT',5001))
    app.run(host="0.0.0.0", port=port,debug=True)