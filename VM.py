#Funciones Ventilador mecánico
from __future__ import print_function
import cv2
import numpy as np
import imutils
from picamera import PiCamera
import io
from gpiozero import LED
import time

import requests
import json


def iniciar(camera,alarma):
    stram = io.BytesIO()
    aux=0
    while aux==0:
        time.sleep(1)
        estado(alarma,2) #indica que hay problemas con la camara, hasta calibrarla
        Bordes=True
        x_max=0
        y_max=0
        x_min=3000
        y_min=3000
        stram = io.BytesIO()
        camera.capture(stram, format = "jpeg")
        data = np.fromstring(stram.getvalue(), dtype=np.uint8)
        img = cv2.imdecode(data,1)
        
        gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #blanco y negro
        gauss = cv2.GaussianBlur(gris, (5,5), 0) #filtro para el ruido
        ret,th = cv2.threshold(gauss,25,255,cv2.THRESH_BINARY)
        #cv2.imshow("",th)
        #cv2.waitKey(0)
        cnts = cv2.findContours(th, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) #busco los contornos de la imagen aplicado el treshold
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:1]
        rect = np.zeros((4, 2), dtype = "float32")# array donde guardare las esquinas de la pantalla
        for c in cnts:
            approx = cv2.approxPolyDP(c, 0.009 * cv2.arcLength(c, True), True)
            n = approx.ravel()

        for c in cnts:
            for x in range (0,len(c)-1):
                x_max=max(x_max,c[x][0][0])
                x_min=min(x_min,c[x][0][0])
                y_max=max(y_max,c[x][0][1])
                y_min=min(y_min,c[x][0][1])
        print([x_max,y_max,x_min,y_min])
        print(len(n))
        if x_min ==0  or y_min==0 or x_max==1919 or y_max==1079:
            Bordes=False
            
            
        if Bordes==True:
            pts=np.zeros((int(len(n)/2),2),dtype="float32")
            for k in range (0, int((len(n)/2))): #extraigo los posibles candidatos a esquinas
                pts[k]=[n[2*k],n[2*k+1]]
                    
            s= pts.sum(axis = 1)             #A partir de relaciones de maximos y minimas distancias se extraen las 4 esquinas
            rect[0] = pts[np.argmin(s)]
            rect[0][0]=rect[0][0]-5
            rect[2] = pts[np.argmax(s)]
            rect[2][0]=rect[2][0]+4

            diff = np.diff(pts, axis = 1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            rect[3][0]=rect[3][0]-5
            rect[3][0]=rect[3][0]+4
            if len(n)<16:
                estado(alarma,1) #indica que la camara esta en posición
                aux=1
                (bl, br, tr, tl) = rect #camara inv
                widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
                widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
                maxWidth = max(int(widthA), int(widthB))
                heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
                heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
                maxHeight = max(int(heightA), int(heightB))
                
                dst = np.array([
                        [0, 0],
                        [maxWidth - 1, 0],
                        [maxWidth - 1, maxHeight - 1],
                        [0, maxHeight - 1]], dtype = "float32")
                    
                    #se corrige y extrae la pantalla, usando como input los puntos y distancias entre ellos
                M = cv2.getPerspectiveTransform(rect, dst)
                return [M,maxWidth,maxHeight]
        enviar_imagen(img)  
        
def alarmas():
    normal= LED(22)
    cam = LED(27)
    net = LED(17)
    return [normal,cam,net]

def estado(alarmas,a):
    if a==1:
        alarmas[0].on()
        alarmas[1].off()
        alarmas[2].off()
    elif a==2:
        alarmas[0].off()
        alarmas[1].on()
        alarmas[2].off()
    elif  a==3:
        alarmas[0].off()
        alarmas[1].off()
        alarmas[2].on()
    elif  a==4:
        alarmas[0].on()
        alarmas[1].on()
        alarmas[2].on()
    else:
        alarmas[0].off()
        alarmas[1].off()
        alarmas[2].off()
        
def recorte(camera,bordes):
    stram = io.BytesIO()
    camera.capture(stram, format = "jpeg")
    data = np.fromstring(stram.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(data,1)
    warped = cv2.warpPerspective(img, bordes[0], (bordes[1], bordes[2]))
    return cv2.rotate(warped, cv2.ROTATE_180)


def zonas(recorte):
    img = cv2.resize(recorte, (1200,1000))#reescalo 
    #RECORTE INCIAL: Por zona aproximada - rectángulos de mediciones, rectágulo de alarmas y rectángulo de gráficos
    zonamed = img[60:710, 0:160] #zona mediciones
    zonaalarm = img[720:900, 0:1200] #zona alarmas
    zonagraf = img[60:740, 160:1200] #zona gráficos
    zonamodo= img[0:80, 15:500]      #zona modo
    zonatipog= img[0:80, 500:700]    #zona tipo de gráfico
    
    return [zonamed,zonaalarm,zonagraf,zonamodo,zonatipog]
    

def enviar_imagen(img, url= 'http://127.0.0.1:5000/VMPaciente/video'):
    content_type = 'output_1.jpg'
    headers = {'content-type': content_type}# prepare headers for http request
    _, img_encoded = cv2.imencode('.jpg', img)# encode image as jpeg
    requests.post(url, data=img_encoded.tostring(), headers=headers)
    return 0

def enviar_data(mensaje,url = 'http://127.0.0.1:5000/VMPaciente/mensajes'):
    mensajejson= json.dumps(mensaje)
    r = requests.post(url, data=mensajejson)
    return 0


def graficos(zonagraf,mode):
    if mode=="trends":
        return zonagraf[0:385, 0:1040]
    
    elif mode=="main":
        return zonagraf[0:680, 0:1040]
    
    elif mode=="loops":  #debo corregirlo arriba después
        return zonagraf[0:650, 0:1040]













