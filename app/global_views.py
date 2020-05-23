import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
# from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.options import get_content_type_for_model
from django.conf import settings
from .models import(
    VmInfo, HostInfo, ClusterInfo, TroubleReport, DailyReport,
    Branch, NetworkDevices, WanNetworks, LanNetworks
) 


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
            'cluster_tag': '集群信息',
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
            'is_active': '是否激活'
        },
        'user':{
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
        }

    }


def form_array():
    return [
        'vm', 
        'host', 
        'user', 
        'cluster', 
        'trouble_report', 
        'daily_report', 
        'branch', 
        'lan_net',
        'wan_net',
        'net_devices'
    ]


@login_required()
def render_static_temp_view(request, temp_name):
    """according parameter render static html template

    Arguments:
        request {object} -- wsgi http request object
        temp_name {str} -- template name

    Returns:
        html -- html template
    """
    res_cluster = ClusterInfo.objects.filter(is_active=0).values('name', 'tag')
    context = {
        'cluster_data': res_cluster,
        'zabbix_api': settings.ZABBIX_API,
        'branch_data': Branch.objects.filter(isenable=1)
    }
    return render(request, 'admin/%s.html' % temp_name, context)


@login_required()
def render_edit_view(request, form_name, nid):
    """according resource primary key,render edit view
    
    Arguments:
        request {object} -- wsgi http request object
        form_name {str} -- resources type name
        nid {int} -- resources id
    
    Returns:
        html -- html template
    """

    request_form_array = form_array()
        
    if form_name not in request_form_array:
        return render(request, 'admin/error.html', {'error_msg': 'illegal request!'})

    app_name = 'app'
    perm_action = 'change'
    perm = {
        'vm': '%s.%s_vminfo',
        'host': '%s.%s_hostinfo',
        'cluster': '%s.%s_clusterinfo',
        'user': 'auth.change_user',
        'trouble': '%s.%s_troublereport',
        'daily_report': '%s.%s_dailyreport',
        'branch': '%s.%s_branch',
        'lan_net': '%s.%s_lannetworks',
        'wan_net': '%s.%s_wannetworks',
        'net_devices': '%s.%s_networkdevices',
    }
    models = {
        'host': HostInfo,
        'vm': VmInfo,
        'cluster': ClusterInfo,
        'user': User,
        'trouble': TroubleReport,
        'daily_report': DailyReport,
        'branch': Branch,
        'lan_net': LanNetworks,
        'wan_net': WanNetworks,
        'net_devices': NetworkDevices
    }
    # permission verify
    if not request.user.has_perm(perm[form_name] % (app_name, perm_action)):
        return render(request, 'admin/error.html')

    temp_name = 'admin/add_or_edit_%s.html' % form_name

    edit_obj = get_object_or_404(models[form_name], id=nid)

    # get all foreigenkey data
    cluster_data = ClusterInfo.objects.filter(is_active=0)
    branch_data = Branch.objects.filter(isenable=1)
    esxi_data = None
    if form_name == 'vm':
        esxi_data = HostInfo.objects.filter(cluster_tag=edit_obj.host.cluster_tag)

    extra_context = {
        'vm': {
            'esxi_list': esxi_data,
            'zabbix_api': settings.ZABBIX_API,
            'cluster_data': cluster_data
        },
        'branch': {},
        'host': {
            'cluster_data': cluster_data
        },
        'lan_net': {
            'branch_data': branch_data
        },
        'wan_net': {
            'branch_data': branch_data
        },
        'net_devices': {
            'branch_data': branch_data
        },
    }
    # append default object
    extra_context[form_name]['obj'] = edit_obj

    return render(
        request,
        temp_name,
        extra_context[form_name],
    )


@login_required()
def delete(request, form_name, nid):
    """delete some resources by form name and primary key

    Arguments:
        request {object} -- wsgi http request object
        form_name {str} -- according this judge resource type,just contains vm host user
        nid {int} -- resource model id

    Returns:
        json -- json object
    """
    return_data = {
        'code': 1,
        'msg': 'illegal request'
    }
    request_form_array = form_array()
    if form_name not in request_form_array:
        return JsonResponse(return_data)

    model = {
        'host': HostInfo,
        'vm': VmInfo,
        'cluster': ClusterInfo,
        'user': User,
        'trouble': TroubleReport,
        'daily_report': DailyReport,
        'branch': Branch,
        'lan_net': LanNetworks,
        'wan_net': WanNetworks,
        'net_devices': NetworkDevices
    }
    perm = {
        'vm': 'app.delete_vminfo',
        'host': 'app.delete_hostinfo',
        'cluster': 'app.delete_clusterinfo',
        'user': 'auth.delete_user',
        'trouble': 'app.delete_troublereport',
        'daily_report': 'app.delete_dailyreport',
        'branch': 'app.delete_branch',
        'lan_net': 'app.delete_lannetworks',
        'wan_net': 'app.delete_wannetworks',
        'net_devices': 'app.delete_networkdevices',
    }
    # permission verify
    if not request.user.has_perm(perm[form_name]):
        return JsonResponse({
            'msg': 'permission denied',
            'code': 1
        })
    # delete record
    res = None
    res = model[form_name].objects.get(id=nid).delete()

    if res:
        return_data['msg'] = 'ok'
        return_data['code'] = 0

    return JsonResponse(return_data)


@login_required()
def create_or_update(request, form_name):
    """user post form event

    Arguments:
        request {object} -- wsgi http request object
        form_type {str} -- form type,just contains vm host user

    Returns:
        json -- json object
    """
    return_data = {
        'code': 1,
        'msg': 'fail'
    }
    request_form_array = form_array()
    if request.method != 'POST' and form_name not in request_form_array:
        return JsonResponse({
            'code': 1,
            'msg': 'illegal request!'
        })

    post_data = request.POST.dict()
    del post_data['csrfmiddlewaretoken']
    del post_data['id']
    log = request.GET.get('log', True)
    nid = int(request.POST.get('id', 0))
    # according id defined action
    if nid == 0:
        act = 'create'
        perm_action_flag = 'add_'
        log_action_flag = ADDITION
    else:
        act = 'update'
        perm_action_flag = 'change_'
        log_action_flag = CHANGE
        log_object_id = nid
    # according form_name define perm app object
    if form_name == 'user':
        app_object = 'auth.'
    else:
        app_object = 'app.'
    # according form_name define perm object
    perm_object = {
        'host': 'hostinfo',
        'vm': 'vminfo',
        'cluster': 'clusterinfo',
        'user': 'user',
        'trouble_report': 'troublereport',
        'daily_report': 'dailyreport',
        'branch': 'branch',
        'lan_net': 'lannetworks',
        'wan_net': 'wannetworks',
        'net_devices': 'networkdevices',
    }
    # according form_name define model
    model = {
        'host': HostInfo,
        'vm': VmInfo,
        'cluster': ClusterInfo,
        'user': User,
        'trouble_report': TroubleReport,
        'daily_report': DailyReport,
        'branch': Branch,
        'lan_net': LanNetworks,
        'wan_net': WanNetworks,
        'net_devices': NetworkDevices
    }
    # permission verify
    if not request.user.has_perm(app_object + perm_action_flag + perm_object[form_name]):
        return JsonResponse({
            'code': 1,
            'msg': 'permission error'
        })
    
    if form_name == 'cluster':
        if post_data['tag'] == 'none':
            post_data['tag'] = '__none__'
    elif form_name == 'user':
        if post_data['password'].strip() == '':
            del post_data['password']
        else:
            post_data['password'] = make_password(post_data['password'])

    # write to db
    if act == 'create':
        res = model[form_name].objects.create(**post_data)
        log_object_id = res.id
    elif act == 'update':
        model[form_name].objects.filter(id=nid).update(**post_data)
        res = model[form_name].objects.get(id=nid)
        log_object_id = res.id
        if form_name == 'user':
            update_session_auth_hash(request, request.user)
    else:
        return_data['msg'] = '%s fail' % act
        return_data['code'] = 1

    # write log
    if log == 'no':
        pass
    else:
        log_content_type_model_id = get_content_type_for_model(model[form_name]).pk
        change_field = request.GET.get('change_field', None)
        log_change_data = []
        field_explain = data_struct()
        if change_field:
            for f in change_field.split(','):
                if form_name == 'vm' and f == 'host_id':
                    v = res.host.hostname
                elif form_name in ['vm', 'host'] and f in ['vm_status', 'dev_status']:
                    v = '开机' if post_data[f] == '0' else '关机'
                elif form_name == 'user' and f == 'is_active':
                    v = '启用' if post_data[f] == '1' else '禁用'
                elif form_name == 'host' and f == 'cluster_tag':
                    if post_data[f] == 'none':
                        v = '独立服务器'
                    else:
                        x = ClusterInfo.objects.filter(tag=post_data[f])
                        v = x[0].name
                elif form_name == 'user' and f == 'password':
                    v = '******'
                elif form_name == 'cluster' and f == 'is_active':
                    v = '启用' if post_data[f] == '0' else '禁用'
                else:
                    v = post_data[f]
                log_change_data.append('%s: %s' % (field_explain[form_name][f], v))

        if log_action_flag == ADDITION:
            log_object_repr = str(res)
        else:
            log_object_repr = ' '.join(log_change_data)

        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=log_content_type_model_id,
            object_id=log_object_id,
            object_repr=log_object_repr,
            action_flag=log_action_flag,
            change_message=json.dumps(post_data, ensure_ascii=True)
        )
    # according return object judge create or update
    if (act == 'update' and res) or (act == 'create' and res.id):
        return_data['code'] = 0
        return_data['msg'] = '%s success' % act

    return JsonResponse(return_data)


@login_required()
def view_log_view(request, content_type, object_id):
    """view log view

    Arguments:
        request {object} -- wsgi request object
        content_type {str} -- content type
        object_id {int} -- admin_log id

    Returns:
        retun  -- html view
    """
    model = {
        'user': User,
        'clusterinfo': ClusterInfo,
        'vminfo': VmInfo,
        'hostinfo': HostInfo
    }

    if content_type not in model:
        return render(request, 'admin/error.html', {'error_msg': 'illegal request!'})

    act_flag_exp = [
        ('none', 0),
        ('创建', 1),
        ('修改', 2),
        ('删除', 3)
    ]
    
    res = model[content_type].objects.get(id=object_id)

    log_entries = LogEntry.objects.filter(
        content_type_id=get_content_type_for_model(model[content_type]).pk,
        object_id=res.id
    )
    return render(request, 'admin/view_log.html', {
        'action_flag': act_flag_exp,
        'log_data': log_entries
    })


@login_required()
def log_rollback_view(request, log_id):
    """rollback according to the content of chang_message(**post_data) field in admin_log table

    Arguments:
        request {object} -- wsgi request object
        log_id {int} -- admin_log id

    Returns:
        str -- rollback state json
    """
    models = {
        'clusterinfo': ClusterInfo,
        'hostinfo': HostInfo,
        'vminfo': VmInfo,
        'user': User
    }
    log_res = LogEntry.objects.get(id=log_id)
    if not log_res:
        return JsonResponse({
            'code': 1,
            'msg': 'not found this log resource!'
        })

    # user_id = request.user.id
    # if user_id != log_res.user_id:
    #     return JsonResponse({
    #         'code': 1,
    #         'msg': 'permission denied'
    #     })

    if not log_res.change_message:
        return JsonResponse({
            'code': 1,
            'msg': 'not found rollback data'
        })

    post_data = json.loads(log_res.change_message)
    content_type = log_res.content_type.model
    origin_res = models[content_type].objects.get(id=log_res.object_id)
    if not origin_res:
        res = models[content_type].objects.create(**post_data)
    else:
        models[content_type].objects.filter(id=log_res.object_id).update(**post_data)
        res = models[content_type].objects.get(id=log_res.object_id)

    if res:
        return JsonResponse({
            'code': 0,
            'msg': 'rollback success',
            'jumpurl': '/admin/edit/%s/%s' % (content_type.replace('info', ''), res.id)
        })
    # else action
    return JsonResponse({
        'code': 0,
        'msg': 'rollback failed'
    })

  