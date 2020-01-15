from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import User, Permission
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password

from .models import VmInfo, HostInfo


@login_required(login_url='/index')
def index(request):
    '''
    admin module default page
    '''
    return render(request, 'admin/index.html')


@login_required(login_url='/index')
def render_static_temp_view(request, temp_name):
    '''
    render static template
    '''
    return render(request, 'admin/%s.html' % (temp_name))


@login_required(login_url='/index')
def render_edit_view(request, form_name, nid):
    '''
    render edit view by form name and primary key
    '''
    if form_name not in ['vm', 'host', 'user']:
        return HttpResponse('object not found')

    temp_name = 'admin/add_or_edit_%s.html' % (form_name)
    if form_name == 'vm' and request.user.has_perm('admin.change_vminfo'):
        vm_obj = VmInfo.objects.get(id=nid)
        host_obj = HostInfo.objects.get(id=vm_obj.host_id)
        esxi_list = HostInfo.objects.filter(cluster_tag=host_obj.cluster_tag)
        context = {
            'vm_obj': vm_obj,
            'cluster_tag': host_obj.cluster_tag,
            'esxi_list': esxi_list
        }
    elif form_name == 'host' and request.user.has_perm('admin.change_hostinfo'):
        host_obj = HostInfo.objects.get(id=nid)
        context = {
            'host_obj': host_obj,
        }
    elif form_name == 'user' and request.user.has_perm('auth.change_user'):
        context = {
            'data': User.objects.get(id=nid)
        }
    else:
        temp_name = 'admin/error.html'
        context = {}

    return render(
        request,
        temp_name,
        context=context
    )


@login_required(login_url='/index')
def delete(request, form_name, nid):
    '''
    delete some resource by form namd and primary key
    '''
    return_data = {
        'code': 1,
        'msg': 'illegal request'
    }
    if form_name not in ['vm', 'host', 'user']:
        return JsonResponse(return_data)
    res = None
    if form_name == 'vm' and request.user.has_perm('admin.delete_vminfo'):
        res = VmInfo.objects.get(id=nid).delete()
    elif form_name == 'host' and request.user.has_perm('admin.delete_hostinfo'):
        res = HostInfo.objects.get(id=nid).delete()
    elif form_name == 'user' and request.user.has_perm('auth.delete_user'):
        res = User.objects.get(id=nid).delete()

    if res:
        return_data['msg'] = 'ok'
        return_data['code'] = 0

    return JsonResponse(return_data)


@login_required(login_url='/index')
def create_or_update(request, form_type):
    '''
    add and update form post event
    '''
    return_data = {
        'code': 1,
        'msg': 'fail'
    }
    if request.method != 'POST' or form_type not in ['vm', 'host', 'user']:
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
    # define model and permisson object
    if form_type == 'host':
        model = HostInfo
        perm_app = 'admin.'
        perm_model = 'hostinfo'
    elif form_type == 'vm':
        model = VmInfo
        del post_data['cluster_tag']
        perm_app = 'admin.'
        perm_model = 'vminfo'
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

@login_required(login_url='/index')
def user_logout(request):
    '''
    user logout
    '''
    logout(request)
    return HttpResponseRedirect('/index')


@login_required(login_url='/index')
def user_change_password(request):
    '''
    change user login password
    '''
    user = request.user
    if request.method != 'POST':
        return JsonResponse({
            'code': 1,
            'msg': 'illegal request'
        })
    old_password = request.POST.get("old_password", None)
    new_password = request.POST.get('new_password', None)
    re_password = request.POST.get('re_password', None)

    if user.check_password(old_password) and\
            old_password and new_password and \
            re_password and new_password == re_password:

        user.set_password(new_password)
        user.save()
        return JsonResponse({
            'code': 0,
            'msg': 'success'
        })
    else:
        return JsonResponse({
            'code': 1,
            'msg': 'failed'
        })


@login_required(login_url='/index')
def get_user_list_view(request):
    '''
    user account admin view
    '''
    if request.user.has_perm('auth.view_user'):
        user_list = User.objects.all()
        temp_name = 'admin/list_users.html'
        context = {
            'obj': user_list
        }
    else:
        temp_name = 'admin/error.html'
        context = {}

    return render(
        request,
        temp_name,
        context=context
    )


@login_required(login_url='/index')
def get_hosts_list(request, dev_type, flag):
    '''
    get all host and virtual machine resource
    '''
    page_size = settings.PAGE_SIZE
    return_data = {
        'code': 1,
        'msg': 'illegal request'
    }

    if dev_type not in ['host', 'vm'] or len(flag) <= 0:
        return JsonResponse(return_data)

    if dev_type == 'host' and request.user.has_perm('admin.view_hostinfo'):
        if flag not in ['cs', 'xh', 'test', 'none', 'all']:
            return JsonResponse(return_data)
        if flag == 'all':
            rs = HostInfo.objects.all()
        else:
            rs = HostInfo.objects.filter(cluster_tag=flag)
        return_data['data'] = [i for i in rs.values()]
        return_data['code'] = 0
        return_data['msg'] = 'ok'
    # get virtual machine info
    elif dev_type == 'vm' and request.user.has_perm('admin.view_vminfo'):
        if '_all' in flag:
            x = flag.split('_')
            if x[0] not in ['cs', 'xh', 'test']:
                return JsonResponse(return_data)
            else:
                vm_obj = VmInfo.objects.filter(host__cluster_tag=x[0])
                host_obj = HostInfo.objects.filter(cluster_tag=x[0])
        elif flag == 'all':
            vm_obj = VmInfo.objects.exclude(host__cluster_tag='none')
            host_obj = HostInfo.objects.all()
        else:
            vm_obj = VmInfo.objects.filter(host__hostname=flag)
            host_obj = HostInfo.objects.filter(hostname=flag)

        p = Paginator(vm_obj.values(), page_size)
        page = int(request.GET.get('page', 1))
        data_obj = p.page(page)
        esxi_kvp = {i.id: i.hostname for i in host_obj}
        vm_data = []
        for i in data_obj:
            i["esxi_host_name"] = esxi_kvp[i['host_id']]
            vm_data.append(i)
        return_data['data'] = vm_data
        return_data['page_data'] = {
            'rs_count': p.count,
            'page_count': p.num_pages,
            'page_size': page_size,
            'curr_page': page,
        }
        return_data['code'] = 0
        return_data['msg'] = 'ok'
    else:
        return_data['msg'] = 'permission error'
        return JsonResponse(return_data)

    return JsonResponse(return_data)


@login_required(login_url='/index')
def search(request, dev_type, keyword):
    '''
    accroding keyword search host or virtual machine
    '''
    if dev_type not in ['vm', 'host'] or len(keyword) == 0:
        return JsonResponse({
            'code': 1,
            'msg': 'illegal request'
        })
    if dev_type == 'vm' and request.user.has_perm('admin.view_vminfo'):
        model = VmInfo
    elif dev_type == 'host' and request.user.has_perm('admin.view_hostinfo'):
        model = HostInfo
    else:
        return JsonResponse({
            'code': 1,
            'msg': 'permission error'
        })

    if dev_type == 'vm':
        res = model.objects.filter(
            Q(vm_ip__contains=keyword) |
            Q(vm_hostname__contains=keyword)
        )
        host_obj = HostInfo.objects.all()
        esxi_kvp = {i.id: i.hostname for i in host_obj}
        vm_data = []
        for i in res.values():
            i["esxi_host_name"] = esxi_kvp[i['host_id']]
            vm_data.append(i)
        return_data = {
            'data': vm_data,
            'code': 0,
            'msg': 'ok',
            'page_data': {
                'rs_count': 1,
                'page_count': 1,
                'page_size': 1,
                'curr_page': 1,
            }
        }
    elif dev_type == 'host':
        res = model.objects.filter(
            Q(host_ip__contains=keyword) |
            Q(hostname__contains=keyword) |
            Q(idrc_ip__contains=keyword)
        )
        return_data = {
            'data': [i for i in res.values()],
            'code': 0,
            'msg': 'ok'
        }
    return JsonResponse(return_data)


@login_required(login_url='/index')
def permissin_admin_view(request, nid):
    '''
    user permissoin admin for someone user
    '''
    if request.user.has_perm('auth.add_user') and request.user.has_perm('auth.change_user'):
        user = User.objects.get(id=nid)
        user_permission_list = user.get_all_permissions()
        data = []
        for i in user_permission_list:
            data.append({
                'permiss_explain': permission_explain(i.split('.')[1]),
                'codename': i.split('.')[1]
            })
        all_permiss_list = Permission.objects.filter(
            content_type_id__in=[1, 2, 5]
        ).values()
        for i in all_permiss_list:
            i['permission_explain'] = permission_explain(i['codename'])
        context = {
            'user': user,
            'user_permiss_list': data,
            'all_permiss_list': all_permiss_list
        }
        temp_name = 'admin/permission_admin.html'
    else:
        context = {}
        temp_name = 'admin/error.html'
    return render(
        request,
        temp_name,
        context=context
    )


@login_required(login_url='/index')
def permission_control(request, method, permiss, nid):
    '''
    user permissoin controller,add and remove user permisson for someone
    '''
    return_data = {
        'code': 1,
        'msg': 'illegal request'
    }
    if method not in ['add', 'remove']:
        return JsonResponse(return_data)

    if request.user.has_perm('auth.add_user') and request.user.has_perm('auth.change_user'):
        user = User.objects.get(id=nid)
        if user:
            user_permiss = Permission.objects.get(codename=permiss)
            if method == 'add':
                res = user.user_permissions.add(user_permiss)
            elif method == 'remove':
                res = user.user_permissions.remove(user_permiss)

        if not res:
            return_data['code'] = 0
            return_data['msg'] = 'ok'
            return JsonResponse(return_data)
        else:
            return JsonResponse(return_data)
    else:
        return JsonResponse({
            'code':1,
            'msg':'permission error'
        })


def permission_explain(permiss):
    '''
    permission chinese explain
    '''
    if not permiss:
        return None

    x = permiss.split('_')
    act_data = {
        'add': '新增',
        'change': '修改',
        'view': '查看',
        'delete': '删除'
    }
    res_data = {
        'vminfo': '虚拟机',
        'hostinfo': '主机',
        'user': '用户'
    }
    return act_data[x[0]]+res_data[x[1]]
