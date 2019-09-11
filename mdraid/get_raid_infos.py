#-*- coding: utf-8 -*-
import os
import re
import sys
import traceback

MDSTAT = '/proc/mdstat'
RAIDSTATE = {
    0: 'ok',
    1: 'build',
    2: 'recovery',
    3: 'alert',
    4: 'error',
    5: 'reshape',
    6: 'check'
}
#---------------------------------
# 获取RAID详细信息
#---------------------------------
def get_raid_infos():
    raidinfos = {}
    raiddevmatch = '^(md(\d+))\s+:\s+(active(\s+\(\S+\)\s+|\s+)raid(\d+)|inactive)\s+(.*)\s*$'
    diskstates = {'F':'faildisks','S':'sparedisks','R':'workingdisks'}
    diskstatematch = '([a-z]+)\((\S+)\)\(*\S*\)*'
    raidprocessmatch = '(recovery|resync|reshape)'
    raidbitmapmatch = 'bitmap:'
    f = open(MDSTAT,'r')
    result = f.readlines()
    f.close()
    reslen = len(result)
    i = 0
    while i < reslen:
        rdm = re.match(raiddevmatch,result[i])
        if rdm:
            raidname = rdm.group(1)
            raiddev = '/dev/%s' % raidname
            raidid = int(rdm.group(2))
            raidstatus = rdm.group(3)
            raidlevel = rdm.group(5)
            raiddiskstr = re.sub('\[\d+\]','',rdm.group(6))
            raidbitmap = False
            raiddisknames = {
                'faildisks':[],
                'sparedisks':[],
                'workingdisks':[]
            }
            raiddisks = raiddiskstr.split()
            for raiddisk in raiddisks:
                dm = re.match(diskstatematch,raiddisk)
                if not dm is None:
                    raiddisknames[diskstates[dm.group(2)]].append(dm.group(1))
                else:
                    raiddisknames['workingdisks'].append(raiddisk)
                    
            raidsize = '0GiB'
            raidsizematch = '\s+(\d+)\s+blocks'
            sm = re.match(raidsizematch,result[i + 1])
            if sm:
                raidsize = '%sGiB' % str(round(float(sm.group(1)) / 1024 / 1024 ,2))
            rpm = re.search(raidprocessmatch,result[i + 2])
            rbm = None
            if rpm:
                rbm = re.search(raidbitmapmatch,result[i + 3])
            else:
                rbm = re.search(raidbitmapmatch,result[i + 2])
            if rbm:
                raidbitmap = True
            raidinfo = {
                'name':raidname,
                'device':raiddev,
                'level':raidlevel,
                'size':raidsize,
                'disks':raiddisknames,
                'bitmap':raidbitmap,
                'state':raidlevel and get_raid_state(raiddev,raidlevel) or 'error'
            }
            raidinfos[raidid] = raidinfo
        i += 1
    return raidinfos
# ------------------------------------
#
# ------------------------------------
def get_raid_state(raiddev, raidlevel):
    raidstate = 4
    if raidlevel in ['0','1','5','6']:
        raidname = raiddev.replace('/dev/', '')
        raidstate = eval("get_raid_state%s('%s')" % (raidlevel, raidname))
        if raidstate not in RAIDSTATE:
            raidstate = 4
    return RAIDSTATE[raidstate]
# ------------------------------------
#   check raid0 state
#   check failed disk from /proc/mdstat
#   command 'pvs' return result contain '/dev/md10: read failed ...Input/output error'
#   command 'mdadm -D /dev/md10' return result contain 'SCSI error' or 'does not appear to be active'
# ------------------------------------
def get_raid_state0(raidname):
    raidstate = 0
    try:
        raiddevmatch = '^%s\s+:\s+.*raid(\d+)\s+(.*)\s*$' % raidname
        faildiskmatch = '\(F\)'
        f = open(MDSTAT, 'r')
        result = f.readlines()
        f.close()
        reslen = len(result)
        i = 0
        while i < reslen:
            rdm = re.match(raiddevmatch, result[i])
            if rdm:
                faildisknum = len(re.findall(faildiskmatch, result[i]))
                if faildisknum > 0:
                    raidstate = 4
                    break
                break
            i += 1
        if raidstate > 0:
            return raidstate
        # check SCSI error
        retcode, proc = utils.cust_popen([settings.MDADM, '-D', raiddev])
        if retcode == 0:
            result = proc.stdout.readlines()
            for line in result:
                if re.search('SCSI error', line) or re.search('does not appear to be active', line):
                    raidstate = 4
                    break
        else:
            return
        if raidstate > 0:
            return raidstate
        # check pvs error
        retcode, proc = utils.timer("%s -s" % settings.PVSCAN, 1)
        result = proc.stdout.readlines()
        result.extend(proc.stderr.readlines())
        for line in result:
            if re.search(raiddev, line) and re.search('Input/output error', line):
                raidstate = 4
                break
    except:
        print >> sys.stderr, traceback.extract_stack()[-2][1], traceback.format_exc()
    return raidstate
# --------------------------
# raid1 state
# --------------------------
def get_raid_state1(raidname):
    raidstate = 4
    try:
        raiddevmatch = '^%s\s+:\s+.*raid(\d+)\s+(.*)\s*$' % raidname
        diskstatematch = '([a-z]+)\((\S+)\)\(*\S*\)*'
        f = open(MDSTAT, 'r')
        result = f.readlines()
        f.close()
        reslen = len(result)
        i = 0
        while i < reslen:
            rdm = re.match(raiddevmatch, result[i])
            if rdm:
                faildisknum = result[i + 1].count('_')
                raiddiskstr = re.sub('\[\d+\]', '', rdm.group(2))
                raiddisks = raiddiskstr.split()

                if faildisknum == 0:
                    if re.search("resync", result[i + 2]):
                        raidstate = 1
                        break
                    elif re.search("reshape", result[i + 2]):
                        raidstate = 5
                        break
                    elif re.search("check", result[i + 2]):
                        raidstate = 6
                        break
                    else:
                        raidstate = 0
                        break
                elif faildisknum == 1:
                    if re.search('recovery', result[i + 2]):
                        raidstate = 2
                        break
                    else:
                        raidstate = 3
                        break
                else:
                    raidstate = 4
                    break
                break
            i += 1
    except:
        print >> sys.stderr, traceback.extract_stack()[-2][1], traceback.format_exc()
    return raidstate
# ---------------------------
# raid5 state
# ---------------------------
def get_raid_state5(raidname):
    raidstate = 4
    try:
        raiddevmatch = '^%s\s+:\s+.*raid(\d+)\s+(.*)\s*$' % raidname
        f = open(MDSTAT, 'r')
        result = f.readlines()
        f.close()
        reslen = len(result)
        i = 0
        while i < reslen:
            rdm = re.match(raiddevmatch, result[i])
            if rdm:
                faildisknum = result[i + 1].count('_')
                faildisknum += result[i].count('_')
                diskstatematch = '([a-z]+)\((\S+)\)\(*\S*\)*'
                raiddiskstr = re.sub('\[\d+\]', '', rdm.group(2))
                raiddisks = raiddiskstr.split()
                if faildisknum == 0:
                    if re.search("resync", result[i + 2]):
                        raidstate = 1
                        break
                    elif re.search("reshape", result[i + 2]):
                        raidstate = 5
                        break
                    elif re.search("check", result[i + 2]):
                        raidstate = 6
                        break
                    else:
                        raidstate = 0
                        break
                elif faildisknum > 1:
                    raidstate = 4
                    break
                else:
                    if re.search('recovery', result[i + 2]):
                        raidstate = 2
                        break
                    elif re.search("reshape", result[i + 2]):
                        raidstate = 5
                        break
                    else:
                        raidstate = 3
                        break
                break
            i += 1
    except:
        print >> sys.stderr, traceback.extract_stack()[-2][1], traceback.format_exc()
    return raidstate
# -----------------------------
# raid6 state
# -----------------------------
def get_raid_state6(raidname):
    raidstate = 4
    try:
        raiddevmatch = '^%s\s+:\s+.*raid(\d+)\s+(.*)\s*$' % raidname
        f = open(MDSTAT, 'r')
        result = f.readlines()
        f.close()
        reslen = len(result)
        i = 0
        while i < reslen:
            rdm = re.match(raiddevmatch, result[i])
            if rdm:
                faildisknum = result[i + 1].count('_')
                sparedisknum = 0
                diskstatematch = '([a-z]+)\((\S+)\)\(*\S*\)*'
                raiddiskstr = re.sub('\[\d+\]', '', rdm.group(1))
                raiddisks = raiddiskstr.split()

                if faildisknum == 0:
                    if re.search("resync", result[i + 2]):
                        raidstate = 1
                        break
                    elif re.search("reshape", result[i + 2]):
                        raidstate = 5
                        break
                    elif re.search("check", result[i + 2]):
                        raidstate = 6
                        break
                    else:
                        raidstate = 0
                        break
                elif faildisknum > 2:
                    raidstate = 4
                    break
                else:
                    if re.search('recovery', result[i + 2]):
                        raidstate = 2
                        break
                    elif re.search("resync", result[i + 2]):
                        raidstate = 1
                        break
                    else:
                        raidstate = 3
                        break
                break
            i += 1
    except:
        print >> sys.stderr, traceback.extract_stack()[-2][1], traceback.format_exc()
    return raidstate

if __name__ == '__main__':
    raidinfos = get_raid_infos()
    for raidid,raidinfo in raidinfos.iteritems():
        print "%s:" % raidid
        print '-----'
        for key,value in raidinfo.iteritems():
            print "%s: %s" % (key.rjust(10,' '), value)
        print '---------------------------------------'
