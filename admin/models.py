from django.db import models
from django.contrib.auth.models import User

class ClusterInfo(models.Model):
    name = models.CharField('集群名称', unique=True, max_length=50)
    tag = models.CharField('集群标记', unique=True, max_length=50)
    is_active = models.IntegerField('是否激活',default=0)
    pub_date = models.DateTimeField(auto_now_add=True) # 添加时间

class FileInfo(models.Model):
    path = models.CharField(max_length=200, null=False) #路径
    type = models.IntegerField(null=False) #类型 0文件夹 1文件
    name = models.CharField(max_length=100, null=False) #名称
    file_size =  models.CharField(max_length=10, null=True, default=0) #文件大小
    real_path = models.CharField(max_length=200, null=True) #真实路径
    real_name = models.CharField(max_length=100, null=True) #真实文件名
    file_type = models.CharField(max_length=5, null=True) #文件类型
    pub_date = models.DateTimeField(auto_now_add=True) # 添加时间
    owner = models.ForeignKey(User, on_delete=models.CASCADE) # 文件属主


class HostInfo(models.Model):
    hostname = models.CharField(max_length=100, unique=True) # 主机名
    sn = models.CharField(max_length=80) # SN序列号
    idrac_ip = models.GenericIPAddressField(max_length=15) # 远程管理卡IP
    host_ip = models.GenericIPAddressField(max_length=15) # 主机IP
    cluster_tag = models.CharField(max_length=20) # 所属集群标签
    
    cpu_nums = models.IntegerField(default=1) # cpu总数
    cpu_core = models.IntegerField(default=1) # cpu总数
    cpu_rate = models.FloatField(default=1) #单颗频率
    cpu_total_rate = models.CharField(max_length=50, null=True) # 主机CPU

    sd_nums = models.IntegerField(default=1) # 机槿硬盘数量
    sd_size = models.CharField(max_length=10, null=True) #机槿硬盘大小
    sd_total_size = models.CharField(max_length=10, null=True) #机槿硬盘总量
    
    ssd_nums = models.IntegerField(default=1) # 固态硬盘数量
    ssd_size = models.CharField(max_length=10, null=True) #固态硬盘大小
    ssd_total_size = models.CharField(max_length=50, null=True) # 固态硬盘总量

    dev_model = models.CharField(max_length=50, null=True) # 设备型号
    memory_nums = models.IntegerField(default=1)
    memory_size = models.IntegerField(default=1)
    memory_total_size = models.CharField(max_length=50) # 主机内存
    os = models.CharField(max_length=20) # 操作系统
    desc = models.TextField(null=True) # 备注
    buy_date = models.CharField("购买日期", max_length=50, null=True)
    end_svc_date = models.CharField("过保时间", max_length=50, null=True)
    svc_net_in = models.CharField("业务网络", max_length=50, null=True)
    idrac_net_in = models.CharField("远程管理卡网络", max_length=50, null=True)
    supply_name = models.CharField("供应商名称", max_length=50, null=True)
    supply_contact_name = models.CharField("供应商联系人", max_length=50, null=True)
    supply_phone = models.IntegerField("供应商联系号码", default=0)
    rack_num = models.CharField("机柜号", max_length=10, null=True)
    slot_num = models.CharField("槽位号", max_length=50, null=True)
    dc_name = models.CharField("机房名称", max_length=50, null=True)
    intention = models.CharField("用途", max_length=100, null=True)
    raid = models.CharField("raid", max_length=50, null=True)
    dev_status = models.IntegerField("设备状态", default=0) # 0开机 1关机   

    pub_date = models.DateTimeField(auto_now_add=True) # 添加时间


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
