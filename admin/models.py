from django.db import models
from django.contrib.auth.models import User

class FileInfo(models.Model):
    path = models.CharField(max_length=200, null=False) #路径
    type = models.IntegerField(null=False) #类型 0文件夹 1文件
    name = models.CharField(max_length=100, null=False) #名称
    #file_size =  models.IntegerField(null=True, default=0) #文件大小
    real_path = models.CharField(max_length=200, null=True) #真实路径
    real_name = models.CharField(max_length=100, null=True) #真实文件名
    file_type = models.CharField(max_length=5, null=True) #文件类型
    pub_date = models.DateTimeField(auto_now_add=True) # 添加时间
    owner = models.ForeignKey(User, on_delete=models.CASCADE) # 文件属主


class HostInfo(models.Model):
    '''hostinfo db table model'''
    hostname = models.CharField(max_length=100, unique=True) # 主机名
    sn = models.CharField(max_length=80) # SN序列号
    idrc_ip = models.GenericIPAddressField(max_length=15) # 远程管理卡IP
    host_ip = models.GenericIPAddressField(max_length=15) # 主机IP
    cluster_tag = models.CharField(max_length=20) # 所属集群标签
    cpu = models.CharField(max_length=50, null=True) # 主机CPU
    disk = models.CharField(max_length=50, null=True) # 主机硬盘
    dev_model = models.CharField(max_length=50, null=True) # 设备型号
    memory = models.CharField(max_length=50) # 主机内存
    os = models.CharField(max_length=20) # 操作系统
    desc = models.TextField(null=True) # 备注
    pub_date = models.DateTimeField(auto_now_add=True) # 添加时间

    def __str__(self):
        return self.hostname


class VmInfo(models.Model):
    '''vminfo（virtual machine） db table model'''
    vm_hostname = models.CharField(max_length=100,) # 主机名
    vm_intention = models.CharField(max_length=100, null=True) # 用途
    vm_register = models.CharField(max_length=10, null=True) # 申请人
    vm_monitor = models.CharField(max_length=5, null=True) # zabbix监控
    vm_ip = models.GenericIPAddressField(max_length=15)# 系统IP
    vlan_tag = models.CharField(max_length=30) # vlan标签
    vlan_id = models.IntegerField() # vlan id
    host = models.ForeignKey(HostInfo, on_delete=models.CASCADE) # 宿主机外键
    vm_cpu = models.CharField(max_length=10) # cpu
    vm_disk = models.CharField(max_length=10, null=True) # 硬盘
    vm_memory = models.CharField(max_length=10) # 内存
    vm_os = models.CharField(max_length=20) # 操作系统
    vm_desc = models.TextField(null=True) # 备注
    pub_date = models.DateTimeField(auto_now_add=True) # 添加时间

    def __str__(self):
        return self.vm_hostname
