#Funciones Ventilador mecánico
from __future__ import print_function
import cv2
import numpy as np
import imutils
from picamera import PiCamera
import io
from gpiozero import LED
import time
import datetime
import requests
import json
a=PiCamera()

cero = cv2.imread('Base_datos/bd0.png',0)
uno = cv2.imread('Base_datos/bd1.png',0)
dos= cv2.imread('Base_datos/bd2.png',0)
tres = cv2.imread('Base_datos/bd3.png',0)
cuatro = cv2.imread('Base_datos/bd4.png',0)
cinco = cv2.imread('Base_datos/bd5.png',0)
seis = cv2.imread('Base_datos/bd6.png',0)
siete = cv2.imread('Base_datos/bd7.png',0)
ocho = cv2.imread('Base_datos/bd8.png',0)
nueve = cv2.imread('Base_datos/bd9.png',0)

basedatos =[cero, uno, dos, tres, cuatro, cinco, seis, siete, ocho, nueve]


def camera():
    global a
    return a

def iniciar(camera,alarma):
    stram = io.BytesIO()
    aux=0
    stram = io.BytesIO()
    camera.capture(stram, format = "jpeg")
    data = np.fromstring(stram.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(data,1)
    while aux==0:
        
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
        ret,th = cv2.threshold(gauss,30,255,cv2.THRESH_BINARY)
        cv2.imshow("",th)
        cv2.waitKey(0)
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
            if len(n)<28:
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
        cv2.imwrite("grafico.jpg",img)
        
def iniciar_2(camera,alarma):
    #camera.brightness= 45
    stram = io.BytesIO()
    aux=0
    stram = io.BytesIO()
    camera.capture(stram, format = "jpeg")
    data = np.fromstring(stram.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(data,1)
    while aux==0:
        red = open("red.txt","r")
        red = red.readline()
        R=red.replace("\n","")
        if R=='1':
            estado(alarma,3)
        else:
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
        TH=[]
        for a in range (0,20):
            Bordes=True
           
            ret,th = cv2.threshold(gauss,20+a,255,cv2.THRESH_BINARY)   
            cnts = cv2.findContours(th, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) #busco los contornos de la imagen aplicado el treshold
            cnts = imutils.grab_contours(cnts)
            cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:1]
            rect = np.zeros((4, 2), dtype = "float32")# array donde guardare las esquinas de la pantalla
            #cv2.imshow("",th)
            #cv2.waitKey(0)
            for c in cnts:
                approx = cv2.approxPolyDP(c, 0.009 * cv2.arcLength(c, True), True)
                n = approx.ravel()
                for x in range (0,len(c)-1):
                    x_max=max(x_max,c[x][0][0])
                    x_min=min(x_min,c[x][0][0])
                    y_max=max(y_max,c[x][0][1])
                    y_min=min(y_min,c[x][0][1])
            #print(len(n))
            if x_min ==0  or y_min==0 or x_max==1919 or y_max==1079:
                Bordes=False
            if Bordes==True:     
                    if len(n)<12:
                        aux=1
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
                
                        estado(alarma,1) #indica que la camara esta en posición
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
                        #cv2.imshow("",th)
                        #cv2.waitKey(0)
                        return [M,maxWidth,maxHeight]
            f = open ("estado.txt","w")
            f.write("0")
            f.close()
            cv2.imwrite("grafico.jpg",img)
            f = open ("estado.txt","w")
            f.write("1")
            f.close()
            
            
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
        
def recorte(camera,bordes,alarma):           
    red = open("red.txt","r")
    red = red.readline()
    R=red.replace("\n","")
    
    if R=='1':
        estado(alarma,3)
    else:
        estado(alarma,1)        
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
    
def detector_circulos(zona_a):
  lista_circ=[]
  #PREPROCESAMIENTO
  copy = cv2.bitwise_not(zona_a)
  zona = (cv2.createCLAHE(clipLimit=0.0, tileGridSize=(1,1))).apply(copy) ##creo una copia con más contraste
  zona = cv2.blur(zona, (9, 9),) # Blur (difuminado/emparejado)
  #RECONOCIMIENTO CIRCULOS Y UBICACIÓN
  detected_circles = cv2.HoughCircles(zona, cv2.HOUGH_GRADIENT, 1, 60, param1 = 50, param2 = 30, minRadius = 50, maxRadius = 70)
  if detected_circles is not None: # Draw circles that are detected
    detected_circles = np.uint16(np.around(detected_circles))   # Convert the circle parameters a, b and r to integers. 
    for pt in detected_circles[0, :]: 
      a, b, r = pt[0], pt[1], pt[2]
      #RECORTE ZONA DE VALOR NUMERICO AL INTERIOR DE CADA CIRCULO
      in_circ= zona_a[b-25:b+45, a-56:a+50] #corto el pedazo que me importa dentro del circulo
      lista_circ.append([a, in_circ])     #lo agrego a la lista de pedacitos
  #REORENAMIENTO Y FORMACIÓN LISTA
  lista_circ.sort() #ordena de izquierda a derecha
  l_circ=[]
  for par in lista_circ:
    l_circ.append(par[1]) #forma lista de interiores de los circulos
  return (l_circ)

def detector_caracteres(in_circ, lmin, lmax, amin, amax, dil, colitas):
  lista_zchars=[]
  #PREPROCESAMIENTO
  gris = cv2.bitwise_not(in_circ)
  pre = cv2.dilate(gris, (np.ones((dil,dil),np.uint8)), iterations = 1)#pongo flaquito
  pre = cv2.threshold(pre, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1] #th con leras blancas
  pre= cv2.medianBlur(pre, 5) #blur para emparejar
  pre = cv2.Canny(pre, 80, 200, 255)
  #BUSCADOR CONTORNOS
  contours, hierarchy = cv2.findContours(pre, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) #puntos contornos
  for contour in contours:
    #BUSCADOR RECTANGULOS
    (x,y,l,a) = cv2.boundingRect(contour) #coordenadas rect, ancho (l) y altura(a)
    if (l>lmin and l<lmax) and (a>amin and a<amax): #si el rectangulo cumple con el tamaño esperado
      #RECORTE
      zchar = gris[y:y+a, x:x+l]  #se recorta el rectangulo de la zona en gris
      if (colitas==1) and (a*l)> 1220: #si el área es más grande de lo general, entonces posee colita y se la recorto altiro
        zchar=zchar[0:a, 7:l]
        l=l-7
        x=x+7
        if a>2.1*l:    #si quedo muy flaquito
          zchar=zchar[0:a-10, 0:l]
          a=a-10    #acorto de abajo, porque la colita es baja
      lista_zchars.append([zchar, x]) #agrego el rectangulo a la lista de caracteres probables
  #REORDENAMIENTO Y FORMACIÓN LISTA DE NUMEROS (RESULTADO LECTURA)
  lista_zchars.sort(key = lambda x: x[1]) #ordena usando el segundo valor de cada sublista
  rects_posicion=[]
  x_antes=0
  for zch in lista_zchars:
    x = zch[1]
    if x!=x_antes:
      rects_posicion.append(zch) #pone su valor al final(derecha)
    x_antes=x
  return (rects_posicion) #retorno una lista de rectangulos donde probablemente exista un caracter

def lector_numeros(rect_char, factor_delgadez, ny_ajuste):
  global basedatos
  val=[]  
  l,a = (len(rect_char[0])), (len(rect_char))  # a=altura imagen (numero filas), l= largo horizontal (numero columnas)
  #PREPROCESAMIENTO
  th = cv2.threshold(rect_char, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
  th= cv2.bitwise_not(th)
  matrixth= np.array(th) #matriz 2D del rectangulo
  vectorth = matrixth.ravel() #vector 1D de la matriz
  posicion, puntajemax, pescogida, iescogida = 0,0,0, cv2.imread('bd0.png',0) #inicializacion
  if a>factor_delgadez*l: #2.1 #si es más alto que ancho
    pescogida =1
    iescogida = cv2.imread('bd1.png',0) #es un uno, inmediatamente
  else:
    for n in basedatos:  #recorro la base de datos
      puntaje, i= 0, 0 #inicializacion del puntaje de coicncidencia y posición en el vector
      num = cv2.resize(n, (l, a))#reescalo imagen de base de datos para que coincida con la comparada
      matrixn= np.array(num)
      vectorn = matrixn.ravel()  #vector 1D de la matriz del numero en la base de datos
      while i<(a*l):
        if (vectorn[i]==vectorth[i]):     #si existe coicidencia de pixel negro en ambas coordenadas
          puntaje= puntaje+1              #sumo coincidencia al puntaje
        else:                             #si no coinciden
          puntaje=puntaje-1               #resto puntaje por falta de coincidencia
        i=i+1                             #sumo 1 a la posición dentro del vector para moverme en este
      if (puntaje> puntajemax) and (posicion!=1):    #si el puntaje final de coincidencia supera al maximo anterior y no es uno
        puntajemax=puntaje                         #entonces este puntaje es el nuevo máximo
        iescogida, pescogida = n, posicion         #y asocio la imagen a este número
      posicion= posicion+1                #sigo recorriendo la base de datos, guardando la posición en ella
  if pescogida == 6 and ((matrixth[ny_ajuste][6]== 255) or (matrixth[ny_ajuste][5]== 255) or (matrixth[ny_ajuste-1][6]== 255)) : # esta es otra condicion para diferenciar el 5 del 6
    iescogida = basedatos[5]
    pescogida= 5
  if pescogida ==8 and ((matrixth[15][5]== 255) or (matrixth[16][5]== 255)): 
    iescogida = basedatos[3]
    pescogida =3
  return (pescogida)

def formador_mensaje(m, val):
  #ALMACENAMIENTO Y ASIGNACIÓN DE VALORES A VARIABLES SEGUN MODO
  if m == "Volume A/C":
    mensajealarmas = ["Rate: "+ val[0]+" rpm", "Volume: "+ val[1]+" mL", "Peak Flow: "+val[2]+" L/min", "Insp Pause: "+ val[3]+ " rpm", "PEEP: "+ val[4]+ " cmH2O", "Flow Trig: "+ val[5]+ " L/min",  "FIO2: "+ val[6]+ " %"]
  elif m == "TCPL":
    mensajealarmas = ["Rate: "+ val[0]+" rpm", "Ins Press: "+ val[1]+" cmH2O", "Peak Flow: "+val[2]+" L/min", "Insp Time: "+ val[3]+ " sec", "PEEP: "+ val[4]+ " cmH2O", "Flow Trig: "+ val[5]+ " L/min",  "FIO2: "+ val[6]+ " %"]
  elif m == "Pressure A/C":
    mensajealarmas = ["Rate: "+ val[0]+" rpm", "Insp Pres: "+ val[1]+" cmH2O", "Insp Time: "+ val[2]+ " sec", "PEEP: "+ val[3]+ " cmH2O", "Flow Trig: "+ val[4]+ " L/min",  "FIO2: "+ val[5]+ " %"]
  else: 
    mensajealarmas = "modo invalido"
  return (mensajealarmas)

#### FUNCIÓN PRINCIPAL ##########
def procesa_alarmas(imagen,modo):
  #LECTURA DE LA IMAGEN Y RECORTE DE LA ZONA DE ALARMAS
  zona_a=cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
  #RECORTES
  lista_circulos = detector_circulos(zona_a) #entrega lista de circulos ordenados de izquierda a derecha
  lista_valores=[]
  for circ in lista_circulos:
    string_valor=""
    lista_rect_posicion = detector_caracteres(circ, 12, 40, 33, 55, 3, 1) #entrega todos los rectángulos donde se ubican los carácteres con su posicion en x (de izquierda a derecha)
    #LECTURA COMPARATIVA
    posicion=0
    i=0
    punto=0
    for par_rect_posicion in lista_rect_posicion: 
      rect, posicion= par_rect_posicion[0], par_rect_posicion[1]
      if i==0: #primera posicion
        i=1
        posicion_antes=posicion
      else:
        delta_p= posicion - posicion_antes
        if delta_p>35:  #si este rect esta muy lejos del anterior
          string_valor= string_valor+"."      #entonces agrego un punto en frente
        posicion_antes= posicion
      numero = lector_numeros(rect, 2.1, 25) #asigna un valor(numero) al rectangulo donde se ubica el caracter por puntaje de coincidencia y guarda su posicion en x
      numero_en_string = str(numero)
      string_valor= string_valor + numero_en_string #pasa cada par [numero, posicion] a un string con el valor real(considera la posicion para saber si hay puntos en medio)
    lista_valores.append(string_valor)
  mensaje= formador_mensaje(modo, lista_valores) #pasa la lista de valores-string encontrados a un mensaje, asignandole a cada quien su variable correspondiente
  return (mensaje)


def corta_mediciones(zona_m):
  #PREPROCESAMIENTO
  zona= cv2.bitwise_not(zona_m)
  zonath = cv2.threshold(zona, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1] #para distinguir cuadraditos
  zonath = cv2.medianBlur(zonath, 5) #blur para emparejar
  kernel = np.ones((5,5),np.uint8) #ventana de los siguientes filtros
  zonath= cv2.erode(zonath, kernel, iterations = 4)#erosion
  #RECORTE: AREA DE INTERÉS
  coords = np.column_stack(np.where(zonath ==[0]))  #[[x1 y1] [x2 y2] ....] cordenadas de pixeles negros
  ymin, ymax, xmin=700, 0, 200
  for c in coords: #[xi yi]
    y, x= c[0], c[1]
    if x==80: #busco desde la mitad 
      if y< ymin:  #busco el primer pixel negro de arriba hacia abajo
        ymin=y
      if y> ymax: #busco el ultimo pixel negro de arriba hacia abajo
        ymax=y
    if x< xmin:  #busco el primer pixel negro de izquierda a derecha
      xmin=x
  h= int((ymax -ymin)*0.2) #altura de cada rectángulo es la altura total dividida en 5
  y=ymin
  i=1
  lista_zonas_med=[]
  #SUBRECORTE CUADRITOS: PARES VARIABLE-MEDICIÓN
  while i<=5:
    parmed = zona[y:y+h, xmin:145] #recorto la imágen gris
    lista_zonas_med.append(parmed)
    y=int(y+h+3) #un quinto de la altura
    i=i+1
  return (lista_zonas_med)

def detector_palabras(zona_palabra): #RECORTA LA ZONA QUE DELIMITA LA PALABRA A RECONOCER
  #PREPROCESAMIENTO
  gris = cv2.bitwise_not(zona_palabra)
  pre = cv2.dilate(gris, (np.ones((3,3),np.uint8)), iterations = 1)#pongo flaquito
  pre = cv2.threshold(pre, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1] #th con leras blancas
  pre= cv2.medianBlur(pre, 7) #blur para emparejar
  pre = cv2.Canny(pre, 80, 200, 255)
  #BUSCADOR CONTORNOS
  contours, hierarchy = cv2.findContours(pre, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) #puntos contornos externos
  for contour in contours:
    #BUSCADOR RECTANGULOS
    (x,y,l,a) = cv2.boundingRect(contour) #coordenadas rect, ancho (l) y altura(a)
    if (l>10 and l<100) and (a>15 and a<40): #si el rectangulo cumple con el tamaño esperado
      zchar = gris[y:y+a, x:x+l]  #se recorta el rectangulo de la zona en gris
  return (zchar) #retorno una lista de rectangulos donde probablemente exista un caracter

def lector_variable(palabra):  #COMPARA CON LA BASE DE DATOS Y POR COINCIDENCIA ASIGNA UNA VARIABLE A LA ZONA
  l,a = (len(palabra[0])), (len(palabra))  # a=altura imagen (numero filas), l= largo horizontal (numero columnas)
  #PREPROCESAMIENTO
  if l<33:
    var="Vti"
  elif l<40:
    var="Vte"
  elif l<50: #puede ser FIO2 o Rate, asi que uso otro criterio
    th = cv2.threshold(palabra, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    matrix= np.array(th) #matriz 2D del rectangulo
    if (matrix[15][3]==255) and (matrix[16][3]==255):
      var = "Total Ve"
    elif (matrix[10][10]==255) and (matrix[10][11]==255):
      var = "FIO2"
    else:
      var="Rate"
  elif l<55:
    var="Total Ve"
  elif l<61:  
    var="Vti/Kg"
  else:
    var="Ppeak"
  return (var)
#### FUNCIÓN PRINCIPAL ##########
def procesa_mediciones(imagen):
  lista_resultado=[]
#   img = cv2.resize(imagen, (1200,1000))
#   img=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#   zona_m = img[60:710, 0:160] #zona mediciones
  img=cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
  zona_m =img
  #RECORTES
  lista_resultados=[]
  lista_zonas_pares = corta_mediciones(zona_m) #define las areas/cuadritos donde se ubican las mediciones en pares de imágenes variable-valor
  for med in lista_zonas_pares:
    #cv2.imshow("",med)
    #cv2.waitKey(0)
### ASIGNACIÓN NÚMERO #####
    zona_valor = med[0:60, 0:]   #zona donde esta el numero
    string_valor=""
    lista_rect_posicion = detector_caracteres(zona_valor, 10, 40, 35, 50, 1, 0) #entrega todos los rectángulos donde se ubican los carácteres con su posicion en x (de izquierda a derecha)
    posicion=0
    i=0
    punto=0
    for par_rect_posicion in lista_rect_posicion: 
      rect, posicion= par_rect_posicion[0], par_rect_posicion[1]
      if i==0: #primera posicion
        i=1
        posicion_antes=posicion
      else:
        delta_p= posicion - posicion_antes
        if delta_p>40:  #si este rect esta muy lejos del anterior
          string_valor= string_valor+"."      #entonces agrego un punto en frente
        posicion_antes= posicion
      numero = lector_numeros(cv2.bitwise_not(rect), 2.1, 30) #asigna un valor(numero) al rectangulo donde se ubica el caracter por puntaje de coincidencia y guarda su posicion en x
      numero_en_string = str(numero)
      string_valor= string_valor + numero_en_string #pasa cada par [numero, posicion] a un string con el valor real(considera la posicion para saber si hay puntos en medio)
#### ASIGNACIÓN VARIABLE #####
    zona_variable = med[85:,0:] #zona donde esta la palabra/variable
    
    palabra = detector_palabras(zona_variable) #entrega una unica matriz que contiene a la palabra delimitada
    nombre = lector_variable(palabra) #traduce la matriz asignandole la variable correspondiente
    lista_resultados.append([nombre, string_valor])
  #mensaje= formador_mensaje(lista_valores)
  return (lista_resultados)

def detector_palabras_modos(zona_palabra): #RECORTA LA ZONA QUE DELIMITA LA PALABRA A RECONOCER
  #PREPROCESAMIENTO
  gris = cv2.cvtColor(zona_palabra, cv2.COLOR_BGR2GRAY)
  gris = cv2.bitwise_not(gris)
  pre = cv2.erode(gris, (np.ones((5,7),np.uint8)), iterations = 1)#pongo flaquito
  pre = cv2.threshold(pre, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1] #th con leras blancas
  pre= cv2.medianBlur(pre, 3) #blur para emparejar
  pre = cv2.Canny(pre, 100, 200, 255)
  #BUSCADOR CONTORNOS
  contours, hierarchy = cv2.findContours(pre, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) #puntos contornos externos
  for contour in contours:
    #BUSCADOR RECTANGULOS
    (x,y,l,a) = cv2.boundingRect(contour) #coordenadas rect, ancho (l) y altura(a)
    if (l>80 and l<300) and (a>20 and a<60): #si el rectangulo cumple con el tamaño esperado
      zchar = gris[y:y+a, x:x+l]  #se recorta el rectangulo de la zona en gris
  return (zchar) #retorno rectangulo donde probablemente exista un modo

def lector_modos_a(palabra): #DETECTA POR LARGO
  l,a = (len(palabra[0])), (len(palabra))  # a=altura imagen (numero filas), l= largo horizontal (numero columnas)
  #PREPROCESAMIENTO
  if l<150:
    modo="TCPL"
  elif l<170:
    modo="Volume A/C"
  else:
    modo="Pressure A/C"
  return modo

def detector_palabras_tipog(zona_palabra): #RECORTA LA ZONA QUE DELIMITA LA PALABRA A RECONOCER
  #PREPROCESAMIENTO
  gris = cv2.cvtColor(zona_palabra, cv2.COLOR_BGR2GRAY)
  gris = cv2.bitwise_not(gris)
  pre = cv2.erode(gris, (np.ones((3,3),np.uint8)), iterations = 1)#pongo flaquito
  pre = cv2.threshold(pre, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1] #th con leras blancas
  pre= cv2.medianBlur(pre, 3) #blur para emparejar
  pre = cv2.Canny(pre, 100, 200, 255)
  #BUSCADOR CONTORNOS
  contours, hierarchy = cv2.findContours(pre, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) #puntos contornos externos
  for contour in contours:
    #BUSCADOR RECTANGULOS
    (x,y,l,a) = cv2.boundingRect(contour) #coordenadas rect, ancho (l) y altura(a)
    if (l>40 and l<100) and (a>15 and a<40): #si el rectangulo cumple con el tamaño esperado
      zchar = gris[y:y+a, x:x+l]  #se recorta el rectangulo de la zona en gris
  return (zchar) #retorno rectangulo donde probablemente exista un modo

def lector_modos(palabra): #DETECTA POR LARGO
  l,a = (len(palabra[0])), (len(palabra))  # a=altura imagen (numero filas), l= largo horizontal (numero columnas)
  #PREPROCESAMIENTO
  if l<60:
    modo="MAIN"
  elif l<75:
    modo="LOOPS"
  else:
    modo="TRENDS"
  return modo

def mensaje(modo,alarmas,mediciones):
    mensaje={}
    mensaje["var1"]="modo="+modo
    msj=alarmas+mediciones
    var="var"
    aux=2
    r=len(msj)
    u=0
    while len(msj)>u:
        mensaje[var+str(aux)]=msj[u]
        aux=aux+1
        u=u+1
        
    return mensaje

def mensaje_2(modo,alarmas,mediciones,ver):
    mensaje={}
    fh_time=datetime.datetime.now()
    fh_s = fh_time.strftime("%Y-%b-%d %H:%M:%S.%f")
    mensaje["tiemp"]=fh_s
    mensaje["modo"]="Modo"+ modo
    
    for a in range(0,len(alarmas)):
        mensaje["al"+str(a+1)]=alarmas[a]
    for a in range(len(alarmas),7):
        mensaje["al"+str(a)]=" "
        
    for a in range(0,len(mediciones)):
        mensaje["med"+str(a+1)]=mediciones[a]
    for a in range(len(mediciones),5):
        mensaje["med"+str(a)]=" "
        
    mensaje["version"]=ver
    return mensaje





