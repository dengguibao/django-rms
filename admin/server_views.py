from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.conf import settings

from .models import VmInfo, HostInfo

def get_hosts_list(request, dev_type, flag):
    """get all host and virtual machine resource
    
    Arguments:
        request {object} -- wsgi http request object
        dev_type {str} -- device type, vm or hosts
        flag {str} -- e.g. cs_all or esxi01.cs.hnyongxiong.com
    
    Returns:
        json -- specific type json object
    """
    page_size = settings.PAGE_SIZE
    return_data = {
        'code': 1,
        'msg': 'illegal request'
    }

    if dev_type not in ['host', 'vm'] or len(flag) <= 0:
        return JsonResponse(return_data)

    if dev_type == 'host':
        if flag not in ['cs', 'xh', 'test', 'none', 'all']:
            return JsonResponse(return_data)
        if flag == 'all':
            rs = HostInfo.objects.order_by('hostname').all()
        else:
            rs = HostInfo.objects.filter(cluster_tag=flag).order_by('hostname')
        rs_data_set = [i for i in rs.values()]
        return_data['data'] = rs_data_set
        return_data['code'] = 0
        return_data['msg'] = 'ok'
    # get virtual machine info
    elif dev_type == 'vm':
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


# @login_required()
def search(request, dev_type, keyword):
    """ accroding keyword search host or virtual machine
    
    Arguments:
        request {object} -- wsgi http request object
        dev_type {str} -- deivce type just contain vm or hosts
        keyword {str} -- search keyword
    
    Returns:
        json -- json object
    """
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