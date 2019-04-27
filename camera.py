import cv2
import time
from spotiface import Spotiface
from threading import Thread

cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
anterior = 0


class VideoCamera(object):
    def __init__(self, device_id, access_token):
        self.video = cv2.VideoCapture(0)
        self.anterior = 0
        self.device_id = device_id
        self.access_token = access_token
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if int(time.perf_counter()) % 10 == 0:
                img_name = "current_face.png"
                cv2.imwrite(img_name, image)
                data = open('current_face.png', 'rb')
                Thread(Spotiface().spotiface(self.access_token, self.device_id, data)).start()

        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

