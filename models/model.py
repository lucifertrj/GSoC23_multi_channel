from PIL import Image
import numpy as np

def assign_red_channel(original_image):
    original_image = original_image.convert('L')
    first_array = np.array(original_image)
    red_ch = np.zeros((first_array.shape[0], first_array.shape[1], 3), dtype=np.uint8)
    red_ch[:, :, 0] = first_array
    return red_ch

def assign_green_channel(original_image):
    original_image = original_image.convert('L')
    second_array = np.array(original_image)
    green_ch = np.zeros((second_array.shape[0], second_array.shape[1], 3), dtype=np.uint8)
    green_ch[:, :, 1] = second_array
    return green_ch

def assign_blue_channel(original_image):
    original_image = original_image.convert('L')
    third_array = np.array(original_image)
    blue_ch = np.zeros((third_array.shape[0], third_array.shape[1], 3), dtype=np.uint8)
    blue_ch[:, :, 2] = third_array
    return blue_ch

def RGB(image):
    image.seek(0)
    red_ch = assign_red_channel(image)
    image.seek(1)
    green_ch = assign_green_channel(image)
    image.seek(2)
    blue_ch = assign_blue_channel(image)
    final_image = np.empty((1020, 954, 3), dtype=np.uint8)
    final_image[:, :, 0] = red_ch[:, :, 0]
    final_image[:, :, 1] = green_ch[:, :, 1]
    final_image[:, :, 2] = blue_ch[:, :, 2]
    
    rgbImg = Image.fromarray(final_image)
    return rgbImg