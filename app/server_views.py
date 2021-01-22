from io import BytesIO
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

    if host_type not in ['host', 'vm'] or len(flag) <= 0:
        return JsonResponse({
            'code': 1,
            'msg': 'illegal request'
        })

    perm_action_flag = 'view'
    perm = register_form[host_type]['perm'] % perm_action_flag
    model = register_form[host_type]['model']

    if not request.is_ajax() or not request.user.has_perm(perm):
        return JsonResponse({
            'msg': 'permission denied',
            'code': 1
        })

    page_size = request.GET.get('page_size', settings.PAGE_SIZE)
    keyword = request.GET.get('keyword', None)
    page = int(request.GET.get('page', 1))
    rs = None

    if host_type == 'host':
        if flag == 'all':
            rs = model.objects.all()
        else:
            rs = model.objects.filter(cluster_tag=flag)
        rs.order_by('hostname')
        
    if host_type == 'vm':
        if '_all' in flag:
            rs = model.objects.filter(host__cluster_tag=flag.split('_')[0]).select_related().order_by('-pub_date')
        elif flag == 'all':
            rs = model.objects.exclude(host__cluster_tag='none').select_related().order_by('-pub_date')
        else:
            rs = model.objects.filter(host__hostname=flag).select_related().order_by('-pub_date')

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

    p = Paginator(rs, page_size)
    query_set = p.page(page)

    model_fields = get_model_fields(host_type)
    data = []
    for i in query_set:
        tmp = {}
        for field in model_fields:
            if not hasattr(i, field):
                continue

            if model_fields[field]['choice']:
                v = eval('i.get_%s_display()' % field)
            elif model_fields[field]['relate_name']:
                try:
                    v = eval('i.%s.hostname' % model_fields[field]['relate_name'])
                except:
                    v = eval('i.%s.name' % model_fields[field]['relate_name'])
            else:
                v = eval('i.%s' % field)

            tmp[field] = v
        data.append(tmp)
        del tmp

    context = {
        'data': data,
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
    export_file_name = None
    if host_type not in ['vm', 'host']:
        return render(request, 'admin/error.html')

    model = register_form[host_type]['model']

    res = None
    if host_type == 'host':
        res = model.objects.all()
        export_file_name = 'host_info.xls'
    if host_type == 'vm':
        export_file_name = 'vms_info.xls'
        res = model.objects.all().select_related('host')

    if res:
        wb = export_to_file(host_type, res)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=%s' % export_file_name
        output = BytesIO()
        wb.save(output)

        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    return render(request, 'admin/error.html', {'error_msg': '非法操作'})


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
