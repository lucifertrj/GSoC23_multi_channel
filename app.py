from flask import Flask, redirect,request, render_template, url_for, session, flash, jsonify,make_response
import os
import scipy.io as sio
from PIL import Image
from flask_caching import Cache
from io import BytesIO
import model,HS2RGB
import base64
import pyvips
from uuid import uuid4

app = Flask(__name__)
app.secret_key = os.urandom(24)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def base64_encode(value):
    return base64.b64encode(value).decode('utf-8')

app.jinja_env.filters['b64encode'] = base64_encode

uploading_folder = "uploaded"
if not os.path.exists(uploading_folder):
    os.makedirs(uploading_folder)

app.config['TEMP_FOLDER'] = uploading_folder
app.config['SECRET_KEY'] = os.urandom(24)

ALLOWED_EXTENSIONS = set(['tif', 'tiff','png','jpeg','jpg','mat'])

sample_image = ['44153.tif','hsi_1.mat','23049.tif','10974.tif']

@app.route('/')
def base():
    return render_template('home.html', image_filenames=sample_image) 

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
        
        #return jsonify({"filename": image_file, "channels": channel_labels})
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
    
    cache_key = f'{uploaded_path}_{channel_order}'
    converted_img = cache.get(cache_key)

    if converted_img is None:
        converted_img = convert_channel_api(uploaded_path, channel_order)
        cache.set(cache_key, converted_img)

    input_image = pyvips.Image.new_from_buffer(converted_img, "")
    
    output_directory = f"static/{uid}"
    input_image.dzsave(output_directory)
    
    path = f"{uid}.dzi"
    session['output_directory'] = output_directory
    return render_template('viewer.html', dzi_path=path)
   
    """
    converted_img = convert_channel_api(uploaded_path,channel_order)
    input_image = pyvips.Image.new_from_buffer(converted_img,"")
    
    output_directory = f"static/{uid}"
    input_image.dzsave(output_directory)
    
    path = f"{uid}.dzi"
    session['output_directory'] = output_directory
    return render_template('viewer.html', dzi_path=path)

    
    dzi_data = input_image.dzsave_buffer(basename=".dzi")
    print(dzi_data)
    response = make_response(dzi_data)
    response.headers['Content-Type'] = 'application/xml'
    response.headers['Content-Dispo'] = f'attachment; filename={uid}.dzi'

    return response
    """

if __name__ == '__main__':
    app.run(debug=True,port=8000)