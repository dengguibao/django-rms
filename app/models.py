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
    info = models.TextField(null=True) # 故障现象
    reason = models.TextField(null=True) # 故障原因
    resolv_method = models.TextField(null=True) # 解决方法
    repairer =  models.CharField(null=True,max_length=100) # 处理人
    prevent = models.TextField(null=True) # 预防措施
    owner = models.ForeignKey(User, on_delete=models.CASCADE) # 报告人
    pub_date = models.DateTimeField(auto_now=True) # 报告时间


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

    UPLOAD_DOC_TYPE = (
        (0,'文件夹'),
        (1,'文件')
    )

    path = models.CharField(max_length=200, null=False)  # 路径
    type = models.IntegerField(null=False, default=0, choices=UPLOAD_DOC_TYPE)  # 类型 0文件夹 1文件
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
    HOST_STATUS = (
        (0, '开机'),
        (1, '关机')
    )

    hostname = models.CharField(max_length=100, unique=True)  # 主机名
    sn = models.CharField(max_length=80)  # SN序列号
    idrac_ip = models.GenericIPAddressField()  # 远程管理卡IP
    host_ip = models.GenericIPAddressField()  # 主机IP
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
    svc_net_in = models.CharField("业务网络", max_length=100, null=True)
    idrac_net_in = models.CharField("远程管理卡网络", max_length=50, null=True)
    supply_name = models.CharField("供应商名称", max_length=50, null=True)
    supply_contact_name = models.CharField("供应商联系人", max_length=50, null=True)
    supply_phone = models.CharField("供应商联系号码",max_length=20, default=0)
    rack_num = models.CharField("机柜号", max_length=10, null=True)
    slot_num = models.CharField("槽位号", max_length=50, null=True)
    dc_name = models.CharField("机房名称", max_length=50, null=True)
    intention = models.CharField("用途", max_length=100, null=True)
    raid = models.CharField("raid", max_length=50, null=True)
    dev_status = models.IntegerField("设备状态", default=0, choices=HOST_STATUS)  # 0开机 1关机
    pub_date = models.DateTimeField(auto_now_add=True)  # 添加时间

    def __str__(self):
        return "主机名:{} ip:{} 集群:{} idrac ip:{}".format(
            self.hostname, self.host_ip, self.cluster_tag, self.idrac_ip
        )


class HostInterface(models.Model):
    host = models.ForeignKey(HostInfo,on_delete=models.CASCADE)
    ifname = models.CharField(max_length=100,null=False)
    access = models.CharField(max_length=100, null=False)


class VmInfo(models.Model):
    """virtual machine info

    Arguments:
        models {object} -- django Model
    """

    HOST_STATUS = (
        (0, '开机'),
        (1, '关机')
    )

    vm_hostname = models.CharField(max_length=100, )  # 主机名
    vm_intention = models.CharField(max_length=100, null=True)  # 用途
    vm_register = models.CharField(max_length=10, null=True)  # 申请人
    vm_monitor = models.CharField(max_length=5, null=True)  # zabbix监控
    vm_ip = models.GenericIPAddressField()  # 系统IP
    vlan_tag = models.CharField(max_length=30)  # vlan标签
    vlan_id = models.IntegerField()  # vlan id
    host = models.ForeignKey(HostInfo, on_delete=models.CASCADE)  # 宿主机外键
    vm_cpu = models.IntegerField(default=0)  # cpu
    vm_disk = models.IntegerField(default=0)  # 硬盘
    vm_memory = models.IntegerField(default=0)  # 内存
    vm_os = models.CharField(max_length=20)  # 操作系统
    vm_desc = models.TextField(null=True)  # 备注
    vm_status = models.IntegerField('虚拟机状态', default=0, choices=HOST_STATUS)  # 虚拟机状态 0开机 1关机
    pub_date = models.DateTimeField(auto_now_add=True)  # 添加时间

    def __str__(self):
        return "主机名:{} 申请人:{} IP:{} VLAN ID:{} VLAN标签:{} ".format(
            self.vm_hostname,
            self.vm_register,
            self.vm_ip,
            self.vlan_id,
            self.vlan_tag
        )


class Branch(models.Model):
    name = models.CharField(max_length=20)   # 分公司名称
    address = models.CharField(max_length=100)   # 分公司地址
    isenable = models.IntegerField(default=1, null=False) # 是否启用


class NetworkDevices(models.Model):
    hostname = models.CharField(max_length=50)   # 设备名称
    device_type = models.CharField(max_length=20)   # 设备类型
    brand = models.CharField(max_length=20)   # 设备品牌
    sn = models.CharField(max_length=50)   # 设备序列号
    device_model = models.CharField(max_length=50)   # 设备型号
    version = models.CharField(max_length=50)   # 软件版本号
    ip = models.CharField(max_length=20)   # 管理IP
    port_num = models.IntegerField(default=8, null=False) # 端口数量
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)   # 地区


class WanNetworks(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)   # 地区
    isp = models.CharField(max_length=20)   # 运营商
    ip = models.CharField(max_length=50)   # IP/掩码
    gateway = models.CharField(max_length=20)   # 网关
    bandwidth = models.CharField(max_length=10)   # 带宽
    rent = models.CharField(max_length=20)   # 付费方式/金额
    dns1 = models.CharField(max_length=20, null=True)   # dns1
    dns2 = models.CharField(max_length=20, null=True)   # dns2
    contact = models.CharField(max_length=50)   # 运营商联系人


class LanNetworks(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)   # 地区
    ip = models.CharField(max_length=50)   # IP/掩码
    gateway = models.CharField(max_length=20)   # 网关
    vlanid = models.IntegerField()  # vlan id
    function = models.CharField(max_length=20)   # 用途


class PortDesc(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)   # 地区
    device = models.ForeignKey(NetworkDevices, on_delete=models.CASCADE) # 设备ID
    index = models.CharField(max_length=50, null=False)  # 端口索引
    desc = models.CharField(max_length=200, null=True)  # 端口描述


class Monitor(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)   # 地区
    dev_model = models.CharField(max_length=20)   # 型号
    ip = models.CharField(max_length=20)   # IP
    camera_nums = models.IntegerField()   # 摄像头数量
    idle_channel = models.IntegerField()   # 剩余通道数
    hdd = models.IntegerField()   # 硬盘容量
    idle_slot = models.IntegerField()   # 剩余硬盘槽位
    storage = models.IntegerField()   # 存储时间是否满足3个月
    desc = models.TextField(null=True)   # 备注


class MonitorAccount(models.Model):
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE)   # 授权监控主机IP
    username = models.CharField(max_length=20)   # 授权账号
    password = models.CharField(max_length=20)   # 密码
    channel = models.CharField(max_length=50)   # 授权通道号
    desc = models.TextField(null=True)   # 授权描述
