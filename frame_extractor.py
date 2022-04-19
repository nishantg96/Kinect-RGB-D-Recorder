
from argparse import ArgumentParser
from tkinter import Image

import cv2
import numpy as np
import os
from tqdm import tqdm
from common.helpers import colorize, convert_to_bgra_if_required, natural_keys
from pyk4a import PyK4APlayback
from PIL import Image,ImageEnhance

def info(playback: PyK4APlayback):
    print(f"Record length: {playback.length / 1000000: 0.2f} sec")

def play(playback: PyK4APlayback,out_path,color):
    count = 0

    color_path = (os.path.join(out_path,"color"))
    depth_path = (os.path.join(out_path,"depth"))

    if not os.path.exists(color_path):
                os.makedirs(color_path)
    if not os.path.exists(depth_path):
                os.makedirs(depth_path)

    while True:
        try:
            capture = playback.get_next_capture()
            # capture = playback.get_next_capture()
            if capture.color is not None:
                # cv2.imshow("Color", convert_to_bgra_if_required(playback.configuration["color_format"], capture.color))
                cv2.imwrite(f"{color_path}/{color}_{count}.png",convert_to_bgra_if_required(playback.configuration["color_format"], capture.color))
            if capture.depth is not None:
                # cv2.imshow("Depth", colorize(capture.transformed_depth, (300, 1200)))
                np.save(f"{depth_path}/{color}_{count}",capture.transformed_depth)
                count += 1

        except EOFError:
            break
    cv2.destroyAllWindows()


def main() -> None:
    parser = ArgumentParser(description="pyk4a player")
    parser.add_argument("FOLDER", type=str, help="Path to MKV files")
    args = parser.parse_args()

    source: str = os.path.normpath(args.FOLDER)
    assert(os.path.isdir(source))

    output = "data/frames" #Change to Argparse
    
    folders = os.listdir(source)
    for folder in tqdm(folders , colour="white", desc='Total progress.'):
        folder_path = os.path.join(source,folder)
        files = os.listdir(folder_path)
        files.sort(key=natural_keys)

        for file in tqdm(files , colour=str(folder) , desc="Files in folder: {}".format(folder) , leave=False):
            name = file.split('.')[0]
            ext = file.split('.')[1]

            input_file = os.path.join(folder_path,file)
            out_path = os.path.join(output,name.split("_")[0],name)
            
            if not os.path.exists(out_path):
                os.makedirs(out_path)

            playback = PyK4APlayback(input_file)
            playback.open()
            play(playback,out_path,str(folder))
            playback.close()

if __name__ == "__main__":
    main()
