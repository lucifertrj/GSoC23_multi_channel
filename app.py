"""
https://github.com/camicroscope/Distro/blob/0161da5ab6efeda81a9f8e634af1ec7e31b8cca5/config/routes.json#L39
https://github.com/camicroscope/Caracal/blob/master/handlers/iipHandler.js
https://github.com/camicroscope/Distro/blob/0161da5ab6efeda81a9f8e634af1ec7e31b8cca5/config/routes.json#L25

Upload image from the directory rather than request['files]

(this line) 

https://github.com/camicroscope/Distro/blob/b3f325f11bbd75f6111558012e0cb974e2758cbd/develop.yml#L11C15-L11C15

Run: http://localhost:4010/multichannel/

TODO:
[Done]- Make relative paths
- caMicroscope => apps:  (JavaScript)
        - User channel (multi-channel)
        - Viewer (multi-channel)
- API returns json - Read the channel order
"""

from flask import Flask, redirect,request, render_template, url_for, session, flash
#from flask import Response,send_file, 
import os
import scipy.io as sio
from PIL import Image
from io import BytesIO
#import imageio
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

@app.route('/')
def base():
    return "hello caMicroscope"

"""
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
            
            if image_path.endswith(".mat"):
                band = sio.loadmat(image_path)
                arr = band['hsi']
                num_channels = arr.shape[2]
            else:
                img_tif = Image.open(image_path)
                http://localhost:4010/multichannel/num_channels = len(img_tif.getbands())+2
            channel_labels = [f"Channel-{i}:" for i in range(num_channels)]  #send total channels as alphabets
            return render_template('channels.html', filename=image_file.filename, channels=channel_labels)

    return render_template('index.html')
"""

@app.route("/<filename>")
def main(filename):
    image_file = f"./{filename}"
        
    if image_file.split('.')[-1] not in ALLOWED_EXTENSIONS:
        flash("Invalid Image file")
    else:
        if image_file.endswith(".mat"):
            band = sio.loadmat(image_file)
            arr = band['hsi']
            num_channels = arr.shape[2]
        else:
            img_tif = Image.open(image_file)
            num_channels = len(img_tif.getbands())+2
        channel_labels = [f"Channel-{i}:" for i in range(num_channels)]  #send total channels as alphabets
        return render_template('channels.html', filename=image_file, channels=channel_labels)

@app.route('/process_channels', methods=['POST'])
def process_channels():
    filename = request.form['filename']
    num_channels = int(len(request.form) - 1)  # Subtract 1 for the filename field
    channel_order = [int(request.form[f'channel_{i}']) for i in range(num_channels)]
    
    return redirect(url_for('view_image', filename=filename, channel_order=channel_order))
    
@app.route('/api/rgb/<filename>', methods=['GET'])
def convert_channel_api(image_path,order):
    image_path = image_path
    #print(image_path)
    #print(type(image_path))
    if image_path.endswith(".mat"):
        band = sio.loadmat(image_path)
        arr = band['hsi']
        final_image = HS2RGB.intoRGB(arr)
    else:
        image = Image.open(image_path)
        final_image = model.RGB(image,order)
        
    """
    converted_folder = 'converted'
    os.makedirs(converted_folder, exist_ok=True)
    _,img_file = image_path.split("/")
    converted_image_path = os.path.join(converted_folder, img_file)
    imageio.imwrite(converted_image_path, final_image, format='TIFF')
    """
    
    image_data = BytesIO()
    final_image.save(image_data, format='JPEG')
    image_data.seek(0)
    return image_data.getvalue()

@app.route('/viewer/<filename>', methods=['GET'])
def view_image(filename):
    uid = uuid4().hex
    uploaded_path = filename
    channel_order = request.args.getlist('channel_order', type=int)
    
    #print(channel_order)
   
    converted_img = convert_channel_api(uploaded_path,channel_order)

    input_image = pyvips.Image.new_from_buffer(converted_img,"")
    output_directory = f"static/{uid}"
    input_image.dzsave(output_directory)
    path = f"{uid}.dzi"
    session['output_directory'] = output_directory
    return render_template('viewer.html', dzi_path=path)

if __name__ == '__main__':
    app.run(debug=True)

