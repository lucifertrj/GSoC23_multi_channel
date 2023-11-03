from flask import Flask, render_template, request, redirect, url_for, send_file
from PIL import Image
import numpy as np
from scipy.io import loadmat
from io import BytesIO
from flask_caching import Cache
import pyvips

app = Flask(__name__)

cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'}) 

def load_hsi_from_mat(file_name):
    mat_data = loadmat(f'static/mat_files/{file_name}.mat')
    return mat_data['hsi']

def hsi_to_rgb(hsi_image, band_selections):
    rgb_image = np.zeros((hsi_image.shape[0], hsi_image.shape[1], 3), dtype=np.float32)

    for selection in band_selections:
        band_index = selection['band']
        color = selection['color']
        
        if color == 'R':
            rgb_image[:,:,0] += hsi_image[:,:,band_index]
        elif color == 'G':
            rgb_image[:,:,1] += hsi_image[:,:,band_index]
        elif color == 'B':
            rgb_image[:,:,2] += hsi_image[:,:,band_index]
    
    for i in range(3):
        channel = rgb_image[:,:,i]
        channel = (channel - np.min(channel)) / (np.max(channel) - np.min(channel)) * 255
        rgb_image[:,:,i] = channel

    return rgb_image.astype(np.uint8)

@app.route('/')
def index():
    sample_files = ['hsi1', 'hsi2', 'hsi3', 'hsi4']
    return render_template('index.html', sample_files=sample_files)

rgb_images = {}

@app.route('/select_bands/<file_name>', methods=['GET', 'POST'])
def select_bands(file_name):
    hsi_image = load_hsi_from_mat(file_name)
    num_bands = hsi_image.shape[2]

    if request.method == 'POST':
        band_selections = []
        for i in range(num_bands):
            color_choice = request.form.get(f'band_{i}', None)
            if color_choice:
                band_selections.append({'band': i, 'color': color_choice})
        rgb_image = hsi_to_rgb(hsi_image, band_selections)
        
        rgb_images[file_name] = rgb_image
        
        return redirect(url_for('view_image', file_name=file_name))
    return render_template('select_bands.html', file_name=file_name, num_bands=num_bands)

@app.route('/view_image/<file_name>', methods=['GET'])
def view_image(file_name):
    if file_name not in rgb_images:
        return "Image not found", 404

    img = Image.fromarray(rgb_images[file_name])
    vips_image = pyvips.Image.new_from_array(np.array(img), 1.0)

    output_directory = f"static/{file_name}"
    """
    vips_image.dzsave(output_directory)
    
    dzi_path = f"{output_directory}.dzi"
    print(dzi_path)
    """
    dzi_path = None
    print(dir())
    return render_template('view.html', dzi_path=dzi_path)


if __name__ == '__main__':
    app.run(debug=True)
