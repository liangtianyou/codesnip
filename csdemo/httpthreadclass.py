#-*- coding: utf-8 -*-

import json
import time
import threading

import utils
import httpsocket
import dataprocess
#-----------------------------------
#
#-----------------------------------
HTTPTHREAD = None #WEB访问分发线程
#-----------------------------------
# start thread
#-----------------------------------
def start():
    global HTTPTHREAD
    try:
        if HTTPTHREAD and isinstance(HTTPTHREAD, HttpThread) and HTTPTHREAD.isAlive():
            if not HTTPTHREAD._HttpThread__running.isSet():
                HTTPTHREAD._HttpThread__running.set()
                HTTPTHREAD.start()
        else:
            HTTPTHREAD = HttpThread('HTTPTHREAD')
            HTTPTHREAD.start()
    except:
        utils.debug(utils.debug_line(),"httpthreadclass")
#-----------------------------------
# stop thread
#-----------------------------------
def stop():
    global HTTPTHREAD
    try:
        if HTTPTHREAD and isinstance(HTTPTHREAD,HttpThread):
            if HTTPTHREAD._HttpThread__running.isSet():
                HTTPTHREAD._HttpThread__running.clear()
    except:
        utils.debug(utils.debug_line(),"httpthreadclass")
#-----------------------------------
# WEB页面访问接收线程
#-----------------------------------
class HttpThread(threading.Thread):
    def __init__ (self,threadname):
        try:
            threading.Thread.__init__(self, name=threadname)
            self.sock = httpsocket.HttpSocket()
            self.__running = threading.Event()
            self.__running.set()
        except:
            utils.debug(utils.debug_line(),"httpthreadclass")

    def run(self):
        while self.__running.isSet():
            try:
                conn,addr = self.sock.Accept()
                workthread = WorkThread(str(addr[1]),addr[0],conn)
                workthread.start()
            except:
                utils.debug(utils.debug_line(),"httpthreadclass")
            time.sleep(.1)
#-----------------------------------
# WEB页面访问分发线程
#-----------------------------------
class WorkThread(threading.Thread):
    def __init__ (self, threadname, ip, conn):
        try:
            threading.Thread.__init__(self, name = threadname)
            self._ip = ip
            self._conn = conn
        except:
            utils.debug(utils.debug_line(),"httpthreadclass")

    def run (self):
        rtndata = json.dumps({'state':'1','result':'9998'}) #数据传输失败
        try:
            cmddata = httpsocket.httpsocket_recv(self._conn)
            if cmddata:
                cmd = json.loads(cmddata)
                if 'params' in cmd:
                    cmd['params']['_ip'] = self._ip
                rtndata = dataprocess.http_dataprocess(cmd)
                sockets.Senddata(self._conn,rtndata)
        except:
            utils.debug(utils.debug_line(),"httpthreadclass")
        finally:
            httpsocket.httpsocket_close(self._conn)
