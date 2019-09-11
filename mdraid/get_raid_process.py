#-*- coding: utf-8 -*-
import os
import re

MDSTAT = '/proc/mdstat'
#-------------------------
# get raid process
#-------------------------
def get_raid_process():
    raidprocess = {}
    raiddevmatch = '^(md(\d+))\s+:\s+(active(\s+\(\S+\)\s+|\s+)raid(\d+)|inactive)\s+(.*)\s*$'
    raidprocessmatch = '(recovery|resync|reshape)'
    f = open(MDSTAT, 'r')
    result = f.readlines()
    f.close()
    reslen = len(result)
    i = 0
    while i < reslen:
        rdm = rpm = None
        rdm = re.match(raiddevmatch,result[i])
        if rdm:
            processline = result[i+2].strip()
            rpm = re.search(raidprocessmatch,processline)
            if rpm:
                raidname = rdm.group(1)
                raidid = int(rdm.group(2))
                raidstatu = rdm.group(3)
                raidlevel = rdm.group(5)
                if processline.find("%") >= 0:
                    #进度
                    rate = remaintime = speed = ''
                    tmp1,tmp2 = processline.split("%")
                    if tmp1.find("=") >= 0:
                        _,tmp1 = tmp1.rsplit("=",1)
                        rate = tmp1.strip()
                    #剩余时间
                    if tmp2.find("min") >= 0:
                        tmp2,tmp3 = tmp2.rsplit("min",1)
                        _,tmp2 = tmp2.rsplit("=",1)
                        remaintime = tmp2.strip()
                    #速度
                    sm = re.match('\s*\S+\s*=\s*(\S+)\s*',tmp3)
                    if sm:
                        speed = sm.group(1).strip()
                    raidprocess[raidid] = {
                        'name':raidname,
                        'rate':rate,
                        'remaintime':remaintime,
                        'speed': speed
                    }
            i += 2
        else:
            i += 1
    return raidprocess
    
if __name__ == '__main__':
    print get_raid_process()
