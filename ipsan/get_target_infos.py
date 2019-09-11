#-*- coding: utf-8 -*-
import os
import re
import sys
import platform
import traceback
import subprocess

ISCSI_SCST = '/etc/init.d/iscsi-scst'
SCSTADMIN = 'scstadmin'
CAT = 'cat'

IPSAN_DRIVER = 'iscsi'
IPSAN_HANDLER = 'vdisk_blockio'
TARGET_PATH = '/sys/kernel/scst_tgt/targets/iscsi/'
TARGET_DEVICE_PATH = '/sys/kernel/scst_tgt/devices/'
DEFAULT_DIR_ITEMS = ['mgmt']
#----------------------------------------
# user defined execute command
#----------------------------------------
def cust_popen(cmd, no_wait=False, close_fds=True):
    proc = None
    retcode = None
    try:
        if close_fds:
            if type(cmd) == list:
                proc = subprocess.Popen(cmd,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=close_fds)
            else:
                proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=close_fds)
        else:
            proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if not no_wait:
            retcode = proc.wait()
    except Exception,e:
        print >> sys.stderr, traceback.extract_stack()[-2][1], traceback.format_exc()
    return retcode,proc
#---------------------------------
# 获取所有的target名称
#---------------------------------
def get_ipsan_target_names():
    target_names = []
    try:
        retcode,proc = cust_popen([SCSTADMIN,'-list_target','-driver',IPSAN_DRIVER,'-noprompt'])
        result = proc.stdout.read().strip()
        patters = re.compile('.*?iscsi\s+(.*?)All\s+done.*?',re.S)
        matched_targets = re.findall(patters,result)
        for targetstr in matched_targets:
            target_names.extend(targetstr.split())
    except:
        print >> sys.stderr, traceback.extract_stack()[-2][1], traceback.format_exc()
    return target_names
#---------------------------------
# get iscsi target
#---------------------------------
def get_targets_from_runtime():
    targets = []
    try:
        target_names = get_ipsan_target_names()
        for target_name in target_names:
            target_info = {
                'name':target_name,
                'devices':[],
                'groups':[]
            }
            #设备
            devices = []
            target_luns_path = os.path.join(TARGET_PATH,target_name,'luns')
            if os.path.exists(target_luns_path):
                items = os.listdir(target_luns_path)
                for item in items:
                    if item not in DEFAULT_DIR_ITEMS:
                        item_path = os.path.join(target_luns_path,item)
                        item_device_path = os.path.join(item_path,'device')
                        if os.path.islink(item_device_path):
                            item_device_real_path = os.readlink(item_device_path)
                            device_name = os.path.split(item_device_real_path)[1]
                            retcode,proc = cust_popen([CAT,os.path.join(item_device_path,'filename')])
                            device_path = proc.stdout.readlines()[0].strip()
                            retcode,proc = cust_popen([CAT,os.path.join(item_device_path,'size_mb')])
                            device_size = proc.stdout.read().strip()
                            device = {
                                'lun':item,
                                'name':device_name,
                                'path':device_path,
                                'size':device_size
                            }
                            devices.append(device)
            target_info['devices'] = devices
            #组
            groups = []
            target_groups_path = os.path.join(TARGET_PATH,target_name,'ini_groups')
            if os.path.exists(target_groups_path):
                group_items = os.listdir(target_groups_path)
                for item in group_items:                
                    if item not in DEFAULT_DIR_ITEMS:
                        group = {
                            'group':item,
                            'devices':[],
                            'initiators':[]
                        }
                        group_item_path = os.path.join(target_groups_path,item)
                        group_item_luns_path = os.path.join(group_item_path,'luns')
                        group_devices = []
                        if os.path.exists(group_item_luns_path):
                            group_lun_items = os.listdir(group_item_luns_path)
                            for lun_item in group_lun_items:
                                if lun_item not in DEFAULT_DIR_ITEMS:
                                    group_lun_path = os.path.join(group_item_luns_path,lun_item)
                                    group_lun_device_path = os.path.join(group_lun_path,'device')
                                    if os.path.islink(group_lun_device_path):
                                        group_lun_device_real_path = os.readlink(group_lun_device_path)
                                        device_name = os.path.split(group_lun_device_real_path)[1]
                                        retcode,proc = cust_popen([CAT,os.path.join(group_lun_device_path,'filename')])
                                        device_path = proc.stdout.readlines()[0].strip()
                                        retcode,proc = cust_popen([CAT,os.path.join(group_lun_device_path,'size_mb')])
                                        device_size = proc.stdout.read().strip()
                                        group_device = {
                                            'lun':item,
                                            'name':device_name,
                                            'path':device_path,
                                            'size':device_size
                                        }
                                        group_devices.append(group_device)
                        group['devices'] = group_devices
                        #group initiator
                        group_item_initiators_path = os.path.join(group_item_path,'initiators')
                        group_initiators = []
                        if os.path.exists(group_item_initiators_path):
                            group_initiator_items = os.listdir(group_item_initiators_path)
                            for initiator_item in group_initiator_items:
                                if initiator_item not in DEFAULT_DIR_ITEMS:
                                    group_initiators.append(initiator_item)
                        group['initiators'] = group_initiators
                        groups.append(group)
            target_info['groups'] = groups
            targets.append(target_info)
    except:
        print >> sys.stderr, traceback.extract_stack()[-2][1], traceback.format_exc()
    return targets

if __name__ == '__main__':
    targetinfos = get_targets_from_runtime()
    for targetinfo in targetinfos:
        for key,value in targetinfo.iteritems():
            print '%s: %s' % (key.rjust(10,' '),value)
