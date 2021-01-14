from .models import *
from django.contrib.auth.models import User


register_form = {
    'host': {
        'model': HostInfo,
        'perm': 'app.%s_hostinfo',
    },
    'hostif': {
        'model': HostInterface,
        'perm': 'app.%s_hostinfo',
    },
    'vm': {
        'model': VmInfo,
        'perm': 'app.%s_vminfo',
    },
    'cluster': {
        'model': ClusterInfo,
        'perm': 'app.%s_clusterinfo',
    },
    'user': {
        'model': User,
        'perm': 'auth.%s_user',
    },
    'trouble_report': {
        'model': TroubleReport,
        'perm': 'app.%s_troublereport',
    },
    'daily_report': {
        'model': DailyReport,
        'perm': 'app.%s_dailyreport',
    },
    'branch': {
        'model': Branch,
        'perm': 'app.%s_branch',
    },
    'lan_net': {
        'model': LanNetworks,
        'perm': 'app.%s_lannetworks',
    },
    'wan_net': {
        'model': WanNetworks,
        'perm': 'app.%s_wannetworks',
    },
    'net_devices': {
        'model': NetworkDevices,
        'perm': 'app.%s_networkdevices',
    },
    'monitor': {
        'model': Monitor,
        'perm': 'app.%s_monitor',
    },
    'monitor_account': {
        'model': MonitorAccount,
        'perm': 'app.%s_monitor',
    },
    'bank_private': {
        'model': BankPrivate,
        'perm': 'app.%s_bankprivate',
    },
}

# models = {
#     'host': HostInfo,
#     'hostif': HostInterface,
#     'vm': VmInfo,
#     'cluster': ClusterInfo,
#     'user': User,
#     'trouble_report': TroubleReport,
#     'daily_report': DailyReport,
#     'branch': Branch,
#     'lan_net': LanNetworks,
#     'wan_net': WanNetworks,
#     'net_devices': NetworkDevices,
#     'monitor': Monitor,
#     'monitor_account': MonitorAccount,
#     'bank_private': BankPrivate,
# }
#
# perms = {
#     'vm': 'app.%s_vminfo',
#     'host': 'app.%s_hostinfo',
#     'hostif': 'app.%s_hostinfo',
#     'cluster': 'app.%s_clusterinfo',
#     'user': 'auth.%s_user',
#     'trouble_report': 'app.%s_troublereport',
#     'daily_report': 'app.%s_dailyreport',
#     'branch': 'app.%s_branch',
#     'lan_net': 'app.%s_lannetworks',
#     'wan_net': 'app.%s_wannetworks',
#     'net_devices': 'app.%s_networkdevices',
#     'monitor': 'app.%s_monitor',
#     'monitor_account': 'app.%s_monitor',
#     'bank_private': 'app.%s_bankprivate'
# }
#
# form_name_list = [
#     'vm',
#     'host',
#     'hostif',
#     'user',
#     'cluster',
#     'trouble_report',
#     'daily_report',
#     'branch',
#     'lan_net',
#     'wan_net',
#     'net_devices',
#     'monitor',
#     'monitor_account',
#     'bank_private'
# ]


def data_struct():
    """field struct chinese description

    Returns:
        dict -- return struct description
    """
    return {
        'vm': {
            'vm_hostname': '主机名',
            'vm_ip': 'IP',
            'vlan_tag': 'VLAN标签',
            'vlan_id': 'VLAN ID',
            'host_id': '宿主机',
            'vm_status': '状态',
            'vm_cpu': 'CPU',
            'vm_disk': '硬盘(G)',
            'vm_memory': '内存(G)',
            'vm_os': '操作系统',
            'vm_monitor': 'zabbix监控',
            'pub_date': '加入时间',
            'vm_register': '申请人',
            'vm_intention': '用途',
            'vm_desc': '备注',
        },
        'host': {
            'hostname': '主机名',
            'sn': '序列号',
            'idrac_ip': 'iDRAC ip',
            'host_ip': '主机IP',
            'dev_status': '状态',
            'cluster_tag_id': '集群信息',
            'cpu_nums': 'CPU数量',
            'cpu_core': 'CPU核心数',
            'cpu_rate': 'CPU频率',
            'cpu_total_rate': 'CPU总频率',
            'sd_nums': 'sata数量',
            'sd_size': 'sata容量(T)',
            'sd_total_size': 'sata总容量(T)',
            'ssd_nums': 'ssd数量',
            'ssd_size': 'ssd容量(T)',
            'ssd_total_size': 'ssd总容量(T)',
            'memory_nums': '内存数量',
            'memory_size': '内存容量(G)',
            'memory_total_size': '内存总容量(G)',
            'supply_name': '供应商名称',
            'supply_contact_name': '供应商联系人',
            'supply_phone': '供应商联系号码',
            'dc_name': '数据中心',
            'rack_num': '机柜号',
            'slot_num': '槽位号',
            'buy_date': '购买日期',
            'end_svc_date': '过保日期',
            'idrac_net_in': '业务网络接入',
            'svc_net_in': 'iDRAC网络接入',
            'raid': 'RAID模式',
            'intention': '用途',
            'os': '操作系统',
            'dev_model': '设备型号',
            'pub_date': '加入时间',
            'desc': '备注',
        },
        'cluster': {
            'name': '集群名称',
            'tag': '集群标记',
            'is_active': '是否激活',
            'is_virt': '类别'
        },
        'user': {
            'username': '用户名',
            'password': '密码',
            'first_name': '姓名',
            'email': '邮箱',
            'is_active': '状态'
        },
        'daily': {
            'content': '工作内容',
            'type': '工作类型',
            'owner': '人员',
            'pub_date': '工作时间',
        },
        'trouble': {
            'desc': '故障描述',
            'type': '故障类型',
            'start_date': '产生时间',
            'end_date': '恢复时间',
            'device': '所属设备',
            'info': '故障现象',
            'reason': '故障原因',
            'resolv_method': '解决方法',
            'owner': '值班人员',
            'pub_date': '报告时间',
        },
        'wan_net': {
            'branch_id': '分公司',
            'isp': '运营商',
            'ip': 'IP',
            'gateway': '网关',
            'bandwidth': '带宽',
            'rent': '付费方式',
            'dns1': 'DNS1',
            'dns2': 'DNS2',
            'contact': '联系人',
        },
        'bank_private': {
            'name': '业务名称',
            'access_type': '访问方式',
            'require_authorize_addr': '需要授权网址',
            'real_authorize_addr': '实际授权网址',
            'is_proxy': '是否代理',
            'firewall_policy_name': '防火墙策略名称',
            'nat_src_addr_pool': 'NAT源地址',
            'nat_dest_addr_pool': 'NAT目标地址',
            'int_behave_control_policy': '上网行为控制策略',
            'int_behave_audit_policy': '上网行业审计策略',
            'global_ip': '公网IP',
            'service_leader': '对接人',
            'user_ip_addr': '授权用户IP',
            'user_permission': '授权用户及权限',
            'is_active': '状态',
            'desc': '备注',
        }
    }
