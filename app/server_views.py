from io import BytesIO
import xlwt
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.conf import settings
from .global_views import data_struct
from .models import VmInfo, HostInfo, ClusterInfo


@login_required()
def get_hosts_list(request, dev_type, flag):
    """get all host and virtual machine resource
    
    Arguments:
        request {object} -- wsgi http request object
        dev_type {str} -- device type, vm or hosts
        flag {str} -- e.g. cs_all or esxi01.cs.hnyongxiong.com
    
    Returns:
        json -- specific type json object
    """

    perm = {
        'vm': 'app.view_vminfo',
        'host': 'app.view_hostinfo'
    }
    # permission verify
    if not request.user.has_perm(perm[dev_type]):
        return JsonResponse({
            'msg': 'permission denied',
            'code': 1
        })

    page_size = settings.PAGE_SIZE
    return_data = {
        'code': 1,
        'msg': 'illegal request'
    }
    if dev_type not in ['host', 'vm'] or len(flag) <= 0:
        return JsonResponse(return_data)

    res_cluster = ClusterInfo.objects.filter(is_active=0).values('name', 'tag')
    cluster_array = {i['tag']: i['name'] for i in res_cluster}

    if dev_type == 'host':
        if flag not in cluster_array and flag not in ['all', 'none']:
            return JsonResponse(return_data)
        if flag == 'all':
            rs = HostInfo.objects.order_by('hostname').all()
        else:
            rs = HostInfo.objects.filter(cluster_tag=flag).order_by('hostname')
        p = Paginator(rs.values(), page_size)
        page = int(request.GET.get('page', 1))
        data_obj = p.page(page)
        return_data['page_data'] = {
            'rs_count': p.count,
            'page_count': p.num_pages,
            'page_size': page_size,
            'curr_page': page,
        }
        return_data['data'] = list(data_obj)
        return_data['code'] = 0
        return_data['msg'] = 'ok'
    # get virtual machine info
    elif dev_type == 'vm':
        if '_all' in flag:
            x = flag.split('_')
            if x[0] not in cluster_array:
                return JsonResponse(return_data)
            else:
                vm_obj = VmInfo.objects.filter(host__cluster_tag=x[0]).order_by('-pub_date')
                host_obj = HostInfo.objects.filter(cluster_tag=x[0])
        elif flag == 'all':
            vm_obj = VmInfo.objects.exclude(host__cluster_tag='none').order_by('-pub_date')
            host_obj = HostInfo.objects.all().order_by('pub_date')
        else:
            vm_obj = VmInfo.objects.filter(host__hostname=flag).order_by('-pub_date')
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

    return JsonResponse(return_data)


@login_required()
def export(request, dev_type):
    backup_data_struct = data_struct()
    export_file_name = None
    if dev_type not in ['vm', 'host']:
        return render(request, 'admin/error.html')

    wb = xlwt.Workbook(encoding='utf8')
    sheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)

    if dev_type == 'host':
        res = HostInfo.objects.all().values()
        export_file_name = 'host_info.xls'
    if dev_type == 'vm':
        export_file_name = 'vms_info.xls'
        res = VmInfo.objects.all().values()

        host_obj = HostInfo.objects.all()
        esxi_kvp = {i.id: i.hostname for i in host_obj}

    res_cluster = ClusterInfo.objects.filter(is_active=0).values('name', 'tag')
    cluster_tag = {i['tag']: i['name'] for i in res_cluster}
    cluster_tag['none'] = '独立服务器'
    status = ['开机', '关机']
    if res:
        column = 0
        for title in backup_data_struct[dev_type]:
            sheet.write(0, column, backup_data_struct[dev_type][title])
            column += 1

        column = 0
        data_row_num = 1
        for res_row in res:
            for key in backup_data_struct[dev_type]:
                if key == 'cluster_tag':
                    sheet.write(data_row_num, column, cluster_tag[res_row[key]])
                elif key == 'host_id':
                    sheet.write(data_row_num, column, esxi_kvp[res_row[key]])
                elif key == 'vm_status' or key == 'dev_status':
                    sheet.write(data_row_num, column, status[res_row[key]])
                else:
                    sheet.write(data_row_num, column, res_row[key])
                column += 1
            column = 0
            data_row_num += 1
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=%s' % export_file_name
    output = BytesIO()
    wb.save(output)

    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


@login_required()
def search(request, dev_type, keyword):
    """
    according keyword search host or virtual machine
    
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

    perm = {
        'vm': 'app.view_vminfo',
        'host': 'app.view_hostinfo'
    }
    # permission verify
    if not request.user.has_perm(perm[dev_type]):
        return JsonResponse({
            'msg': 'permission denied',
            'code': 1
        })

    mod = {
        'vm': VmInfo,
        'host': HostInfo
    }

    model = mod[dev_type]

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
            Q(idrac_ip__contains=keyword)
        )
        return_data = {
            'data': [i for i in res.values()],
            'code': 0,
            'msg': 'ok'
        }
    return JsonResponse(return_data)
