from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.db.models import Count

from .models import VmInfo, HostInfo, FileInfo, ClusterInfo

@login_required()
def index_view(request):
    """admin module default page,and this is search page too
    
    Arguments:
        request {object} -- wsgi http request object
    
    Returns:
        html -- html template
    """
    vms_count = VmInfo.objects.all().count()
    hosts_count = HostInfo.objects.all().count()

    res_cluster = ClusterInfo.objects.filter(is_active=0).values('name','tag')
    cluster_array = {i['tag']:i['name'] for i in res_cluster}

    cluster_count = ClusterInfo.objects.all().count()
    print(cluster_count)
    vms_count_data = []
    for i in cluster_array:
        d = VmInfo.objects.filter(host__cluster_tag=i).count()
        vms_count_data.append(d)

    esxi_count_data = []   
    for i in cluster_array:
        d = HostInfo.objects.filter(cluster_tag=i).count()
        esxi_count_data.append(d)

    esxi_none_count = HostInfo.objects.filter(cluster_tag='none').count()
    
    user_count = User.objects.all().count()
    file_count = FileInfo.objects.all().count()

    return render(request, 'admin/index.html', {
        'user_url_path': '管理',
        'data':{
            'vms_count':vms_count,
            'hosts_count':hosts_count,
            'vms_count_data':vms_count_data,
            'esxi_count_data':esxi_count_data,
            'cluster_count':cluster_count,
            'cluster_data':res_cluster,
            'file_count': file_count,
            'user_count': user_count,
            'esxi_none_count': esxi_none_count

        }
    })


@login_required()
def get_cluster_count_info(request, cluster_name):
    res_cluster = ClusterInfo.objects.filter(is_active=0).values('name','tag')
    cluster_array = {i['tag']:i['name'] for i in res_cluster}
    if cluster_name not in cluster_array:
        return JsonResponse({
            'code':1,
            'msg': 'cluster name error'
        })
    else:
        res = HostInfo.objects.\
            filter(cluster_tag=cluster_name).\
            annotate(count=Count("vminfo__vm_hostname")).\
            values_list("hostname", "count")
        return JsonResponse({
            'code':0,
            'name': cluster_array[cluster_name],
            'msg':'success',
            'data':list(res)
        })
        


@login_required()
def render_static_temp_view(request, temp_name):
    """accroding parameter render static html template
    
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
    return render(request, 'admin/%s.html' % (temp_name), context)


@login_required()
def render_edit_view(request, form_name, nid):
    """accrodding resource primary key,render edit view
    
    Arguments:
        request {object} -- wsgi http request object
        form_name {str} -- resources type name
        nid {int} -- resources id
    
    Returns:
        html -- html template
    """
        
    if form_name not in ['vm', 'host', 'user', 'cluster']:
        return HttpResponse('object not found')

    temp_name = 'admin/add_or_edit_%s.html' % (form_name)
    if form_name == 'vm' and request.user.has_perm('admin.change_vminfo'):
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
    elif form_name == 'host' and request.user.has_perm('admin.change_hostinfo'):
        host_obj = HostInfo.objects.get(id=nid)
        context = {
            'user_url_path': '编辑',
            'host_obj': host_obj,
            'cluster_data': ClusterInfo.objects.filter(is_active=0).values('name','tag')
        }
    elif form_name == 'cluster' and request.user.has_perm('admin.change_clusterinfo'):
        obj = ClusterInfo.objects.get(id=nid)
        context = {
            'user_url_path': '编辑',
            'obj': obj,
        }
    elif form_name == 'user' and request.user.has_perm('auth.change_user'):
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
    if form_name not in ['vm', 'host', 'user', 'cluster']:
        return JsonResponse(return_data)
    res = None
    if form_name == 'vm' and request.user.has_perm('admin.delete_vminfo'):
        res = VmInfo.objects.get(id=nid).delete()
    elif form_name == 'host' and request.user.has_perm('admin.delete_hostinfo'):
        res = HostInfo.objects.get(id=nid).delete()
    elif form_name == 'cluster' and request.user.has_perm('admin.delete_clusterinfo'):
        res = ClusterInfo.objects.get(id=nid).delete()
    elif form_name == 'user' and request.user.has_perm('auth.delete_user'):
        res = User.objects.get(id=nid).delete()

    if res:
        return_data['msg'] = 'ok'
        return_data['code'] = 0

    return JsonResponse(return_data)


@login_required()
def create_or_update(request, form_type):
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
    if request.method != 'POST' or form_type not in ['vm', 'host', 'user', 'cluster']:
        return JsonResponse(return_data)

    post_data = request.POST.dict()
    del post_data['csrfmiddlewaretoken']
    del post_data['id']

    nid = int(request.POST.get('id', 0))
    # according id defind action
    if nid == 0:
        act = 'create'
        perm_act = 'add_'
    else:
        act = 'update'
        perm_act = 'change_'
    # define model and permission object
    if form_type == 'host':
        model = HostInfo
        perm_app = 'admin.'
        perm_model = 'hostinfo'
    elif form_type == 'vm':
        model = VmInfo
        del post_data['cluster_tag']
        perm_app = 'admin.'
        perm_model = 'vminfo'
    elif form_type == 'cluster':
        model = ClusterInfo
        perm_app = 'admin.'
        perm_model = 'clusterinfo'
        if post_data['tag'] == 'none':
            post_data['tag'] = '__none__'
    elif form_type == 'user':
        post_data['password'] = make_password(post_data['password'])
        model = User
        perm_app = 'auth.'
        perm_model = 'user'
    # permission verify
    if not request.user.has_perm(perm_app+perm_act+perm_model):
        return JsonResponse({
            'code': 1,
            'msg': 'permission error'
        })
    # do
    if act == 'create':
        res = model.objects.create(**post_data)
    elif act == 'update':
        res = model.objects.filter(id=nid).update(**post_data)
    else:
        return_data['msg'] = act + ' fail'
        return_data['code'] = 1
    # accroding return object judge create or update
    if (act == 'update' and res) or (act == 'create' and res.id):
        return_data['code'] = 0
        return_data['msg'] = act+' success'

    return JsonResponse(return_data)