#-*- coding: utf-8 -*-

import os
import sys
import time
import socket

import utils 
#-----------------------------------
# 全局变量
#-----------------------------------
HTTPSOCK_PORT = 1980
TIMEOUT = 5
BUFFSIZE = 10240
#-----------------------------------
# 接收HTTP和网络指令
#-----------------------------------
class HttpSocket():
    def __init__(self):
        try:
            self.conn = ''
            self.address = ''
            self.httpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.httpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            while True:
                try:
                    self.httpsock.bind(('0.0.0.0',HTTPSOCK_PORT))
                    self.httpsock.listen(100)
                    break
                except Exception,e:
                    pass
                time.sleep(1)
        except:
            utils.debug(utils.debug_line(),"httpsocket")

    def Accept(self):
        try:
            self.conn,self.address = self.httpsock.accept()
            return self.conn,self.address
        except:
            utils.debug(utils.debug_line(),"httpsocket")
#-----------------------------------
# 接收HTTP发送过来的数据
#-----------------------------------
def httpsocket_send(conn,senddata = 'ok'):
    try:
        sendbuf = conn.sendall(senddata)
    except:
        utils.debug(utils.debug_line(),"httpsocket")
#-----------------------------------
# 将处理后的结果返回
#-----------------------------------
def httpsocket_recv(conn):
    readbuf = None
    try:
        conn.settimeout(TIMEOUT)
        readbuf = conn.recv(BUFFSIZE)
    except:
        readbuf = None
        utils.debug(utils.debug_line(),"httpsocket",'Recive data time out!')
    return readbuf
#-----------------------------------
# 关闭socket
#-----------------------------------
def httpsocket_close(conn):
    try:
        conn.close()
    except:
        utils.debug(utils.debug_line(),"httpsocket")
#-----------------------------------
# 接收HTTP和网络指令，受限
#-----------------------------------
class HttpCommunicateSocket():
    def __init__(self):
        self.connection = ''
        self.address = ''
        self.httpcommunicatesock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.httpcommunicatesock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while True:
            try:
                self.httpcommunicatesock.bind(('0.0.0.0', 1981))
                self.httpcommunicatesock.listen(20)
                break
            except Exception, e:
                utils.debug(utils.debug_line(), "httpsocket-httpcommunicatesock")
            time.sleep(1)

    def Accept(self):
        try:
            self.connection, self.address = self.httpcommunicatesock.accept()
            return self.connection, self.address
        except:
            utils.debug(utils.debug_line(), "httpsocket-httpcommunicatesock")
