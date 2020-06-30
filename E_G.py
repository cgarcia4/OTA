#envio Imagenes
import cv2
import requests
import time
T=[]
n=0



f = open("estado.txt","r")
f = f.readline()
f.replace("\n","")
if f=="1":
    try:
        img=cv2.imread("grafico.jpg")
        content_type = 'output_1.jpg'
        headers = {'content-type': content_type}# prepare headers for http request
        _, img_encoded = cv2.imencode('.jpg', img)# encode image as jpeg
        requests.post("https://capstonetest0.herokuapp.com/VMPaciente/video", data=img_encoded.tostring(), headers=headers)
    except:
        print("no mande nadi")
        enviar_grafico()
else:
    print("no mande nadi")
