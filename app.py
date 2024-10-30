import cv2
import os
import tkinter as tk
from tkinter import messagebox
from threading import Thread
import time
from PIL import Image, ImageTk

class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Application")
        
        # Create a folder for images if it doesn't exist
        self.folder_name = "Webcamimage"
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

        # Initialize webcam
        self.cap = cv2.VideoCapture(0)  # Change to 1 or 2 if using a different USB camera
        self.is_running = False
        self.capture_thread = None
        
        # Button size
        button_width = 10
        button_height = 2

        # Create GUI elements using grid layout
        self.start_button = tk.Button(root, text="Start", command=self.start_camera, width=button_width, height=button_height)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.capture_button = tk.Button(root, text="Capture", command=self.capture_images, width=button_width, height=button_height)
        self.capture_button.grid(row=0, column=1, padx=10, pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_camera, width=button_width, height=button_height)
        self.stop_button.grid(row=0, column=2, padx=10, pady=10)

        self.canvas = tk.Canvas(root, width=640, height=480)
        self.canvas.grid(row=1, column=0, columnspan=3)

        self.image_on_canvas = None
        
    def start_camera(self):
        if not self.is_running:
            self.is_running = True
            self.capture_thread = Thread(target=self.update_frame)
            self.capture_thread.start()

    def stop_camera(self):
        self.is_running = False
        if self.capture_thread is not None:
            self.capture_thread.join()
        self.cap.release()
        self.canvas.delete(self.image_on_canvas)

    def update_frame(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert the image to PIL format
                img = Image.fromarray(frame)
                # Convert the image to PhotoImage format
                self.photo = ImageTk.PhotoImage(image=img)
                if self.image_on_canvas is not None:
                    self.canvas.delete(self.image_on_canvas)
                self.image_on_canvas = self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            time.sleep(0.01)

'''
    def capture_images(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.capture_button.config(state=tk.DISABLED)
        for i in range(5):  # Change 5 to any number of captures
            ret, frame = self.cap.read()
            if ret:
                file_path = os.path.join(self.folder_name, f"image_{int(time.time())}.png")
                cv2.imwrite(file_path, frame)
                print(f"Captured {file_path}")
            time.sleep(10)  # Capture every 10 seconds
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.capture_button.config(state=tk.NORMAL)
'''

if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamApp(root)
    root.mainloop()
