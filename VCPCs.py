import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QGridLayout, QWidget, QLabel,
                             QPushButton, QComboBox, QFileDialog,
                             QSpacerItem, QSizePolicy, QMessageBox, QSlider)
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import QThread, pyqtSignal, Qt

class VideoCaptureThread(QThread):
    frameCaptured = pyqtSignal(np.ndarray)

    def __init__(self, webcam_index):
        super().__init__()
        self.webcam_index = webcam_index
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(self.webcam_index)
        while self.running:
            ret, frame = cap.read()
            if ret:
                self.frameCaptured.emit(frame)
        cap.release()

    def stop(self):
        self.running = False
        self.wait()

class WebcamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Free Picture Capture Script by ABY at https://github.com/abyshergill/VCPCs")

        self.layout = QGridLayout()

        title_font = QFont("Arial", 16)
        button_font = QFont("Arial", 12)

        # Webcam Label
        self.webcam_label = QLabel("Select Webcam:")
        self.webcam_label.setFont(title_font)
        self.layout.addWidget(self.webcam_label, 0, 0)

        # Webcam Combo Box
        self.webcam_combo = QComboBox()
        self.webcam_combo.setFixedSize(200, 30)
        self.layout.addWidget(self.webcam_combo, 0, 1)


        # Create buttons
        self.start_button = QPushButton("Start")
        self.start_button.setFont(button_font)
        self.start_button.setFixedSize(200, 50)
        self.start_button.clicked.connect(self.start_camera)
        self.layout.addWidget(self.start_button, 1, 0)

        self.capture_button = QPushButton("Capture")
        self.capture_button.setFont(button_font)
        self.capture_button.setFixedSize(200, 50)
        self.capture_button.clicked.connect(self.capture_image)
        self.layout.addWidget(self.capture_button, 1, 1)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setFont(button_font)
        self.stop_button.setFixedSize(200, 50)
        self.stop_button.clicked.connect(self.stop_camera)
        self.layout.addWidget(self.stop_button, 1, 2)
         
        
        # Video Label
        self.video_label = QLabel()
        self.layout.addWidget(self.video_label, 2, 0, 1, 3)  
        
        self.setLayout(self.layout)

        self.capture_thread = None
        self.last_frame = None
        self.populate_webcam_list()

    def populate_webcam_list(self):
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.webcam_combo.addItem(f"Webcam {i}")
                cap.release()

    def start_camera(self):
        self.showMaximized()
        self.start_button.setEnabled(False)
        self.capture_button.setEnabled(True)
        self.stop_button.setEnabled(True)

        if self.capture_thread is None:
            webcam_index = self.webcam_combo.currentIndex()
            self.capture_thread = VideoCaptureThread(webcam_index)
            self.capture_thread.frameCaptured.connect(self.update_frame)
            self.capture_thread.start()
    
    def update_frame(self, frame, width=1890, height=850):
        self.last_frame = frame  
        frame = cv2.resize(frame, (width, height))  
        
        # Convert the frame from BGR (OpenCV format) to RGB (Qt format)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        h, w, ch = frame.shape  
        bytes_per_line = ch * w  
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
       
        self.video_label.setPixmap(QPixmap.fromImage(q_img))

    def capture_image(self):
        self.capture_thread.stop()
        if self.last_frame is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.jpg *.jpeg)")
            if file_path:
                cv2.imwrite(file_path, self.last_frame)
                QMessageBox.information(self, "Success", "Image saved successfully!")
        else:
            QMessageBox.warning(self, "Error", "No frame to capture.")

    def stop_camera(self):
        #self.showNormal()
        self.start_button.setEnabled(True)
        self.capture_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        if self.capture_thread is not None:
            self.capture_thread.stop()
            self.capture_thread = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    webcam_app = WebcamApp()
    webcam_app.show()
    sys.exit(app.exec_())
