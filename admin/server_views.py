from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.conf import settings

from .models import VmInfo, HostInfo

from io import BytesIO
import xlwt


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


def export(request, dev_type):
    if dev_type not in ['vm', 'host']:
        return render(request, 'admin/error.html')

    wb = xlwt.Workbook(encoding='utf8')
    sheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)

    if dev_type == 'host':
        res = HostInfo.objects.all()
        export_file_name = 'host_info.xls'
    if dev_type == 'vm':
        export_file_name = 'vms_info.xls'
        res = VmInfo.objects.all()

    # 导出虚拟机
    if res and dev_type == 'vm':
        host_obj = HostInfo.objects.all()
        esxi_kvp = {i.id: i.hostname for i in host_obj}
        sheet.write(0, 0, '主机名')
        sheet.write(0, 1, 'IP')
        sheet.write(0, 2, 'vlan tag')
        sheet.write(0, 3, 'vlan id')
        sheet.write(0, 4, '宿主机')
        sheet.write(0, 5, 'cpu')
        sheet.write(0, 6, '硬盘')
        sheet.write(0, 7, '内存')
        sheet.write(0, 8, '操作系统')
        sheet.write(0, 9, 'zabbix agent')
        sheet.write(0, 10, '建立时间')
        sheet.write(0, 11, '申请人')
        sheet.write(0, 12, '用途')
        sheet.write(0, 13, '备注')
        data_row = 1
        for i in res:
            sheet.write(data_row, 0, i.vm_hostname)
            sheet.write(data_row, 1, i.vm_ip)
            sheet.write(data_row, 2, i.vlan_tag)
            sheet.write(data_row, 3, i.vlan_id)
            sheet.write(data_row, 4, esxi_kvp[i.host_id])
            sheet.write(data_row, 5, i.vm_cpu)
            sheet.write(data_row, 6, i.vm_disk)
            sheet.write(data_row, 7, i.vm_memory)
            sheet.write(data_row, 8, i.vm_os)
            sheet.write(data_row, 9, i.vm_monitor)
            sheet.write(data_row, 10, i.pub_date)
            sheet.write(data_row, 11, i.vm_register)
            sheet.write(data_row, 12, i.vm_intention)
            sheet.write(data_row, 13, i.vm_desc)
            data_row += 1
    # 导出宿主机（祼机）
    if res and dev_type == 'host':
        sheet.write(0, 0, '主机名')
        sheet.write(0, 1, 'sn')
        sheet.write(0, 2, 'idrc ip')
        sheet.write(0, 3, 'host ip')
        sheet.write(0, 4, '所属集群')
        sheet.write(0, 5, 'cpu')
        sheet.write(0, 6, '硬盘')
        sheet.write(0, 7, '内存')
        sheet.write(0, 8, '操作系统')
        sheet.write(0, 9, '设备型号')
        sheet.write(0, 10, '建立时间')
        sheet.write(0, 11, '备注')
        cluster_tag = {
            'cs':'长沙',
            'xh':'新化',
            'test':'开发测试',
            'none':'裸机'
        }
        data_row = 1
        for i in res:
            sheet.write(data_row, 0, i.hostname)
            sheet.write(data_row, 1, i.sn)
            sheet.write(data_row, 2, i.idrc_ip)
            sheet.write(data_row, 3, i.host_ip)
            sheet.write(data_row, 4, cluster_tag[i.cluster_tag])
            sheet.write(data_row, 5, i.cpu)
            sheet.write(data_row, 6, i.disk)
            sheet.write(data_row, 7, i.memory)
            sheet.write(data_row, 8, i.os)
            sheet.write(data_row, 9, i.dev_model)
            sheet.write(data_row, 10, i.pub_date)
            sheet.write(data_row, 11, i.desc)
            data_row += 1

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=%s' % (export_file_name)
    output = BytesIO()
    wb.save(output)

    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


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
