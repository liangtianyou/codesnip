#-*- coding: utf-8 -*-

import os
import sys
import time
import socket
import select
import traceback

import utils
import settings
###############################
#接收HTTP和网络指令
###############################
class HttpSocket():
    def __init__ (self):
        self.connection = ''
        self.address = ''
        self.httpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.httpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while True:
            try:
                self.httpsock.bind(('0.0.0.0',9998))
                self.httpsock.listen(100)
                break
            except Exception,e:
				pass
            time.sleep(1)
    def Accept (self):
        try:
            self.connection,self.address = self.httpsock.accept()
            return self.connection,self.address
        except:
            pass
def Senddata (conn,senddata = 'ok'):
    try:
        sendbuf = conn.sendall(senddata)
    except:
        utils.debug(utils.debug_line(),"sockets",traceback.print_exc())
def Recvdate (conn):
    try:
        conn.settimeout(5)
        readbuf = conn.recv(settings.BUFFSIZE)
        return readbuf
    except:
        utils.debug(utils.debug_line(),"sockets",'Recive data time out!')
        return -1
def CloseSocket (conn):
    try:
        conn.close()
    except:
        utils.debug(utils.debug_line(),"sockets",traceback.print_exc())
