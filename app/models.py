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

    class Meta:
        verbose_name = '银行专线'


class DailyReport(models.Model):
    content = models.TextField(null=False, verbose_name='工作内容')
    type = models.CharField(null=False, max_length=10, verbose_name='工作类别')
    owner = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE)
    pub_date = models.DateField(verbose_name="发布时间", null=False, auto_now=True)

    def __str__(self):
        return '%s %s' % (self.owner.first_name, self.type)

    class Meta:
        verbose_name = '日报'


class TroubleReport(models.Model):
    desc = models.CharField(verbose_name="故障说明", null=False, max_length=80)
    type = models.CharField(verbose_name="故障类别", null=False, max_length=20)
    start_date = models.DateTimeField(verbose_name="开始时间", null=False)
    end_date = models.DateTimeField(verbose_name="结束时间", null=True)
    device = models.CharField(verbose_name="故障设备", null=True, max_length=100)
    info = models.TextField(verbose_name="故障现象", null=True)
    reason = models.TextField(verbose_name="故障原因", null=True)
    resolv_method = models.TextField(verbose_name="解决办法", null=True)
    repairer = models.CharField(verbose_name="处理人", null=True, max_length=100)
    prevent = models.TextField(verbose_name="预防措施", null=True)
    owner = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE)
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now=True)

    class Meta:
        verbose_name = '故障报告'


class ClusterInfo(models.Model):
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
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)

    def __str__(self):
        return "集群名称:{} 集群标记:{}".format(self.name, self.tag)

    class Meta:
        verbose_name = '集群'


class FileInfo(models.Model):
    UPLOAD_DOC_TYPE = (
        (0, '文件夹'),
        (1, '文件')
    )

    path = models.CharField(verbose_name="文件路径", max_length=200, null=False)
    type = models.IntegerField(verbose_name="文件类型", null=False, default=0, choices=UPLOAD_DOC_TYPE)
    name = models.CharField(verbose_name="文件名称", max_length=100, null=False)
    file_size = models.CharField(verbose_name="文件大小", max_length=10, null=True, default=0)
    real_path = models.CharField(verbose_name="存储路径", max_length=200, null=True)
    real_name = models.CharField(verbose_name="存储名称", max_length=100, null=True)
    file_type = models.CharField(verbose_name="文件类型", max_length=5, null=True)
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)
    owner = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE)

    def __str__(self):
        return "name:{} type:{},".format(self.name, self.type)

    class Meta:
        verbose_name = '文档'


class HostInfo(models.Model):
    HOST_STATUS = (
        (0, '开机'),
        (1, '关机')
    )

    hostname = models.CharField(verbose_name="主机名", max_length=100, unique=True)
    sn = models.CharField(verbose_name="序列号", max_length=80)
    idrac_ip = models.GenericIPAddressField(verbose_name="iDRAC IP")
    host_ip = models.GenericIPAddressField(verbose_name="主机IP")
    cluster_tag = models.ForeignKey(ClusterInfo, verbose_name="集群", on_delete=models.CASCADE, to_field="tag", null=True)
    cpu_nums = models.IntegerField(verbose_name="CPU数量", default=0)
    cpu_core = models.IntegerField(verbose_name="CPU总数", default=0)
    cpu_rate = models.FloatField(verbose_name="CPU频率", default=0)
    cpu_total_rate = models.FloatField(verbose_name="CPU总数量", default=0)
    sd_nums = models.IntegerField(verbose_name="机槿硬盘数量", default=0)
    sd_size = models.FloatField(verbose_name="机械硬盘大小", default=0)
    sd_total_size = models.FloatField(verbose_name="机槿硬盘总量", default=0)
    ssd_nums = models.IntegerField(verbose_name="SSD数量", default=0)
    ssd_size = models.FloatField(verbose_name="SSD大小", default=0)
    ssd_total_size = models.FloatField(verbose_name="SSD总量", default=0)
    dev_model = models.CharField(verbose_name="设备型号", max_length=50, null=True)
    memory_nums = models.IntegerField(verbose_name="内存数量", default=0)
    memory_size = models.IntegerField(verbose_name="内存容量", default=0)
    memory_total_size = models.IntegerField(verbose_name="内存总容量", default=0)
    os = models.CharField(verbose_name="操作系统", max_length=20)
    desc = models.TextField(verbose_name="备注", null=True)
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
    dev_status = models.IntegerField(verbose_name="状态", default=0, choices=HOST_STATUS)
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)

    def __str__(self):
        return "主机名:{} ip:{} 集群:{} idrac ip:{}".format(
            self.hostname, self.host_ip, self.cluster_tag, self.idrac_ip
        )

    class Meta:
        verbose_name = '服务器'


class HostInterface(models.Model):
    host = models.ForeignKey(HostInfo, on_delete=models.CASCADE)
    ifname = models.CharField(verbose_name="接口序号", max_length=100, null=False)
    access = models.CharField(verbose_name="接口描述", max_length=100, null=False)

    class Meta:
        verbose_name = '设备接口'


class VmInfo(models.Model):
    HOST_STATUS = (
        (0, '开机'),
        (1, '关机')
    )

    vm_hostname = models.CharField(verbose_name="主机名", max_length=100, )
    vm_intention = models.CharField(verbose_name="用途", max_length=100, null=True)
    vm_register = models.CharField(verbose_name="申请人", max_length=10, null=True)
    vm_monitor = models.CharField(verbose_name="zabbix监控", max_length=5, null=True)
    vm_ip = models.GenericIPAddressField(verbose_name="IP地址",)
    vlan_tag = models.CharField(verbose_name="vlan标签", max_length=30)
    vlan_id = models.IntegerField(verbose_name="vlan号",)
    host = models.ForeignKey(HostInfo, verbose_name="宿主机", on_delete=models.CASCADE)
    vm_cpu = models.IntegerField(verbose_name="CPU", default=0)
    vm_disk = models.IntegerField(verbose_name="硬盘", default=0)
    vm_memory = models.IntegerField(verbose_name="内存", default=0)
    vm_os = models.CharField(verbose_name="操作系统", max_length=20)
    vm_desc = models.TextField(verbose_name="备注", null=True)
    vm_status = models.IntegerField(verbose_name="状态", default=0, choices=HOST_STATUS)
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)

    def __str__(self):
        return "主机名:{} 申请人:{} IP:{} VLAN ID:{} VLAN标签:{} ".format(
            self.vm_hostname, self.vm_register, self.vm_ip,
            self.vlan_id, self.vlan_tag
        )

    class Meta:
        verbose_name = '虚拟服务器'


class Branch(models.Model):
    IS_ENABLE = (
        (0, '停用'),
        (1, '启用')
    )
    name = models.CharField(verbose_name="名称", max_length=20)
    address = models.CharField(verbose_name="公司地址", max_length=100)
    isenable = models.IntegerField(verbose_name="状态", default=1, choices=IS_ENABLE, null=False)

    class Meta:
        verbose_name = '分子公司'


class NetworkDevices(models.Model):
    hostname = models.CharField(verbose_name="主机名", max_length=50)
    device_type = models.CharField(verbose_name="设备类型", max_length=20)
    brand = models.CharField(verbose_name="设备品牌", max_length=20)
    sn = models.CharField(verbose_name="设备序号", max_length=50)
    device_model = models.CharField(verbose_name="设备型号", max_length=50)
    version = models.CharField(verbose_name="系统版本", max_length=50)
    ip = models.CharField(verbose_name="管理IP", max_length=20)
    port_num = models.IntegerField(verbose_name="端口数量", default=8, null=False)
    branch = models.ForeignKey(Branch, verbose_name="分公司", on_delete=models.CASCADE)

    class Meta:
        verbose_name = '网络设备'


class WanNetworks(models.Model):
    branch = models.ForeignKey(Branch, verbose_name="分公司", on_delete=models.CASCADE)
    isp = models.CharField(verbose_name="运营商", max_length=20)
    ip = models.CharField(verbose_name="IP地址", max_length=50)
    gateway = models.CharField(verbose_name="网关", max_length=20)
    bandwidth = models.CharField(verbose_name="带宽", max_length=10)
    rent = models.CharField(verbose_name="付费方式", max_length=20)
    dns1 = models.CharField(verbose_name="DNS1", max_length=20, null=True)
    dns2 = models.CharField(verbose_name="DNS2", max_length=20, null=True)
    contact = models.CharField(verbose_name="联系人", max_length=50)

    class Meta:
        verbose_name = '互联网信息'


class LanNetworks(models.Model):
    branch = models.ForeignKey(Branch, verbose_name="分公司", on_delete=models.CASCADE)
    ip = models.CharField(verbose_name="IP网段", max_length=50)
    gateway = models.CharField(verbose_name="网关", max_length=20)
    vlanid = models.IntegerField(verbose_name="VLAN号",)
    function = models.CharField(verbose_name="用途", max_length=20)

    class Meta:
        verbose_name = '内网信息'


class PortDesc(models.Model):
    branch = models.ForeignKey(Branch, verbose_name="分公司", on_delete=models.CASCADE)
    device = models.ForeignKey(NetworkDevices, verbose_name="设备", on_delete=models.CASCADE)
    index = models.CharField(verbose_name="端口号", max_length=50, null=False)
    desc = models.CharField(verbose_name="端口描述", max_length=200, null=True)

    class Meta:
        verbose_name = '端口描述'


class Monitor(models.Model):
    STORAGE_THREE_MONTH = (
        (0, '不满足'),
        (1, '满足')
    )
    branch = models.ForeignKey(Branch, verbose_name="分公司", on_delete=models.CASCADE)
    dev_model = models.CharField(verbose_name="设备型号", max_length=20)
    ip = models.CharField(verbose_name="IP", max_length=20)
    camera_nums = models.IntegerField(verbose_name="摄像头数量", )
    idle_channel = models.IntegerField(verbose_name="空闲通道", )
    hdd = models.IntegerField(verbose_name="硬盘容量",)
    idle_slot = models.IntegerField(verbose_name="剩余槽位",)
    storage = models.IntegerField(verbose_name="满足存储三个月", choices=STORAGE_THREE_MONTH)
    desc = models.TextField(verbose_name="备注", null=True)

    class Meta:
        verbose_name = '监控主机'


class MonitorAccount(models.Model):
    monitor = models.ForeignKey(Monitor, verbose_name="监控主机", on_delete=models.CASCADE)
    username = models.CharField(verbose_name="帐号", max_length=20)
    password = models.CharField(verbose_name="密码", max_length=20)
    channel = models.CharField(verbose_name="授权通道", max_length=50)
    desc = models.TextField(verbose_name="授权描述", null=True)

    class Meta:
        verbose_name = '监控主机授权'
