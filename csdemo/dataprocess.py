#-*- coding: utf-8 -*-
import json

import utils

def http_dataprocess(command):
    try:
        utils.debug(utils.debug_line(),"dataprocess",command)
        return json.dumps({'state':'0'})     
    except:
        utils.debug(utils.debug_line(),"dataprocess")
