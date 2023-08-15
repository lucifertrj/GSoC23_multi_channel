"""
https://github.com/camicroscope/Distro/blob/0161da5ab6efeda81a9f8e634af1ec7e31b8cca5/config/routes.json#L39
https://github.com/camicroscope/Caracal/blob/master/handlers/iipHandler.js
https://github.com/camicroscope/Distro/blob/0161da5ab6efeda81a9f8e634af1ec7e31b8cca5/config/routes.json#L25
"""

from flask import Flask, redirect,request, render_template, url_for
from flask import Response,send_file, session, flash
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

ALLOWED_EXTENSIONS = set(['tif', 'tiff','png','jpeg','jpg','mat'])

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return "No image uploaded", 400
        
        image_file = request.files['image']
        
        if image_file.filename.split('.')[-1] not in ALLOWED_EXTENSIONS:
            flash("Invalid Image file")
        else:
            image_path = os.path.join(app.config['TEMP_FOLDER'], image_file.filename)
            image_file.save(image_path)
            
            img = Image.open(image_path)
            
            num_channels = len(img.getbands())
            channel_labels = [chr(65 + i) for i in range(num_channels)] 
            
            return render_template('channels.html', filename=image_file.filename, channels=channel_labels)

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
    _,img_file = image_path.split("/")
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
    
"""
input has [A,B,C,D,E,F], and output is [R,G,B]; can we let a user choose A->R, F->G, C->B and display that as output?
to avoid duplicate B
input has [1,2,3,4,5,6], and output is [R,G,B]; can we let a user choose 1->R, 6->G, 3->B and display that as output?
"""