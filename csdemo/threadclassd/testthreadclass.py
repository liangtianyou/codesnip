#-*- coding: utf-8 -*-

import time
import Queue
import threading

import utils
#-----------------------------------
#
#-----------------------------------
TESTTHREAD = None #设备监控报警线程
TIMEOUT = 60
#-----------------------------------
# start thread
#-----------------------------------
def start():
    global TESTTHREAD
    try:
        if TESTTHREAD and isinstance(TESTTHREAD, TestThread) and TESTTHREAD.isAlive():
            if not TESTTHREAD._TestThread__running.isSet():
                TESTTHREAD._TestThread__running.set()
                TESTTHREAD.start()
        else:
            TESTTHREAD = TestThread('TESTTHREAD')
            TESTTHREAD.start()
    except:
        utils.debug(utils.debug_line(),"testthreadclass")
#-----------------------------------
# stop thread
#-----------------------------------
def stop():
    global TESTTHREAD
    try:
        if TESTTHREAD and isinstance(TESTTHREAD, TestThread):
            if TESTTHREAD._TestThread__running.isSet():
                TESTTHREAD._TestThread__running.clear()
    except:
        utils.debug(utils.debug_line(),"testthreadclass")
#-----------------------------------
# 设备监控报警线程
#-----------------------------------
class TestThread(threading.Thread):
    def __init__ (self, threadname):
        try:
            threading.Thread.__init__(self, name=threadname)
            self.__running = threading.Event()
            self.__running.set()
        except:
            utils.debug(utils.debug_line(),"testthreadclass")

    def run(self):
        while self.__running.isSet():
            try:
                utils.debug(utils.debug_line(), "testthreadclass", "hello,python")
            except:
                utils.debug(utils.debug_line(),"testthreadclass")
            time.sleep(10)
