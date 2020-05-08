from django.db import models
from django.contrib.auth.models import User

class DailyReport(models.Model):
    """daily report

    Arguments:
        models {object} -- django Model
    """
    content = models.TextField(null=False, verbose_name='工作内容')
    type = models.CharField(null=False, max_length=10, verbose_name='工作类别')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateField(null=False, auto_now=True)

    def __str__(self):
        return '%s %s'% (self.owner.first_name, self.type)


class TroubleReport(models.Model):
    """trouble report

    Arguments:
        models {object} -- django Model
    """
    desc = models.CharField(verbose_name="故障说明", null=False, max_length=80)
    type = models.CharField(verbose_name="故障类别", null=False, max_length=20)
    start_date = models.DateTimeField(null=False, verbose_name="开始时间")
    end_date = models.DateTimeField(null=True, verbose_name="结束时间")
    device = models.CharField(verbose_name="故障设备", null=True, max_length=100)
    info = models.TextField(null=True)
    reason = models.TextField(null=True)
    resolv_method = models.TextField(null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now=True)


class ClusterInfo(models.Model):
    """esxi cluster info

    Arguments:
        models {object} -- django Model
    """
    name = models.CharField('集群名称', unique=True, max_length=50)
    tag = models.CharField('集群标记', unique=True, max_length=50)
    is_active = models.IntegerField('是否激活', default=0)
    pub_date = models.DateTimeField(auto_now_add=True)  # 添加时间

    def __str__(self):
        return "集群名称:{} 集群标记:{}".format(self.name, self.tag)


class FileInfo(models.Model):
    """user upload file info

    Arguments:
        models {object} -- django Model
    """
    path = models.CharField(max_length=200, null=False)  # 路径
    type = models.IntegerField(null=False)  # 类型 0文件夹 1文件
    name = models.CharField(max_length=100, null=False)  # 名称
    file_size = models.CharField(max_length=10, null=True, default=0)  # 文件大小
    real_path = models.CharField(max_length=200, null=True)  # 真实路径
    real_name = models.CharField(max_length=100, null=True)  # 真实文件名
    file_type = models.CharField(max_length=5, null=True)  # 文件类型
    pub_date = models.DateTimeField(auto_now_add=True)  # 添加时间
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # 文件属主

    def __str__(self):
        return "name:{} type:{},".format(self.name, self.type)


class HostInfo(models.Model):
    """host info

    Arguments:
        models {object} -- django Model
    """
    hostname = models.CharField(max_length=100, unique=True)  # 主机名
    sn = models.CharField(max_length=80)  # SN序列号
    idrac_ip = models.GenericIPAddressField(max_length=15)  # 远程管理卡IP
    host_ip = models.GenericIPAddressField(max_length=15)  # 主机IP
    cluster_tag = models.CharField(max_length=20)  # 所属集群标签
    cpu_nums = models.IntegerField(default=0)  # cpu总数
    cpu_core = models.IntegerField(default=0)  # cpu总数
    cpu_rate = models.FloatField(default=0)  # 单颗频率
    cpu_total_rate = models.FloatField(default=0)  # 主机CPU
    sd_nums = models.IntegerField(default=0)  # 机槿硬盘数量
    sd_size = models.FloatField(default=0)  # 机槿硬盘大小
    sd_total_size = models.FloatField(default=0)  # 机槿硬盘总量
    ssd_nums = models.IntegerField(default=0)  # 固态硬盘数量
    ssd_size = models.FloatField(default=0)  # 固态硬盘大小
    ssd_total_size = models.FloatField(default=0)  # 固态硬盘总量
    dev_model = models.CharField(max_length=50, null=True)  # 设备型号
    memory_nums = models.IntegerField(default=0)
    memory_size = models.IntegerField(default=0)
    memory_total_size = models.IntegerField(default=0)  # 主机内存
    os = models.CharField(max_length=20)  # 操作系统
    desc = models.TextField(null=True)  # 备注
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
    dev_status = models.IntegerField("设备状态", default=0)  # 0开机 1关机
    pub_date = models.DateTimeField(auto_now_add=True)  # 添加时间

    def __str__(self):
        return "主机名:{} ip:{} 集群:{} idrac ip:{} " \
               "CPU颗数:{} CPU频率:{} CPU核心数:{} CPU总频率:{} " \
               "内存数量:{} 内存容量:{} 内存总容量:{} " \
               "SSD数量:{} SSD容量:{} SSD总容量:{} " \
               "硬盘数量:{} 硬盘容量:{} 硬盘总容量:{} " \
               "设备状态:{} 描述:{} 操作系统:{}".format(
            self.hostname, self.host_ip, self.cluster_tag, self.idrac_ip,
            self.cpu_nums, self.cpu_rate, self.cpu_core, self.cpu_total_rate,
            self.memory_nums, self.memory_size, self.memory_total_size,
            self.ssd_nums, self.ssd_size, self.ssd_total_size,
            self.sd_nums, self.sd_size, self.sd_total_size,
            '开机' if self.dev_status == 0 else '关机', self.desc, self.os
        )


class VmInfo(models.Model):
    """virtual machine info

    Arguments:
        models {object} -- django Model
    """
    vm_hostname = models.CharField(max_length=100, )  # 主机名
    vm_intention = models.CharField(max_length=100, null=True)  # 用途
    vm_register = models.CharField(max_length=10, null=True)  # 申请人
    vm_monitor = models.CharField(max_length=5, null=True)  # zabbix监控
    vm_ip = models.GenericIPAddressField(max_length=15)  # 系统IP
    vlan_tag = models.CharField(max_length=30)  # vlan标签
    vlan_id = models.IntegerField()  # vlan id
    host = models.ForeignKey(HostInfo, on_delete=models.CASCADE)  # 宿主机外键
    vm_cpu = models.IntegerField(default=0)  # cpu
    vm_disk = models.IntegerField(default=0)  # 硬盘
    vm_memory = models.IntegerField(default=0)  # 内存
    vm_os = models.CharField(max_length=20)  # 操作系统
    vm_desc = models.TextField(null=True)  # 备注
    vm_status = models.IntegerField('虚拟机状态', default=0)  # 虚拟机状态 0开机 1关机
    pub_date = models.DateTimeField(auto_now_add=True)  # 添加时间

    def __str__(self):
        return "主机名:{} 申请人:{} 用途:{} ZABBIX监控:{} IP:{} VLAN ID:{} VLAN标签:{} " \
               "宿主机:{} CPU:{} 磁盘:{} 内存:{} 操作系统:{} 状态:{} 备注:{}".format(
            self.vm_hostname,
            self.vm_register,
            self.vm_intention,
            self.vm_monitor,
            self.vm_ip,
            self.vlan_id,
            self.vlan_tag,
            self.host.hostname,
            self.vm_cpu,
            self.vm_disk,
            self.vm_memory,
            self.vm_os,
            '开机' if self.vm_status == 0 else '关机',
            self.vm_desc
        )
