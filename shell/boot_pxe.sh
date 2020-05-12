#!/bin/bash

# 网络启动
ipmitool -H 10.10.165.201 -U ADMIN -P ADMIN chassis bootdev pxe

# 光盘启动
ipmitool -H 10.10.108.74 -U ADMIN -P ADMIN chassis bootdev cdron

# 硬盘启动
ipmitool -H 10.10.108.74 -U ADMIN -P ADMIN chassis bootdev disk

# 重启执行
ipmitool -H 10.10.108.74 -U ADMIN -P ADMIN power reset
