#!/usr/bin/python
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from os import curdir, sep
import cgi
import imageio
import numpy
from scipy import ndimage
from g2s import run as g2s
from PIL import Image
import base64
from io import BytesIO
from threading import Thread
from queue import Queue
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

hostName = ""
hostPort = 80
serverAddress="localhost"

q = Queue(maxsize=0)
# Use many threads (50 max, or one for each url)
num_theads = 1;

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):

		if 'limit=off' in self.path:
			self.path="/tryAgain.html"

		mainPath=self.path.split('?')[0];

		print(mainPath)

		if mainPath=="/":
			self.path="/qs.html"

		if mainPath=="/qs":
			self.path="/qs.html"

		try:
			#Check the file extension required and
			#set the right mime type

			sendReply = False
			if self.path.endswith(".html"):
				mimetype='text/html'
				sendReply = True
			if self.path.endswith(".jpg"):
				mimetype='image/jpg'
				sendReply = True
			if self.path.endswith(".jpeg"):
				mimetype='image/jpeg'
				sendReply = True
			if self.path.endswith(".gif"):
				mimetype='image/gif'
				sendReply = True
			if self.path.endswith(".png"):
				mimetype='image/png'
				sendReply = True
			if self.path.endswith(".js"):
				mimetype='application/javascript'
				sendReply = True
			if self.path.endswith(".css"):
				mimetype='text/css'
				sendReply = True

			if sendReply == True:
				#Open the static file requested and send it
				f = open(curdir + sep + self.path) 
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				if 'text' in mimetype or 'application' in mimetype:
					f = open(curdir + sep + self.path) 
					self.wfile.write(bytes(f.read(), "utf-8"))
				else:
					f = open(curdir + sep + self.path,'rb') 
					self.wfile.write(bytes(f.read()))
				f.close()
			return


		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	def do_POST(self):
		if self.path=="/qsRun":
			form = cgi.FieldStorage(
				fp=self.rfile, 
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
						'CONTENT_TYPE':self.headers['Content-Type'],
			})

			im=None;
			dt=None;
			if form.getfirst("ti")=='file':
				im = imageio.imread(form["uploadedImage"].file.read());
				dt=numpy.zeros(shape=(im.shape[2] if im.ndim>2 else 1 ,1));
				if im.shape[0]>300 or im.shape[1]>300:
					self.send_response(200)
					self.end_headers()
					self.wfile.write(bytes('{"error":"Uploaded image should be smaller than 300 x 300 px"}',"utf-8"));
			else :
				if form.getfirst("ti") in ['strebelle']:
					im = imageio.imread("Strebelle.png");
					dt = numpy.ones(shape=(1,1));
				if form.getfirst("ti") in ['stone']:
					im = imageio.imread("Stone.png");
					dt = numpy.zeros(shape=(1,1));

			idValue=-2 ;
			if im is not None :
				target=numpy.nan*numpy.empty((int(form.getfirst("h")),int(form.getfirst("w")),im.shape[2]) if im.ndim>2 else (int(form.getfirst("h")),int(form.getfirst("w"))));
				idValue=g2s('-sa',serverAddress,'-a','qs','-ti',im,'-di',target,'-dt',dt,'-k',float(form.getfirst("k")),'-n',int(form.getfirst("n")),'-s',int(form.getfirst("s")),'-submitOnly');#,'-j',0.5

			# isCategorical=False;
			# if "iscategorical" in form:
			# 	isCategorical=True;
			#q.put((form["emailAddress"].value,im,int(form["height"].value),int(form["width"].value),int(form["n"].value),float(form["k"].value),isCategorical))

			self.send_response(200)
			self.end_headers()
			self.wfile.write(bytes('{"jobId":'+str(idValue)+',"WL":0}',"utf-8"));
			return
		if self.path=="/qsStatusOrResult":
			form = cgi.FieldStorage(
				fp=self.rfile, 
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
						'CONTENT_TYPE':self.headers['Content-Type'],
			})
			jobId=form.getfirst("jobId");
			progression=g2s('-sa',serverAddress,'-statusOnly',int(jobId));
			self.send_response(200)
			self.end_headers()

			if( type(progression) is tuple):
				buffered = BytesIO()
				Image.fromarray(progression[0].astype(numpy.uint8)).save(buffered, format="PNG");
				encoded_string = base64.b64encode(buffered.getvalue());
				self.wfile.write(bytes('{"WL":0,"progress":100,"sim":"'+encoded_string.decode("utf-8")+'"}',"utf-8"))
			else:
				self.wfile.write(bytes('{"WL":0,"progress":'+str(progression)+'}',"utf-8"))
			return

myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
	myServer.serve_forever()

except KeyboardInterrupt:
	pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
