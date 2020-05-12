#!/usr/bin/python
#-*- coding: utf-8 -*-
import os
import sys
from Queue import Queue
#-----------------------------------
# 重载编码
#-----------------------------------
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass
#-----------------------------------
# 当前目录加入sys.path
#-----------------------------------
currpath = os.path.join(os.getcwd(),os.path.dirname(__file__))
if currpath not in sys.path:
    sys.path.append(currpath)

import utils
import settings
import httpsocket
import threadclass
#-----------------------------------
#
#-----------------------------------
def main ():
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '-D':
            settings.DEBUG = True
        #启动线程
        threadclass.init_thread()
        #记录启动日志
        utils.debug(utils.debug_line(), "main", "system start success")
        #接收WEB请求
        sock = httpsocket.HttpSocket()
        while True:
            try:
                conn,addr = sock.Accept()
                workthread = threadclass.WorkThread(str(addr[1]), addr[0], conn)
                workthread.start()
            except:
                utils.debug(utils.debug_line(),"main")
    except:
        utils.debug(utils.debug_line(), "main")
#-----------------------------------
#
#-----------------------------------
if __name__ == '__main__':
    main()
