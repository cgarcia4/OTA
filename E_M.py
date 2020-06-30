#envio_mensajes
import requests
import time
import numpy as np
import json

np_load_old = np.load

np.load = lambda *a,**k: np_load_old(*a, allow_pickle=True, **k)


# call load_data with allow_pickle implicitly set to true
while True:
    try:
        
        mensaje = np.load('my_file.npy').item()
        mensajejson= json.dumps(mensaje)
    except:
        print("soy un codigo malo y no sirvo")
        
    try:
        
        r = requests.post("https://capstonetest0.herokuapp.com/VMPaciente/mensajes", data=mensajejson)
        f = open ("red.txt","w")
        f.write("0")
        f.close() 
    except:
        f = open ("red.txt","w")
        f.write("1")
        f.close() 
        
