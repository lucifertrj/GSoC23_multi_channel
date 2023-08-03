from sklearn.decomposition import PCA

import numpy as np
from PIL import Image

import warnings
warnings.filterwarnings('ignore')

def intoRGB(image):
    reshaped_image = image.reshape(image.shape[0]*image.shape[1], image.shape[2])
    norm = (reshaped_image - np.mean(reshaped_image, axis=0)) / np.std(reshaped_image, axis=0)
    pca = PCA(n_components=3)
    pca.fit(norm)
    rgb = pca.components_
    rgb_arr = np.dot(norm, rgb.T)
    rgb_arr = rgb_arr.reshape(image.shape[0], image.shape[1], 3)
    arr = rgb_arr.astype(np.uint8)
    rgb_image = Image.fromarray(arr)
    return rgb_image