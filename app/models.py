from django.db import models
from django.contrib.auth.models import User


class BankPrivate(models.Model):
    IS_PROXY = (
        ('y', 'Yes'),
        ('n', 'No')
    )

    IS_ACTIVE = (
        ('y', 'Yes'),
        ('n', 'No'),
    )

    name = models.CharField(verbose_name="业务名称", max_length=50, null=False)
    access_type = models.CharField(verbose_name="访问方式", max_length=10, null=False)
    require_authorize_addr = models.TextField(verbose_name="银行要求授权", null=False)
    real_authorize_addr = models.TextField(verbose_name="实际授权", null=False)
    is_proxy = models.CharField(verbose_name="是否代理", max_length=1, choices=IS_PROXY)
    firewall_policy_name = models.CharField(verbose_name="防火墙策略", null=False, max_length=50)
    nat_src_addr_pool = models.TextField(verbose_name="NAT源地址池", null=False)
    nat_dest_addr_pool = models.TextField(verbose_name="NAT目标地址池")
    int_behave_control_policy = models.TextField(verbose_name='上网行为控制策略')
    int_behave_audit_policy = models.TextField(verbose_name="上网行为审计策略")
    global_ip = models.TextField(verbose_name="公网IP")
    service_leader = models.CharField(verbose_name="业务对接人", max_length=10, null=False)
    user_ip_addr = models.TextField(verbose_name="授权电脑IP")
    user_permission = models.TextField(verbose_name="授权说明")
    desc = models.TextField(verbose_name="描述")
    is_active = models.CharField(verbose_name="状态", max_length=1, null=False, choices=IS_ACTIVE)
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now=True)

    def __str__(self):
        return '%s' % self.name


class DailyReport(models.Model):
    """daily report

    Arguments:
        models {object} -- django Model
    """
    content = models.TextField(null=False, verbose_name='工作内容')
    type = models.CharField(null=False, max_length=10, verbose_name='工作类别')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateField(verbose_name="发布时间", null=False, auto_now=True)

    def __str__(self):
        return '%s %s' % (self.owner.first_name, self.type)


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
    info = models.TextField(verbose_name="故障现象", null=True)  # 故障现象
    reason = models.TextField(verbose_name="故障原因", null=True)  # 故障原因
    resolv_method = models.TextField(verbose_name="解决办法", null=True)  # 解决方法
    repairer = models.CharField(verbose_name="处理人", null=True, max_length=100)  # 处理人
    prevent = models.TextField(verbose_name="预防措施", null=True)  # 预防措施
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # 报告人
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now=True)  # 报告时间


class ClusterInfo(models.Model):
    """esxi cluster info

    Arguments:
        models {object} -- django Model
    """
    IS_VIRT = (
        (0, '普通服务器'),
        (1, '虚拟化集群')
    )
    IS_ACTIVE = (
        (0, '启用'),
        (1, '禁用')
    )
    name = models.CharField(verbose_name="集群名称", unique=True, max_length=50)
    tag = models.CharField(verbose_name="集群标记", unique=True, max_length=50)
    is_active = models.IntegerField(verbose_name="状态", choices=IS_ACTIVE, default=0)
    is_virt = models.IntegerField(verbose_name="类别", choices=IS_VIRT, default=0, null=False)
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)  # 添加时间

    def __str__(self):
        return "集群名称:{} 集群标记:{}".format(self.name, self.tag)


class FileInfo(models.Model):
    """user upload file info

    Arguments:
        models {object} -- django Model
    """

    UPLOAD_DOC_TYPE = (
        (0, '文件夹'),
        (1, '文件')
    )

    path = models.CharField(verbose_name="文件路径", max_length=200, null=False)  # 路径
    type = models.IntegerField(verbose_name="文件类型", null=False, default=0, choices=UPLOAD_DOC_TYPE)  # 类型 0文件夹 1文件
    name = models.CharField(verbose_name="文件名称", max_length=100, null=False)  # 名称
    file_size = models.CharField(verbose_name="文件大小", max_length=10, null=True, default=0)  # 文件大小
    real_path = models.CharField(verbose_name="存储路径", max_length=200, null=True)  # 真实路径
    real_name = models.CharField(verbose_name="存储名称", max_length=100, null=True)  # 真实文件名
    file_type = models.CharField(verbose_name="文件类型", max_length=5, null=True)  # 文件类型
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)  # 添加时间
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

    hostname = models.CharField(verbose_name="主机名", max_length=100, unique=True)  # 主机名
    sn = models.CharField(verbose_name="序列号", max_length=80)  # SN序列号
    idrac_ip = models.GenericIPAddressField(verbose_name="iDRAC IP")  # 远程管理卡IP
    host_ip = models.GenericIPAddressField(verbose_name="主机IP")  # 主机IP
    cluster_tag = models.ForeignKey(ClusterInfo, on_delete=models.CASCADE, to_field="tag", null=True, blank=True)  # 所属集群标签
    cpu_nums = models.IntegerField(verbose_name="CPU数量", default=0)  # cpu总数
    cpu_core = models.IntegerField(verbose_name="CPU总数", default=0)  # cpu总数
    cpu_rate = models.FloatField(verbose_name="CPU频率", default=0)  # 单颗频率
    cpu_total_rate = models.FloatField(verbose_name="CPU总数量", default=0)  # 主机CPU
    sd_nums = models.IntegerField(verbose_name="机槿硬盘数量", default=0)  # 机槿硬盘数量
    sd_size = models.FloatField(verbose_name="机械硬盘大小", default=0)  # 机槿硬盘大小
    sd_total_size = models.FloatField(verbose_name="机槿硬盘总量", default=0)  # 机槿硬盘总量
    ssd_nums = models.IntegerField(verbose_name="SSD数量", default=0)  # 固态硬盘数量
    ssd_size = models.FloatField(verbose_name="SSD大小", default=0)  # 固态硬盘大小
    ssd_total_size = models.FloatField(verbose_name="SSD总量", default=0)  # 固态硬盘总量
    dev_model = models.CharField(verbose_name="设备型号", max_length=50, null=True)  # 设备型号
    memory_nums = models.IntegerField(verbose_name="内存数量", default=0)
    memory_size = models.IntegerField(verbose_name="内存容量", default=0)
    memory_total_size = models.IntegerField(verbose_name="内存总容量", default=0)  # 主机内存
    os = models.CharField(verbose_name="操作系统", max_length=20)  # 操作系统
    desc = models.TextField(verbose_name="备注", null=True)  # 备注
    buy_date = models.CharField(verbose_name="购买日期", max_length=50, null=True)
    end_svc_date = models.CharField(verbose_name="过保日期", max_length=50, null=True)
    svc_net_in = models.CharField(verbose_name="业务接入", max_length=100, null=True)
    idrac_net_in = models.CharField(verbose_name="iDRAC接入", max_length=50, null=True)
    supply_name = models.CharField(verbose_name="供应商名称", max_length=50, null=True)
    supply_contact_name = models.CharField(verbose_name="供应商联系人", max_length=50, null=True)
    supply_phone = models.CharField(verbose_name="供应商号码", max_length=20, default=0)
    rack_num = models.CharField(verbose_name="机架号", max_length=10, null=True)
    slot_num = models.CharField(verbose_name="槽位号", max_length=50, null=True)
    dc_name = models.CharField(verbose_name="机房名称", max_length=50, null=True)
    intention = models.CharField(verbose_name="用途", max_length=100, null=True)
    raid = models.CharField(verbose_name="RAID级别", max_length=50, null=True)
    dev_status = models.IntegerField(verbose_name="状态", default=0, choices=HOST_STATUS)  # 0开机 1关机
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)  # 添加时间

    def __str__(self):
        return "主机名:{} ip:{} 集群:{} idrac ip:{}".format(
            self.hostname, self.host_ip, self.cluster_tag, self.idrac_ip
        )


class HostInterface(models.Model):
    host = models.ForeignKey(HostInfo, on_delete=models.CASCADE)
    ifname = models.CharField(verbose_name="接口序号", max_length=100, null=False)
    access = models.CharField(verbose_name="接口描述", max_length=100, null=False)


class VmInfo(models.Model):
    """virtual machine info

    Arguments:
        models {object} -- django Model
    """

    HOST_STATUS = (
        (0, '开机'),
        (1, '关机')
    )

    vm_hostname = models.CharField(verbose_name="主机名", max_length=100, )  # 主机名
    vm_intention = models.CharField(verbose_name="用途", max_length=100, null=True)  # 用途
    vm_register = models.CharField(verbose_name="申请人", max_length=10, null=True)  # 申请人
    vm_monitor = models.CharField(verbose_name="zabbix监控", max_length=5, null=True)  # zabbix监控
    vm_ip = models.GenericIPAddressField(verbose_name="IP地址",)  # 系统IP
    vlan_tag = models.CharField(verbose_name="vlan标签", max_length=30)  # vlan标签
    vlan_id = models.IntegerField(verbose_name="vlan号",)  # vlan id
    host = models.ForeignKey(HostInfo, verbose_name="宿主机", on_delete=models.CASCADE)  # 宿主机外键
    vm_cpu = models.IntegerField(verbose_name="CPU", default=0)  # cpu
    vm_disk = models.IntegerField(verbose_name="硬盘", default=0)  # 硬盘
    vm_memory = models.IntegerField(verbose_name="内存", default=0)  # 内存
    vm_os = models.CharField(verbose_name="操作系统", max_length=20)  # 操作系统
    vm_desc = models.TextField(verbose_name="备注", null=True)  # 备注
    vm_status = models.IntegerField(verbose_name="状态", default=0, choices=HOST_STATUS)  # 虚拟机状态 0开机 1关机
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)  # 添加时间

    def __str__(self):
        return "主机名:{} 申请人:{} IP:{} VLAN ID:{} VLAN标签:{} ".format(
            self.vm_hostname,
            self.vm_register,
            self.vm_ip,
            self.vlan_id,
            self.vlan_tag
        )


class Branch(models.Model):
    IS_ENABLE = (
        (0, '停用'),
        (1, '启用')
    )
    name = models.CharField(verbose_name="名称", max_length=20)  # 分公司名称
    address = models.CharField(verbose_name="公司地址", max_length=100)  # 分公司地址
    isenable = models.IntegerField(verbose_name="状态", default=1, choices=IS_ENABLE, null=False)  # 是否启用


class NetworkDevices(models.Model):
    hostname = models.CharField(verbose_name="主机名", max_length=50)  # 设备名称
    device_type = models.CharField(verbose_name="设备类型", max_length=20)  # 设备类型
    brand = models.CharField(verbose_name="设备品牌", max_length=20)  # 设备品牌
    sn = models.CharField(verbose_name="设备序号", max_length=50)  # 设备序列号
    device_model = models.CharField(verbose_name="设备型号", max_length=50)  # 设备型号
    version = models.CharField(verbose_name="系统版本", max_length=50)  # 软件版本号
    ip = models.CharField(verbose_name="管理IP", max_length=20)  # 管理IP
    port_num = models.IntegerField(verbose_name="端口数量", default=8, null=False)  # 端口数量
    branch = models.ForeignKey(Branch, verbose_name="分公司", on_delete=models.CASCADE)  # 地区


class WanNetworks(models.Model):
    branch = models.ForeignKey(Branch, verbose_name="分公司", on_delete=models.CASCADE)  # 地区
    isp = models.CharField(verbose_name="运营商", max_length=20)  # 运营商
    ip = models.CharField(verbose_name="IP地址", max_length=50)  # IP/掩码
    gateway = models.CharField(verbose_name="网关", max_length=20)  # 网关
    bandwidth = models.CharField(verbose_name="带宽", max_length=10)  # 带宽
    rent = models.CharField(verbose_name="付费方式", max_length=20)  # 付费方式/金额
    dns1 = models.CharField(verbose_name="DNS1", max_length=20, null=True)  # dns1
    dns2 = models.CharField(verbose_name="DNS2", max_length=20, null=True)  # dns2
    contact = models.CharField(verbose_name="联系人", max_length=50)  # 运营商联系人


class LanNetworks(models.Model):
    branch = models.ForeignKey(Branch, verbose_name="分公司", on_delete=models.CASCADE)  # 地区
    ip = models.CharField(verbose_name="IP网段", max_length=50)  # IP/掩码
    gateway = models.CharField(verbose_name="网关", max_length=20)  # 网关
    vlanid = models.IntegerField(verbose_name="VLAN号",)  # vlan id
    function = models.CharField(verbose_name="用途", max_length=20)  # 用途


class PortDesc(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)  # 地区
    device = models.ForeignKey(NetworkDevices, on_delete=models.CASCADE)  # 设备ID
    index = models.CharField(max_length=50, null=False)  # 端口索引
    desc = models.CharField(max_length=200, null=True)  # 端口描述


class Monitor(models.Model):
    STORAGE_THREE_MONTH = (
        (0, '不满足'),
        (1, '满足')
    )
    branch = models.ForeignKey(Branch, verbose_name="分公司", on_delete=models.CASCADE)  # 地区
    dev_model = models.CharField(verbose_name="设备型号", max_length=20)  # 型号
    ip = models.CharField(verbose_name="IP", max_length=20)  # IP
    camera_nums = models.IntegerField(verbose_name="摄像头数量", )  # 摄像头数量
    idle_channel = models.IntegerField(verbose_name="空闲通道", )  # 剩余通道数
    hdd = models.IntegerField(verbose_name="硬盘容量",)  # 硬盘容量
    idle_slot = models.IntegerField(verbose_name="剩余槽位",)  # 剩余硬盘槽位
    storage = models.IntegerField(verbose_name="满足存储三个月", choices=STORAGE_THREE_MONTH)  # 存储时间是否满足3个月
    desc = models.TextField(verbose_name="备注", null=True)  # 备注


class MonitorAccount(models.Model):
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE)  # 授权监控主机IP
    username = models.CharField(max_length=20)  # 授权账号
    password = models.CharField(max_length=20)  # 密码
    channel = models.CharField(max_length=50)  # 授权通道号
    desc = models.TextField(null=True)  # 授权描述
