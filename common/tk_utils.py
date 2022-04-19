import cv2
import pyk4a
import threading
from time import time
import tkinter as tki
from PIL import Image,ImageTk
from playsound import playsound
from pyk4a import PyK4ARecord,ImageFormat
from common.helpers import convert_to_bgra_if_required,colorize

class AzureRecorder():
	
	def __init__(self,capture,config,output,color,count):
		
		self.flag_record = False
		# ========================================================================================================
		self.cap = capture
		self.config = config
		self.color = color
		self.count = count
		self.outpath = output
		self.record = None
		self.rgb = None
		self.depth = None
		self.frame = None
		self.thread = None
		self.stop_event = None
		self.start = None
		self.root = tki.Tk()
		self.rgb_panel = None
		self.depth_panel = None

		btn = tki.Button(self.root, text="Start recording",command=self.start_callback)
		btn.pack(side="bottom",fill="both",expand="yes",padx=10,pady=10)

		stop_btn = tki.Button(self.root, text="Stop recording",command=self.stop_callback)
		stop_btn.pack(side="bottom",fill="both",expand="yes",padx=10,pady=10)
		# ========================================================================================================
		
		self.stop_event = threading.Event()
		self.thread = threading.Thread(target=self.run,args=())
		self.thread.start()
		
		self.root.wm_title("Azure Kinect Recorder")
		self.root.wm_protocol("WM_DELETE_WINDOW",self.on_close)
		
		if not pyk4a.connected_device_count():
			raise RuntimeError('Failed to connect to sensor')
	
	def start_callback(self):
		print("Started recording")
		try:
			playsound("Processor/common/audio/start.mp3")
			self.record = PyK4ARecord(device=self.cap, config=self.config, path=(self.outpath+ f"/{self.color}_{self.count}.mkv"))
			self.flag_record = True
			self.record.create()
			self.start = time()

		except (RuntimeError, TypeError, NameError) as e:
			print("Can't start recording! :",e)
	
	def stop_callback(self):
		playsound("Processor/common/audio/stop.mp3")
		print("stop recording")
		self.flag_record = False
		self.record.flush()
		self.record.close()
		print(f"{self.record.captures_count} frames written.")
		self.count += 1
	
	def run(self):
		try:
			while not self.stop_event.is_set():
				self.frame = self.cap.get_capture()
				self.rgb = convert_to_bgra_if_required(ImageFormat.COLOR_MJPG,self.frame.color)[:,:,:3]
				self.depth = self.frame.transformed_depth

				#===================================================================================
				#						Not so elegant way to do this! 							   #
				#===================================================================================
				rgb_image = cv2.cvtColor(self.rgb, cv2.COLOR_BGR2RGB)
				rgb_image = Image.fromarray(rgb_image)
				rgb_image = ImageTk.PhotoImage(rgb_image)

				depth_image = colorize(self.depth, (300, 1100))
				depth_image = Image.fromarray(depth_image)
				depth_image = ImageTk.PhotoImage(depth_image)

				if (self.rgb_panel or self.depth_panel) is None :
					self.rgb_panel = tki.Label(image=rgb_image)
					self.rgb_panel.image = rgb_image
					self.rgb_panel.pack(side="left", padx=10, pady=10)

					self.depth_panel = tki.Label(image=depth_image)
					self.depth_panel.image = depth_image
					self.depth_panel.pack(side="right", padx=10, pady=10)
					
				else:
					self.rgb_panel.configure(image=rgb_image)
					self.rgb_panel.image = rgb_image

					self.depth_panel.configure(image=depth_image)
					self.depth_panel.image = depth_image
				#=========================================================================================

				if self.flag_record:
					self.record.write_capture(self.frame)
					if time()-self.start >= 2.5:
						self.stop_callback()

		except RuntimeError as e:
			print("Runtime error: ",e)
		
	def on_close(self):
		print("closing")
		self.stop_event.set()
		self.cap.stop()
		self.root.destroy()
		self.root.quit()