#TCPImageServer v0.1.3


import socket
import sys
import pygame
from os import listdir
import os.path
from pygame.locals import *
import threading
import time
import subprocess
import netifaces as ni
from omxplayer import OMXPlayer

pygame.init()


ni.ifaddresses('eth0')
ip = ni.ifaddresses('eth0')[2][0]['addr']

#Connection Info#
TCP_IP = ip
TCP_PORT = 5007
BUFFER_SIZE = 1024


#MEDIA DIR#
MEDIA = '/home/pi/MEDIA/'





#Bind to socket#

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP,TCP_PORT))
s.listen(8)



def video(moviefile, loop, stop_event):
    while(not stop_event.is_set()):
        print("{} thread has started".format("video"))
        if(loop == True):
            looparg = '--loop'
        else:
            looparg = ''
        os.popen("omxplayer -o hdmi " + looparg + " --no-osd --win '0 0 1920 1080' /home/pi/MEDIA/videos/" + moviefile)
        stop_event.wait(2)
        if(loop == False):
            mt_stop.set()
        pass

mt_stop = threading.Event()
mt = threading.Thread(name='video', target=video)
          
#windowSurface initial properties#
WIDTH=1920
HEIGHT=1080
windowSurface = pygame.display.set_mode((WIDTH,HEIGHT), 0, 32)
img= pygame.image.load('/home/pi/MEDIA/images/eslwp.jpg')
pygame.mouse.set_visible(False);
windowSurface.blit(img, (0, 0))
pygame.display.flip()



            

conn, addr = s.accept()

#main loop#
while True:
    print("started")
    

    events = pygame.event.get()

    print("AJSNKJNFKN")

    d = conn.recv(BUFFER_SIZE)

    if d == "":
        conn, addr = s.accept()
    print("conn")

    raw = d.decode('utf-8')

    print ("received message:" + raw)

    loop = False

    try:
        if raw.index("PLAY ") == 0:
            ARGS = raw.split(' ')
            
            file = ARGS[1];
            loop = False
            try:
                if ARGS[2] == "LOOP":
                    print("LOOPING MOVIE")
            except IndexError:
                print("NO LOOP ARG")
            else:
                loop = True
            
            print( "File is " + '"' + file + '"')
            newevent = pygame.event.Event(USEREVENT)
            pygame.event.post(newevent)
    except ValueError:
            print("Not a play command")

    try:
        if raw.index("MOVIE ") == 0:
            
            ARGS = raw.split(' ')
            
            file = ARGS[1];
            loop = False
            try:
                if ARGS[2] == "LOOP":
                    print("LOOPING MOVIE")
            except IndexError:
                print("NO LOOP ARG")
            else:
                loop = True
                
            print( "File is " + '"' + file + '"')
            newevent = pygame.event.Event(movieevent)
            pygame.event.post(newevent)
    except ValueError:
        print("Not a play command")
    #HELP#
    try:
        if raw.index("HELP") == 0:
            f = open("tcpimageserver.txt","r")    

            file = f.read(1024)
           
            conn.send(file.encode('utf-8'))
    except ValueError:
        print("Not a HELP command")
    #KILL#
    try:
        if raw.index("KILL") == 0:
            newevent = pygame.event.Event(QUIT)
            pygame.event.post(newevent)
    except ValueError:
        print("Not a kill command")

    try:
        if raw.index("LIST") == 0:

            w = listdir(MEDIA + 'images')
            for index in range(len(w)):
                w[index] = w[index] + " [STILL]"

            x = listdir(MEDIA + 'videos')
            for index in range(len(x)):
                x[index] = x[index] + " [VIDEO]"

            y = w + x
            y = sorted(y, key=str.lower)
            z = ' \r\n'.join(y)

            print (z)
            conn.send(z.encode('utf-8'))
    except ValueError:
        print("Not a list command")

        
    

            
    #pygame events#
    for event in pygame.event.get():
	    if event.type == QUIT:
                conn.close()
                subprocess.call("pkill omx", shell=True)
                mt_stop.set()
                print ("event: KILL")
                pygame.quit()
                sys.exit()
	    if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SEMICOLON:
                        #mt_stop.set()
                        print ("event: KILL1")
                        pygame.quit()
                        sys.exit()
            if event.type == USEREVENT:
                try:
                    try:
                        mt_stop.set()
                        if(os.path.isfile("/home/pi/MEDIA/images/" + file)):
                            img = pygame.image.load("/home/pi/MEDIA/images/" + file + ".jpg")
                            img1 =pygame.transform.scale(img, (1920,1080));
                            windowSurface.blit(img1, (0,0))
                            pygame.display.flip()
                            #if(mt.isAlive()):
                            subprocess.call("pkill omx", shell=True)
                        if(os.path.isfile("/home/pi/MEDIA/videos/" + file)):
                            mt_stop.clear()
                            mt = threading.Thread(target=video, args=(file, loop, mt_stop))
                            mt.start()
                                        


                        img = pygame.image.load("/home/pi/MEDIA/images/" + file)
                        img1 =pygame.transform.scale(img, (1920,1080));

                    except:
                        if(os.path.isfile("/home/pi/MEDIA/images/" + file + ".jpg")):
                            print ("file resolved as: " + file + ".jpg")
                            img = pygame.image.load("/home/pi/MEDIA/images/" + file + ".jpg")
                            img1 =pygame.transform.scale(img, (1920,1080));
                            windowSurface.blit(img1, (0,0))
                            pygame.display.flip()
                            #if(mt.isAlive()):
                            subprocess.call("pkill omx", shell=True)
                        if(os.path.isfile(MEDIA + "/images/" + file + ".png")):
                            print ("file resolved as: " + file + ".png")
                            img = pygame.image.load(MEDIA + "/images/" + file + ".png")
                            img1 =pygame.transform.scale(img, (1920,1080));
                            windowSurface.blit(img1, (0,0))
                            pygame.display.flip()
                            #if(mt.isAlive()):
                            subprocess.call("pkill omx", shell=True)
                        if(os.path.isfile("/home/pi/MEDIA/videos/" + file + ".mp4")):
                            print ("file resolved as: " + file + ".mp4")
                            mt_stop.clear()
                            file = file + ".mp4"
                            mt = threading.Thread(target=video, args=(file, loop, mt_stop))
                            mt.start()
                    else:

                        mt_stop.set()
                        windowSurface.blit(img1, (0,0))
                        pygame.display.flip()
                        #if(mt.isAlive()):
                        subprocess.call("pkill omx", shell=True)
                except:
                    print("User Event Error")

conn.close()


