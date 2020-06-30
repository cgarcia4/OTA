#main
import VM as VM
import OTA as OTA
import cv2
from picamera import PiCamera
import time
import os
import sys
import datetime
import numpy as np

Version="2"
alarma=VM.alarmas()
a = open("contador.txt","r")
a = a.readline()
a.replace("\n","")
a=int(a)



try:
    camara = VM.camera()
except:
    estado(alarma,4)
    
def main(camara,alarma,Version,a):
    bordes=VM.iniciar_2(camara,alarma)
    f = open("Version.txt","r")
    f = f.readline()
    Version_OTA=f.replace("\n","")
    
    while True:
        print(a)
        f = open("Version.txt","r")
        f = f.readline()
        Version_OTA=f.replace("\n","")

        if Version!=Version_OTA:
            print ("amimir")
            os.system('sudo shutdown -r now')
            
        img=VM.recorte(camara,bordes,alarma)
        zonas=VM.zonas(img)
        try:
            palabra = VM.detector_palabras_modos(zonas[3]) #entrega una unica matriz que contiene a la palabra delimitada
            modo = VM.lector_modos_a(palabra)
        except:
            main(camara,alarma,Version,a)
        try:
            palabra_g = VM.detector_palabras_tipog(zonas[4])
            modo_g = VM.lector_modos(palabra_g)
        except:
            main(camara,alarma,Version,a) 
        try:
            M=VM.procesa_mediciones(zonas[0])
        except:
            main(camara,alarma,Version,a)   
        try:
            A=VM.procesa_alarmas(zonas[1],modo)
        except:
            main(camara,alarma,Version,a)
        
        grafico=VM.graficos(zonas[2],"main")
        grafico=cv2.resize(grafico, (600,400))
        mensaje=VM.mensaje_2(modo,A,M,Version,a)
        np.save('my_file.npy', mensaje)
        f = open ("estado.txt","w")
        f.write("0")
        f.close()
        cv2.imwrite("grafico.jpg",grafico)
        f = open ("estado.txt","w")
        f.write("1")
        f.close()
        f = open ("contador.txt","w")
        f.write(str(a))
        f.close()
        a=a+1

while True:
    main(camara,alarma,Version,a)
