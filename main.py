#main
import VM as VM
import OTA as OTA
import cv2
from picamera import PiCamera
import time
import os
import sys
Version=2.0
alarma=VM.alarmas()


x=OTA.get_V()
print(x)
if(Version!=OTA.get_V()):
    print("actualizado")
    os.execl(sys.executable, sys.executable, *sys.argv)

else:
    print("Version correcta")
camera = PiCamera()
bordes=VM.iniciar(camera,alarma)
T=time.time()

while time.time()-T<10:
    img=VM.recorte(camera,bordes)
    zonas=VM.zonas(img)
    grafico=VM.graficos(zonas[2],"main")
    VM.enviar_imagen(grafico)

cv2.imwrite("salida.jpg",img)