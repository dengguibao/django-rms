from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import VmInfo, HostInfo
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User, Permission


def index(request):
    return render(request, 'admin/index.html')


def render_static_temp_view(request, temp_name):
    '''
    新增物理机和虚拟机对应的前端ＵＩ路由
    '''
    return render(request, 'admin/%s.html' % (temp_name))


def render_view(request, form_name, nid):
    if form_name not in ['vm', 'host', 'user']:
        return HttpResponse('object not found')

    temp_name = 'admin/add_or_edit_%s.html' % (form_name)
    if form_name == 'vm':
        vm_obj = VmInfo.objects.get(id=nid)
        host_obj = HostInfo.objects.get(id=vm_obj.host_id)
        esxi_list = HostInfo.objects.filter(cluster_tag=host_obj.cluster_tag)
        return render(
            request,
            temp_name,
            {
                'vm_obj': vm_obj,
                'cluster_tag': host_obj.cluster_tag,
                'esxi_list': esxi_list
            }
        )
    elif form_name == 'host':
        host_obj = HostInfo.objects.get(id=nid)
        return render(
            request,
            temp_name,
            {
                'host_obj': host_obj,
            }
        )
    elif form_name == 'user':
        return render(
            request,
            temp_name,
            context={
                'user': User.objects.get(id=nid)
            }
        )


def delete(request, form_name, nid):

    return_json = {
        'code': 1,
        'msg': 'fail'
    }
    if form_name not in ['vm', 'host', 'user']:
        return JsonResponse(return_json)

    if form_name == 'vm':
        res = VmInfo.objects.get(id=nid).delete()
    elif form_name == 'host':
        res = HostInfo.objects.get(id=nid).delete()
    elif form_name == 'user':
        res = User.objects.get(id=nid).delete()

    if res[0] >= 0:
        return_json['msg'] = 'ok'
        return_json['code'] = 0
    return JsonResponse(return_json)


def create_or_update(request, form_type):
    '''
    新增物理机和虚拟机对应的post事件
    '''
    return_json = {
        'code': 1,
        'msg': 'fail'
    }
    if request.method != 'POST' or form_type not in ['vm', 'host', 'user']:
        return JsonResponse(return_json)

    post_data = request.POST.dict()
    del post_data['csrfmiddlewaretoken']
    del post_data['id']

    nid = int(request.POST.get('id', 0))

    if nid == 0:
        act = 'create'
    else:
        act = 'update'

    if form_type == 'host':
        model = HostInfo
    elif form_type == 'vm':
        model = VmInfo
        del post_data['cluster_tag']
    elif form_type == 'user':
        model = User

    if act == 'create':
        res = model.objects.create(**post_data)
    elif act == 'update':
        res = model.objects.filter(id=nid).update(**post_data)
    else:
        return_json['msg'] = 'illegal request'
        return_json['code'] = 1

    if (act == 'update' and res) or (act == 'create' and res.id):
        return_json['code'] = 0
        return_json['msg'] = act+' success'

    return JsonResponse(return_json)


def get_user_list(request):
    user_list = User.objects.all()
    return render(request, 'admin/list_users.html', context={
        "obj": user_list
    })


def get_hosts_list(request, dev_type, flag):
    '''
    ajax获得所有主机列表
    dev_type 设备类型，可以指定host或者vm（物理机和虚拟机）
    flag　标记，如果是物理机则指定cluster_tag，虚拟机则指明是format cluster_host
    '''
    page_size = settings.PAGE_SIZE
    return_json = {
        'code': 1,
        'msg': 'device type is none'
    }
    if dev_type not in ['host', 'vm'] or len(flag) <= 0:
        return JsonResponse(return_json)
    if dev_type == 'host':
        if flag not in ['cs', 'xh', 'test', 'none', 'all']:
            return_json['msg'] = 'illegal request'
            return JsonResponse(return_json)
        if flag == 'all':
            rs = HostInfo.objects.all()
        else:
            rs = HostInfo.objects.filter(cluster_tag=flag)
        return_json['data'] = [i for i in rs.values()]
        return_json['code'] = 0
        return_json['msg'] = 'ok'
    # get all vms
    elif dev_type == 'vm':
        if '_all' in flag:
            x = flag.split('_')
            if x[0] not in ['cs', 'xh', 'test']:
                return_json['msg'] = 'illegal request'
                return JsonResponse(return_json)
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
        return_json['data'] = vm_data
        return_json['page_data'] = {
            'rs_count': p.count,
            'page_count': p.num_pages,
            'page_size': page_size,
            'curr_page': page,
        }
        return_json['code'] = 0
        return_json['msg'] = 'ok'
    return JsonResponse(return_json)


def search(request, dev_type, keyword):
    if dev_type not in ['vm', 'host'] or len(keyword) == 0:
        return JsonResponse({
            'code': 1,
            'msg': 'illegal request'
        })
    if dev_type == 'vm':
        model = VmInfo
    else:
        model = HostInfo

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
        return_json = {
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
    else:
        res = model.objects.filter(
            Q(host_ip__contains=keyword) |
            Q(hostname__contains=keyword) |
            Q(idrc_ip__contains=keyword)
        )
        return_json = {
            'data': [i for i in res.values()],
            'code': 0,
            'msg': 'ok'
        }
    return JsonResponse(return_json)


def permissin_admin_view(request, nid):
    user = User.objects.get(id=nid)
    user_permission_list = user.get_all_permissions()
    data=[]
    for i in user_permission_list:
        data.append({
            'permiss_explain' : permission_explain(i.split('.')[1]),
            'codename' : i.split('.')[1]
        })

    all_permiss_list = Permission.objects.filter(
        content_type_id__in=[1, 2, 5]
    ).values()
    for i in all_permiss_list:
        i['permission_explain'] = permission_explain(i['codename'])
    return render(
        request,
        'admin/permission_admin.html',
        context={
            'user': user,
            'user_permiss_list': data,
            'all_permiss_list': all_permiss_list
        }
    )


def permission_control(request, method, permiss, nid):

    return_data = {
        'code': 1,
        'msg': 'illegal request'
    }
    if method not in ['add', 'remove']:
        return JsonResponse(return_data)
    user = User.objects.get(id=nid)
    if user:
        user_permiss = Permission.objects.get(codename=permiss)
        if method == 'add':
            res = user.user_permissions.add(user_permiss)
        elif method == 'remove':
            res = user.user_permissions.remove(user_permiss)
    print(res)
    if not res:
        return_data['code'] = 0
        return_data['msg'] = 'ok'
        return JsonResponse(return_data)
    else:
        return JsonResponse(return_data)



def permission_explain(permiss):
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
