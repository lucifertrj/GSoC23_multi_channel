from flask import Flask, redirect,request, render_template, url_for, Response
import os
import scipy.io as sio
from PIL import Image
from io import BytesIO
import model,HS2RGB
import base64
import pyvips
from uuid import uuid4

app = Flask(__name__)

def base64_encode(value):
    return base64.b64encode(value).decode('utf-8')

app.jinja_env.filters['b64encode'] = base64_encode

uploading_folder = "uploaded"
if not os.path.exists(uploading_folder):
    os.makedirs(uploading_folder)

app.config['TEMP_FOLDER'] = uploading_folder
app.config['SECRET_KEY'] = os.urandom(24)

ALLOWED_EXTENSIONS = set(['tif', 'tiff','png', 'jpg','mat'])

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return "No image uploaded", 400
        
        image_file = request.files['image']
        image_path = os.path.join(app.config['TEMP_FOLDER'], image_file.filename)
        
        image_file.save(image_path)
        return redirect(url_for('view_image', filename=image_file.filename))
    
    return render_template('index.html')

@app.route('/api/rgb/<filename>', methods=['GET'])
def convert_channel_api(image_path):
    image_path = image_path
    print(image_path)
    print(type(image_path))
    if image_path.endswith(".mat"):
        band = sio.loadmat(image_path)
        arr = band['hsi']
        final_image = HS2RGB.intoRGB(arr)
    else:
        image = Image.open(image_path)
        final_image = model.RGB(image)

    image_data = BytesIO()
    final_image.save(image_data, format='JPEG')
    image_data.seek(0)
    return image_data.getvalue()

@app.route('/viewer/<filename>', methods=['GET'])
def view_image(filename):
    uid = uuid4().hex
    uploaded_path = os.path.join("uploaded",filename)
    converted_img = convert_channel_api(uploaded_path)
    input_image = pyvips.Image.new_from_buffer(converted_img,"")
    output_directory = f"static/{uid}"
    input_image.dzsave(output_directory)
    path = f"{uid}.dzi"
    return render_template('viewer.html', dzi_path=path)


@app.route('/gettile')
def get_tile(filename, level, col, row):
    pass

if __name__ == '__main__':
    app.run(debug=True)
