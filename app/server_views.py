from io import BytesIO
import xlwt
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.conf import settings
from .common import *


@login_required()
def list_hosts_list(request, host_type, flag):
    """get all host and virtual machine resource
    
    Arguments:
        request {object} -- wsgi http request object
        host_type {str} -- host type, vm or host
        flag {str} -- e.g. cs_all or esxi01.cs.hnyongxiong.com
    
    Returns:
        json -- specific type json object
    """

    perm_action_flag = 'view'
    # permission verify
    if not request.is_ajax() or not request.user.has_perm(perms[host_type] % perm_action_flag):
        return JsonResponse({
            'msg': 'permission denied',
            'code': 1
        })

    if host_type not in ['host', 'vm'] or len(flag) <= 0:
        return JsonResponse({
            'code': 1,
            'msg': 'illegal request'
        })

    page_size = request.GET.get('page_size', settings.PAGE_SIZE)
    keyword = request.GET.get('keyword', None)
    page = int(request.GET.get('page', 1))
    rs = None

    if host_type == 'host':
        if flag == 'all':
            rs = HostInfo.objects.all()
        else:
            rs = HostInfo.objects.filter(cluster_tag=flag)
        
    if host_type == 'vm':
        if '_all' in flag:
            rs = VmInfo.objects.filter(host__cluster_tag=flag.split('_')[0]).select_related().order_by('-pub_date')
        elif flag == 'all':
            rs = VmInfo.objects.exclude(host__cluster_tag='none').select_related().order_by('-pub_date')
        else:
            rs = VmInfo.objects.filter(host__hostname=flag).select_related().order_by('-pub_date')

    if keyword:
        if host_type == 'host':
            rs = rs.filter(
                Q(host_ip__contains=keyword) |
                Q(hostname__contains=keyword) |
                Q(idrac_ip__contains=keyword) |
                Q(sn__contains=keyword)
            )
        if host_type == 'vm':
            rs = rs.filter(
                Q(vm_ip__contains=keyword) |
                Q(vm_hostname__contains=keyword)
            )
    
    if host_type == 'host':
        data = rs.order_by('hostname').values()

    if host_type == 'vm':
        data = rs.values()
        # bug: no this follow code,will be large query database
        for i in data:
            pass

        nn = 0
        for i in rs:
            data[nn]['esxi_host_name'] = i.host.hostname
            nn += 1

    p = Paginator(data, page_size)
    query_set = p.page(page)

    context = {
        'data': list(query_set),
        'code': 0,
        'msg': 'ok',
        'page_data': {
            'rs_count': p.count,
            'page_count': p.num_pages,
            'page_size': page_size,
            'curr_page': page,
        }
    }

    return JsonResponse(context)


@login_required()
def export(request, host_type):
    backup_data_struct = data_struct()
    export_file_name = None
    if host_type not in ['vm', 'host']:
        return render(request, 'admin/error.html')

    wb = xlwt.Workbook(encoding='utf8')
    sheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)

    if host_type == 'host':
        res = HostInfo.objects.all()
        export_file_name = 'host_info.xls'
    if host_type == 'vm':
        export_file_name = 'vms_info.xls'
        res = VmInfo.objects.all().select_related('host')

    if res:
        column = 0
        for title in backup_data_struct[host_type]:
            sheet.write(0, column, backup_data_struct[host_type][title])
            column += 1

        column = 0
        data_row_num = 1
        for res_row in res:
            for key in backup_data_struct[host_type]:
                field_value = eval('res_row.%s' % key)
                if key == 'cluster_tag_id':
                    sheet.write(data_row_num, column, res_row.cluster_tag.name)
                elif key == 'host_id':
                    sheet.write(data_row_num, column, res_row.host.hostname)
                elif key == 'vm_status':
                    sheet.write(data_row_num, column, res_row.get_vm_status_display())
                elif key == 'dev_status':
                    sheet.write(data_row_num, column, res_row.get_dev_status_display())
                else:
                    sheet.write(data_row_num, column, field_value)
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
def get_host_interface_list(request, host_id):
    res = HostInterface.objects.filter(host=host_id)
    return JsonResponse({
        'code': 0,
        'data': list(res.values())
    })


@login_required()
def update_host_interface(request):
    id = request.GET.get('id', None)
    ifname = request.GET.get('ifname', None)
    access = request.GET.get('access', None)
    host_id = request.GET.get('host_id', None)
    if id:
        res = HostInterface.objects.update(
            ifname=ifname,
            access=access,
        )
    else:
        res = HostInterface.objects.create(
            host=HostInfo.objects.get(id=host_id),
            ifname=ifname,
            access=access,
        )

    if res:
        return JsonResponse({
            'code': 0,
            'msg': 'success'
        })

    return JsonResponse({
        'code': 1,
        'msg': 'failed'
    })
