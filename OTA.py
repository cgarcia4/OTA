#Ota UPDATE
import os
import sys
import psutil
import logging

def get_V():
	f = open("Version.txt","r")
	f = f.readline()
	return(f.replace("\n",""))
	


def restart():
	try:
	   p = psutil.Process(os.getpid())
	   for handler in p.get_open_files() + p.conections():
		os.close(handler.fd)
	except Exception, e:
	   logging.error(e)
	python = sys.executable
	os.execl(python, python, *sys.argv) 
