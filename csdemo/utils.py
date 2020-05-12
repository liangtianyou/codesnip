#-*- coding: utf-8 -*-
import os
import sys
import time
import traceback

import settings
   
debugfile = '/var/log/ODSP.log'

# 获取打印日志的行号
def debug_line():
    return traceback.extract_stack()[-2][1]

def debug(linenum, module, msg='', *args):
    if settings.DEBUG:
        if not os.path.isfile(debugfile):
            os.mknod(debugfile)
        logfd = None
        try:
            logfd = open(debugfile,'a')
        except:
            pass
        if logfd:
            logfd.write('%s %s [line:%s]: ' % (time.strftime("%Y-%m-%d %X"), module, linenum))
            if msg:
                if args:
                    args = [str(arg) for arg in args]
                logfd.write('%s %s\n' % (str(msg), ' '.join(args)))
            else:
                traceback.print_exc(file = logfd)
            logfd.flush()
            logfd.close()
