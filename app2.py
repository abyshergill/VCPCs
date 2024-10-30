import cv2
import os
import tkinter as tk
from tkinter import ttk
from threading import Thread, Event
import time
import subprocess
from PIL import Image, ImageTk
from datetime import datetime

class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Application")

        # Check for expiration date
        self.check_expiration()

        # Set the window size and prevent resizing
        self.root.geometry("645x580")
        self.root.resizable(False, False)

        # Create a folder for images if it doesn't exist
        self.folder_name = "Webcamimage"
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

        # Initialize webcam settings
        self.cap = None
        self.is_running = False
        self.capture_images_running = False
        self.capture_interval = 10  # Default capture interval
        self.stop_event = Event()  # Event to signal thread to stop

        # Webcam options
        self.webcam_list = self.get_webcam_list()
        self.selected_webcam = tk.StringVar(value=self.webcam_list[0])  # Default to the first webcam

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Frame for webcam selection
        webcam_frame = tk.Frame(self.root)
        webcam_frame.grid(row=0, column=0, padx=10, pady=10)

        # Dropdown for selecting webcam
        webcam_label = tk.Label(webcam_frame, text="Select Webcam:")
        webcam_label.grid(row=0, column=0, padx=10, pady=10)
        self.webcam_dropdown = ttk.Combobox(webcam_frame, textvariable=self.selected_webcam, values=self.webcam_list)
        self.webcam_dropdown.grid(row=0, column=1, padx=10, pady=10)

        # Frame for capture time selection
        capture_frame = tk.Frame(self.root)
        capture_frame.grid(row=0, column=1, padx=10, pady=10)

        # Dropdown for selecting capture interval
        capture_label = tk.Label(capture_frame, text="Capture Interval (seconds):")
        capture_label.grid(row=0, column=0, padx=10, pady=10)
        self.capture_time = tk.StringVar(value="10")  # Default value
        self.capture_time_dropdown = ttk.Combobox(capture_frame, textvariable=self.capture_time, values=["5", "10", "15", "20"])
        self.capture_time_dropdown.grid(row=0, column=1, padx=10, pady=10)

        # Start, Capture, Stop buttons
        self.start_button = tk.Button(self.root, text="Start", command=self.start_camera, width=10, height=2)
        self.start_button.grid(row=1, column=0, padx=100, pady=10, sticky='w')

        self.capture_button = tk.Button(self.root, text="Capture", command=self.start_capturing, width=10, height=2)
        self.capture_button.grid(row=1, column=1, padx=10, pady=10, sticky='w')

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_camera, width=10, height=2)
        self.stop_button.grid(row=1, column=1, padx=10, pady=10, sticky='e')

        # Canvas for video
        self.canvas = tk.Canvas(self.root, width=640, height=480)
        self.canvas.grid(row=2, column=0, columnspan=3)

        self.image_on_canvas = None

    def check_expiration(self):
        expiration_date = datetime(2025, 2, 23)
        if datetime.now() > expiration_date:
            tk.messagebox.showerror("Expiration", "This application has expired. I remember you, Aby Brother.")
            self.root.destroy()
            
    def get_webcam_list(self):
        # Check for available webcams
        webcams = []
        for i in range(5):  # Check the first 5 indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                webcams.append(f"Webcam {i}")
                cap.release()
            else:
                print(f"Webcam index {i} is not available.")
        return webcams


    def start_camera(self):
        if not self.is_running:
            webcam_index = self.webcam_list.index(self.selected_webcam.get())
            self.cap = cv2.VideoCapture(webcam_index)  # Use selected webcam
            
            # Set the desired video size (e.g., 640x480)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 420)

            if not self.cap.isOpened():
                tk.messagebox.showerror("Error", "Could not open the selected webcam.")
                return
            
            self.is_running = True
            self.stop_event.clear()  # Reset the stop event
            self.capture_thread = Thread(target=self.update_frame)
            self.capture_thread.start()

    def stop_camera(self):
        # Signal to stop capturing images if it's running
        self.stop_event.set()  # Signal the threads to stop

        # Set the running state to false and release the camera
        self.is_running = False
        if self.capture_thread is not None:
            self.capture_thread.join(timeout=1)  # Wait for a short time for the capture thread to finish

        if self.cap is not None:
            self.cap.release()  # Release the camera

        # Clear the canvas
        self.canvas.delete(self.image_on_canvas)

        # Re-enable buttons after stopping
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.capture_button.config(state=tk.DISABLED)

    def update_frame(self):
        while not self.stop_event.is_set():  # Check if the stop event is set
            if not self.is_running:
                break
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
            time.sleep(0.01)  # Small sleep to prevent high CPU usage

    def start_capturing(self):
        if self.is_running:  # Only allow capturing if the camera is running
            self.capture_images_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.capture_button.config(state=tk.DISABLED)

            # Get capture interval from the dropdown
            try:
                self.capture_interval = int(self.capture_time.get())
            except ValueError:
                tk.messagebox.showerror("Error", "Please enter a valid number for capture interval.")
                return

            self.capture_thread = Thread(target=self.capture_images)
            self.capture_thread.start()

    def capture_images(self):
        while self.capture_images_running and not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if ret:
                file_path = os.path.join(self.folder_name, f"image_{int(time.time())}.png")
                cv2.imwrite(file_path, frame)
                print(f"Captured {file_path}")
            time.sleep(self.capture_interval)  # Capture every specified interval

        # Re-enable buttons after stopping
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.capture_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamApp(root)
    root.mainloop()
