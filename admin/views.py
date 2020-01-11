from django.shortcuts import render
from django.http import JsonResponse
from .models import VmInfo, HostInfo
from django.core.paginator import Paginator
from django.db.models import Q

# Create your views here.


def index(request):
    return render(request, 'admin/index.html')


def render_temp(request, temp_name):
    '''
    新增物理机和虚拟机对应的前端ＵＩ路由
    '''
    return render(request, 'admin/%s.html' % (temp_name))


def render_edit(request, form_name, nid):
    if form_name not in ['vm', 'host']:
        return
    temp_name = 'admin/edit_%s.html' % (form_name)
    if form_name == 'vm':
        vm_obj = VmInfo.objects.get(id=nid)
        host_obj = HostInfo.objects.get(id=vm_obj.host_id)
        print(vm_obj.vm_disk)
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
    else:
        host_obj = HostInfo.objects.get(id=nid)
        return render(
            request,
            temp_name,
            {
                'host_obj': host_obj,
            }
        )


def delete(request, form_name, nid):

    return_json = {
        'code': 1,
        'msg': 'fail'
    }
    if form_name not in ['vm', 'host']:
        return JsonResponse(return_json)
    if form_name == 'vm':
        res = VmInfo.objects.get(id=nid).delete()
    else:
        res = HostInfo.objects.get(id=nid).delete()
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
    if form_type not in ['vm', 'host']:
        return JsonResponse(return_json)

    post_data = request.POST.dict()
    del post_data['csrfmiddlewaretoken']
    nid = request.POST.get('id', 0)
    if nid == 0:
        act = 'create'
    else:
        del post_data['id']
        act = 'update'

    if form_type == 'host':
        model = HostInfo
    else:
        model = VmInfo
        del post_data['cluster_tag']

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


def get_hosts_list(request, dev_type, flag):
    '''
    ajax获得所有主机列表
    dev_type 设备类型，可以指定host或者vm（物理机和虚拟机）
    flag　标记，如果是物理机则指定cluster_tag，虚拟机则指明是format cluster_host
    '''
    page_size = 15
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
        # page_size = 15
        # p = Paginator(res, page_size)
        # page = int(request.GET.get('page', 1))
        # data_obj = p.page(page)
        vm_data = []
        for i in res.values():
            i["esxi_host_name"] = esxi_kvp[i['host_id']]
            vm_data.append(i)
        return_json = {
            'data': vm_data,
            'code': 0,
            'msg': 'ok',
            'page_data':{
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
