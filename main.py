#main
import VM as VM
import cv2
from picamera import PiCamera
import time

camera = PiCamera()
alarma=VM.alarmas()
bordes=VM.iniciar(camera,alarma)
img=VM.recorte(camera,bordes)
cv2.imwrite("works.jpg",img)


cv2.imshow("Game Boy Screen", img)
cv2.waitKey(0)