from turtle import bgcolor
from flask import Flask, json, request, jsonify
import os
import urllib.request
from werkzeug.utils import secure_filename
import uuid
from pymongo import MongoClient
from rembg import remove
from PIL import Image

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.remove_bg
input_img_col = db.input_image_collection
output_img_col = db.output_image_collection

app.secret_key = "makaloteliborrypuciparatulakingpooka"

UPLOAD_FOLDER = 'static/uploads/input'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg'])

# function allow file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def main():
    return 'Homepage'

@app.route('/v1/remove-bg', methods=['POST'])
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
            output_path = 'static/uploads/output/'+filename+'.png'
            process_remove_bg = Image.open('static/uploads/input/'+get_image)
            output = remove(process_remove_bg)
            output.save(output_path)
            # post to output_image_collection
            output_img_col.insert_one({'image_name': filename})
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
    if success:
        resp = jsonify({'message' : 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp

if __name__ == '__main__':
    app.run(debug=True)