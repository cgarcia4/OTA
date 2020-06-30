#/home/pi/Desktop/Casptone/Entrega_3
import os
import sys
import subprocess

def get_V():
    f = open("Version.txt","r")
    f = f.readline()
    return(f.replace("\n",""))


