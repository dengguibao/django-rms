import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.admin.options import get_content_type_for_model
from django.conf import settings
from .common import *


@login_required()
def render_static_temp_view(request, temp_name):
    """according parameter render static html template

    Arguments:
        request {object} -- wsgi http request object
        temp_name {str} -- template name

    Returns:
        html -- html template
    """
    res_cluster = ClusterInfo.objects.filter(is_active=0)
    context = {
        'cluster_data': res_cluster,
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
        
    if form_name not in form_name_list:
        return render(request, 'admin/error.html', {'error_msg': 'illegal request!'})

    perm_action_flag = 'change'
    # permission verify
    if not request.user.has_perm(perms[form_name] % perm_action_flag):
        return render(request, 'admin/error.html')

    temp_name = 'admin/add_or_edit_%s.html' % form_name

    edit_obj = get_object_or_404(models[form_name], id=nid)

    # get all foreigenkey data
    cluster_data = ClusterInfo.objects.filter(is_active=0)
    branch_data = Branch.objects.filter(isenable=1)
    esxi_data = None
    if form_name == 'vm':
        esxi_data = HostInfo.objects.filter(cluster_tag=edit_obj.host.cluster_tag)

    context = {
        'obj': edit_obj
    }

    extra_context = {
        'vm': {
            'esxi_list': esxi_data,
            'zabbix_api': settings.ZABBIX_API,
            'cluster_data': cluster_data
        },
        'host': {
            'cluster_data': cluster_data,
            'branch_data': branch_data
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
        'monitor': {
            'branch_data': branch_data
        }
    }
    # append default object
    if form_name in extra_context:
        context.update(extra_context[form_name])

    return render(
        request,
        temp_name,
        context
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
    if not request.is_ajax():
        return JsonResponse(return_data)

    if form_name not in form_name_list:
        return JsonResponse(return_data)

    perm_action_flag = 'delete'
    # permission verify
    if not request.user.has_perm(perms[form_name] % perm_action_flag):
        return JsonResponse({
            'msg': 'permission denied',
            'code': 1
        })
    # delete record
    res = None
    res = models[form_name].objects.get(id=nid).delete()

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
    if not request.is_ajax() and form_name not in form_name_list:
        return JsonResponse({
            'code': 1,
            'msg': 'illegal request!'
        })
    
    # permission verify
    perm_action_flag = 'add'
    if not request.user.has_perm(perms[form_name] % perm_action_flag):
        return JsonResponse({
            'code': 1,
            'msg': 'permission denied'
        })

    if request.user.is_superuser and form_name != 'user':
        return JsonResponse({
            'code': 1,
            'msg': '管理员不允许创建业务数据'
        })

    post_data = request.POST.dict()
    del post_data['csrfmiddlewaretoken']
    del post_data['id']

    log = request.GET.get('log', True)
    nid = int(request.POST.get('id', 0))
    # according id defined action
    if nid == 0:
        act = 'create'
        perm_action_flag = 'add'
        log_action_flag = ADDITION
    else:
        act = 'update'
        perm_action_flag = 'change'
        log_action_flag = CHANGE
        log_object_id = nid

    # -------extra logic action-------
    extra_data = []
    if form_name == 'net_devices':
        for k in list(post_data.keys()):
            if 'port_index' in k:
                extra_data.append(
                    (k, post_data[k])
                )
                del post_data[k]
    elif form_name == 'monitor':
        tmp_data = {}
        for k in list(post_data.keys()):
            if 'username_' in k or 'password_' in k or 'desc_' in k or 'channel_' in k:
                tmp_data[k.split('_')[0]] = post_data[k]
                del post_data[k]
                if len(tmp_data) == 4:
                    extra_data.append(tmp_data)
                    del tmp_data
                    tmp_data = {}
    elif form_name == 'host':
        tmp_data = {}
        for k in list(post_data.keys()):
            if 'ifname_' in k or 'access_' in k:
                tmp_data[k.split('_')[0]] = post_data[k]
                del post_data[k]
                if len(tmp_data) == 2:
                    extra_data.append(tmp_data)
                    del tmp_data
                    tmp_data = {}
    # -------end extra logic-------

    # write to db
    if act == 'create':
        res = models[form_name].objects.create(**post_data)
        log_object_id = res.id
        # -------extra action-------
        if form_name == "net_devices" and extra_data:
            write_port_desc(res.branch_id, res.id, extra_data)
        if form_name == 'monitor' and extra_data:
            write_monitor_account(res.id, extra_data)
        if form_name == 'host' and extra_data:
            write_host_interface(res.id, extra_data)
        # -------end extra action-------
            
    elif act == 'update':
        models[form_name].objects.filter(id=nid).update(**post_data)
        res = models[form_name].objects.get(id=nid)
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
        log_content_type_model_id = get_content_type_for_model(models[form_name]).pk
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

    if content_type not in models:
        return render(request, 'admin/error.html', {'error_msg': 'illegal request!'})

    act_flag_exp = [
        ('none', 0),
        ('创建', 1),
        ('修改', 2),
        ('删除', 3)
    ]

    res = get_object_or_404(models[content_type], pk=object_id)
    
    log_entries = LogEntry.objects.filter(
        content_type_id=get_content_type_for_model(models[content_type]).pk,
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


@login_required()
def navigation(request):
    return render(request, 'admin/navigation.html')


def write_port_desc(branch_id, device_id, data):
    branch_obj = Branch.objects.get(id=branch_id)
    device_obj = NetworkDevices.objects.get(id=device_id)
    d = []
    for k, v in data:
        d.append(
            PortDesc(
                branch=branch_obj,
                device=device_obj,
                index=k,
                desc=v
            )
        )
    PortDesc.objects.bulk_create(d)


def write_monitor_account(monitor_id, data):
    monitor_obj = Monitor.objects.get(id=monitor_id)
    d = []
    for i in data:
        d.append(
            MonitorAccount(
                monitor=monitor_obj,
                username=i['username'],
                password=i['password'],
                desc=i['desc'],
                channel=i['channel']
            )
        )
    MonitorAccount.objects.bulk_create(d)


def write_host_interface(host_id, data):
    host_obj = HostInfo.objects.get(id=host_id)
    d = []
    for i in data:
        d.append(
            HostInterface(
                host=host_obj,
                ifname=i['ifname'],
                access=i['access'],
            )
        )
    HostInterface.objects.bulk_create(d)