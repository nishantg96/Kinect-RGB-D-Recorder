import os
from common.tk_utils import AzureRecorder,pyk4a
from common.helpers import set_count
from pyk4a import FPS, Config, PyK4A, ImageFormat
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-c","--color",
                    required=True, help="Color of the bin to be recorded!")
parser.add_argument("-o","--output",
                    default="Processor/data/videos", help="Location to save video dataset!")
args = parser.parse_args()

out_path = os.path.join(os.path.normpath(args.output),args.color)

if os.path.isdir(out_path):
    print("Path exists - continuing....")
else:
    os.makedirs(out_path)
    print(f"Folder created for color - {args.color}")

count = set_count(out_path)

config = Config(color_resolution=pyk4a.ColorResolution.RES_720P, 
                depth_mode=pyk4a.DepthMode.WFOV_2X2BINNED,
                synchronized_images_only=True,
                color_format=ImageFormat.COLOR_MJPG,
                camera_fps= FPS.FPS_30,)

recorder = PyK4A(config=config)
recorder.start()

app = AzureRecorder(recorder, config, out_path, args.color,count)
app.root.mainloop()
