"""
[Done]- A new route to test different channel in the image based on the user request[Red,Green,Blue]
- Two things left to do: 
[Done]  - Dockerize this application [DockerFile]
[Pending]  - test with caMicroscope - Resources:https://github.com/camicroscope/caMicroscope/blob/c14569fe2d2fe18b51f0ce673ffed699b66477f6/core/CaMic.js#L204
"""

from flask import Flask, redirect,request, render_template, url_for
from flask import Response,send_file, session
import os
import scipy.io as sio
from PIL import Image
from io import BytesIO
import imageio
import model,HS2RGB
import base64
import pyvips
from uuid import uuid4

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
    #print(image_path)
    #print(type(image_path))
    if image_path.endswith(".mat"):
        band = sio.loadmat(image_path)
        arr = band['hsi']
        final_image = HS2RGB.intoRGB(arr)
    else:
        image = Image.open(image_path)
        final_image = model.RGB(image)
        
    converted_folder = 'converted'
    os.makedirs(converted_folder, exist_ok=True)
    dir,img_file = image_path.split("/")
    converted_image_path = os.path.join(converted_folder, img_file)
    imageio.imwrite(converted_image_path, final_image, format='TIFF')
    
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
    session['output_directory'] = output_directory
    return render_template('viewer.html', dzi_path=path)

@app.route('/gettile/<int:level>/<int:col>/<int:row>')
def get_tile(level, col, row):
    dzi_path = session.get('output_directory')
    #print(dzi_path)
    tile_path = f"{dzi_path}_files/{level}/{col}_{row}.jpeg"
    #print(tile_path)
    try:
        return send_file(tile_path, mimetype='image/jpeg')
    except FileNotFoundError:
        placeholder_image_path = "path_to_placeholder_image.jpg"
        return send_file(placeholder_image_path, mimetype='image/jpeg')

def user_channel_choice(channel):
    img_io = BytesIO()
    channel.save(img_io, format='JPEG')
    img_io.seek(0)
    return img_io

@app.route('/color/<filename>/<channel>')
def choose_color(filename,channel):
    image = Image.open(f"converted/{filename}")
    
    if channel == 'red':
        channel_image = image.split()[0]
    elif channel == 'green':
        channel_image = image.split()[1]
    elif channel == 'blue':
        channel_image = image.split()[2]
    else:
        return "Invalid channel"

    img_io = BytesIO()
    channel_image.save(img_io, format='JPEG')
    img_io.seek(0)
    return Response(img_io, mimetype='image/jpeg')
    
if __name__ == '__main__':
    app.run(debug=True)