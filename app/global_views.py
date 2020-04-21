from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.admin.options import get_content_type_for_model
from django.conf import settings
from .models import VmInfo, HostInfo, ClusterInfo


@login_required()
def render_static_temp_view(request, temp_name):
    """according parameter render static html template
    
    Arguments:
        request {object} -- wsgi http request object
        temp_name {str} -- template name
    
    Returns:
        html -- html template
    """
    res_cluster = ClusterInfo.objects.filter(is_active=0).values('name','tag')

    if 'list_' in temp_name:
        context = {
            'user_url_path': '管理',
        }
    elif 'change_password' in temp_name:
        context = {
            'user_url_path': '用户'
        }
    else:
        context = {
            'user_url_path': '添加',
        }
    context['cluster_data'] = res_cluster
    context['zabbix_api'] = settings.ZABBIX_API
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
        
    if form_name not in ['vm', 'host', 'user', 'cluster']:
        return render(request, 'admin/error.html', {'error_msg': 'illegal request!'})

    perm = {
        'vm': 'app.change_vminfo',
        'host': 'app.change_hostinfo',
        'cluster': 'app.change_clusterinfo',
        'user': 'auth.change_user'
    }
    # permission verify
    if not request.user.has_perm(perm[form_name]):
        return render(request, 'admin/error.html')

    temp_name = 'admin/add_or_edit_%s.html' % form_name

    if form_name == 'vm':
        vm_obj = VmInfo.objects.get(id=nid)
        host_obj = HostInfo.objects.get(id=vm_obj.host_id)
        esxi_list = HostInfo.objects.filter(cluster_tag=host_obj.cluster_tag)
        context = {
            'user_url_path': '编辑',
            'vm_obj': vm_obj,
            'cluster_tag': host_obj.cluster_tag,
            'esxi_list': esxi_list,
            'zabbix_api': settings.ZABBIX_API,
            'cluster_data': ClusterInfo.objects.filter(is_active=0).values('name','tag')
        }
    elif form_name == 'host':
        host_obj = HostInfo.objects.get(id=nid)
        context = {
            'user_url_path': '编辑',
            'host_obj': host_obj,
            'cluster_data': ClusterInfo.objects.filter(is_active=0).values('name','tag')
        }
    elif form_name == 'cluster':
        obj = ClusterInfo.objects.get(id=nid)
        context = {
            'user_url_path': '编辑',
            'obj': obj,
        }
    elif form_name == 'user':
        context = {
            'user_url_path': '编辑',
            'data': User.objects.get(id=nid)
        }
    else:
        temp_name = 'admin/error.html'
        context = {}

    return render(
        request,
        temp_name,
        context=context,
    )


@login_required()
def delete(request, form_name, nid):
    """
    delete some resources by form name and primary key
    
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
    if form_name not in ['vm', 'host', 'user', 'cluster']:
        return JsonResponse(return_data)

    model = {
        'host': HostInfo,
        'vm': VmInfo,
        'cluster': ClusterInfo,
        'user': User
    }
    perm = {
        'vm': 'app.delete_vminfo',
        'host': 'app.delete_hostinfo',
        'cluster': 'app.delete_clusterinfo',
        'user': 'auth.delete_user'
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
    """
    user post form event
    
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
    if request.method != 'POST' or form_name not in ['vm', 'host', 'user', 'cluster']:
        return JsonResponse(return_data)

    post_data = request.POST.dict()
    del post_data['csrfmiddlewaretoken']
    del post_data['id']

    nid = int(request.POST.get('id', 0))
    # according id defined action
    if nid == 0:
        act = 'create'
        perm_action_flag = 'add_'
    else:
        act = 'update'
        perm_action_flag = 'change_'
    # according form_name define perm app object
    if form_name == 'user':
        app_object = 'auth.'
    else:
        app_object = 'app.'
    # according form_name define model
    model = {
        'host': HostInfo,
        'vm': VmInfo,
        'cluster': ClusterInfo,
        'user': User
    }
    # according form_name define perm object
    perm_object = {
        'host': 'hostinfo',
        'vm': 'vminfo',
        'cluster': 'clusterinfo',
        'user': 'user'
    }
    if form_name == 'vm':
        del post_data['cluster_tag']
    elif form_name == 'cluster':
        if post_data['tag'] == 'none':
            post_data['tag'] = '__none__'
    elif form_name == 'user':
        if post_data['password'].strip() == '':
            del post_data['password']
        else:
            post_data['password'] = make_password(post_data['password'])

    # permission verify
    if not request.user.has_perm(app_object+perm_action_flag+perm_object[form_name]):
        return JsonResponse({
            'code': 1,
            'msg': 'permission error'
        })
    # do
    if act == 'create':
        res = model[form_name].objects.create(**post_data)
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(model[form_name]).pk,
            object_id=res.id,
            object_repr='',
            action_flag=ADDITION,
            change_message=str(res)
        )
    elif act == 'update':
        res = model[form_name].objects.filter(id=nid).update(**post_data)
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(model[form_name]).pk,
            object_id=nid,
            object_repr='',
            action_flag=CHANGE,
            change_message=str(model[form_name].objects.get(id=nid))
        )
        if form_name == 'user':
            update_session_auth_hash(request, request.user)
    else:
        return_data['msg'] = '%s fail' % act
        return_data['code'] = 1
    # according return object judge create or update
    if (act == 'update' and res) or (act == 'create' and res.id):
        return_data['code'] = 0
        return_data['msg'] = '%s success' % act

    return JsonResponse(return_data)


@login_required()
def view_log_view(request, content_type, object_id):
    model_array = [
        'user',
        'clusterinfo',
        'vminfo',
        'hostinfo'
    ]
    if content_type not in model_array:
        return render(request, 'admin/error.html', {'error_msg':'illegal request!'})
    all_user_queryset = User.objects.all().values('id', 'first_name')
    act_flag_exp = [
        {
            'id': 1,
            'value': '创建'
        },
        {
            'id': 2,
            'value': '修改'
        }
    ] 
    model = {
        'user': User,
        'clusterinfo': ClusterInfo,
        'vminfo': VmInfo,
        'hostinfo': HostInfo
    }
    res = model[content_type].objects.get(id=object_id)
    log_entries = LogEntry.objects.filter(
        content_type_id=get_content_type_for_model(model[content_type]).pk,
        object_id=res.id
    )
    return render(request, 'admin/view_log.html', {
        'action_flag':act_flag_exp,
        'all_user': all_user_queryset,
        'log_data': log_entries
    })
