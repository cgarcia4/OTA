#main
import VM as VM
import OTA as OTA
import cv2
from picamera import PiCamera
import time
import os
import sys
Version="2"
Version_OTA=OTA.get_V()
print(Version_OTA)


alarma=VM.alarmas()
camera = VM.camera()
bordes=VM.iniciar(camera,alarma)
T=time.time()

while time.time()-T<100:
    
    if Version!=Version_OTA:
        print ("amimir")
        os.system('sudo shutdown -r now')
    
    img=VM.recorte(camera,bordes)
    cv2.imwrite("foto_isi_10.jpg",img)
    zonas=VM.zonas(img)
    
    grafico=VM.graficos(zonas[2],"main")
    VM.enviar_imagen(grafico,"https://capstonetest0.herokuapp.com/VMPaciente/video")

cv2.imwrite("salida.jpg",img)
