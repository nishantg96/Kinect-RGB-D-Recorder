import re,os
import cv2
import numpy as np
import pandas
import pandas as pd
from pyk4a import ImageFormat
from typing import Optional, Tuple

def convert_to_bgra_if_required(color_format: ImageFormat, color_image):
    # examples for all possible pyk4a.ColorFormats
    if color_format == ImageFormat.COLOR_MJPG:
        color_image = cv2.imdecode(color_image, cv2.IMREAD_COLOR)
    elif color_format == ImageFormat.COLOR_NV12:
        color_image = cv2.cvtColor(color_image, cv2.COLOR_YUV2BGRA_NV12)
        # this also works and it explains how the COLOR_NV12 color color_format is stored in memory
        # h, w = color_image.shape[0:2]
        # h = h // 3 * 2
        # luminance = color_image[:h]
        # chroma = color_image[h:, :w//2]
        # color_image = cv2.cvtColorTwoPlane(luminance, chroma, cv2.COLOR_YUV2BGRA_NV12)
    elif color_format == ImageFormat.COLOR_YUY2:
        color_image = cv2.cvtColor(color_image, cv2.COLOR_YUV2BGRA_YUY2)
    return color_image


def colorize(
    image: np.ndarray,
    clipping_range: Tuple[Optional[int], Optional[int]] = (None, None),
    colormap: int = cv2.COLORMAP_JET,
) -> np.ndarray:
    if clipping_range[0] or clipping_range[1]:
        img = image.clip(clipping_range[0], clipping_range[1])
    else:
        img = image.copy()
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    img = cv2.applyColorMap(img, colormap)
    return img

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def set_count(savepath):
    last_file = os.listdir(savepath)
    last_file.sort(key=natural_keys)

    if len(last_file) == 0:
        count = 1
    else:
        pattern = "^[^_]+_([^.]+)"
        file = last_file[-1]
        count = int(re.search(pattern,file).group(1)) + 1
    
    return count

def interpolated_DF_to_list(data):
    data = pd.DataFrame(data)
    data_new = data.iloc[:, 1:6]
    data_new = data_new.interpolate(method='values', limit_direction='both')
    data.update(data_new)
    data.reset_index(inplace=True)
    
    return data.to_numpy().tolist()