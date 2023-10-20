import numpy as np
from PIL import Image

import warnings
warnings.filterwarnings('ignore')

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
    
    # Normalize each channel to be in the range [0, 255]
    for i in range(3):
        channel = rgb_image[:,:,i]
        channel = (channel - np.min(channel)) / (np.max(channel) - np.min(channel)) * 255
        rgb_image[:,:,i] = channel
    
    arr = rgb_image.astype(np.uint8)
    rgb_image = Image.fromarray(arr)
    
    return rgb_image