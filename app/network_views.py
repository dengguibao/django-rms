from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .common import *


@login_required()
def list_device_info(request, form_name):
    """render lannetworks list
    
    Arguments:
        request {object} -- wsgi http request object
    
    Returns:
        html -- render html template
    """
    branch_id = request.GET.get('branch_id', 0)
    keyword = request.GET.get('keyword', None)
    page_size = settings.PAGE_SIZE
    page = int(request.GET.get('page', 1))
    export = request.GET.get('export', None)

    if form_name not in register_form:
        return render(
            request, 'admin/error.html',
            {'error_msg': 'Illegal request'}
        )

    perm_action_flag = 'view'
    model = register_form[form_name]['model']
    perm = register_form[form_name]['perm'] % perm_action_flag
    if not request.user.has_perm(perm):
        return render(
            request, 'admin/error.html',
            {
                'error_msg': 'permission denied'
            }
        )
    if form_name in ['branch', 'bank_private']:
        res_list = model.objects.all().order_by('-id')
    else:
        res_list = model.objects.all().select_related('branch').order_by('-id')

    if form_name == 'branch' and keyword:
        res_list = res_list.filter(
            Q(name__contains=keyword) |
            Q(address__contains=keyword)
        )
    if form_name == 'bank_private' and keyword:
        res_list = res_list.filter(
            Q(name__contains=keyword) |
            Q(user_ip_addr__contains=keyword) |
            Q(global_ip__contains=keyword)
        )
    if form_name == 'lan_net' and keyword:
        res_list = res_list.filter(
            Q(ip__contains=keyword)
        )
    if form_name == 'wan_net' and keyword:
        res_list = res_list.filter(
            Q(ip__contains=keyword) |
            Q(bandwidth__contains=keyword) |
            Q(rent__contains=keyword) |
            Q(contact__contains=keyword) |
            Q(isp__contains=keyword)
        )
    if form_name == 'net_devices' and keyword:
        res_list = res_list.filter(
            Q(sn__contains=keyword) |
            Q(ip__contains=keyword) |
            Q(device_model__contains=keyword) |
            Q(brand__contains=keyword) |
            Q(device_type__contains=keyword) |
            Q(hostname__contains=keyword)
        )

    if not keyword:
        pass

    if int(branch_id) == 0:
        pass
    else:
        res_list = res_list.filter(branch_id=branch_id)

    if export:
        wb = export_to_file(form_name, res_list)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=%s.xls' % form_name
        output = BytesIO()
        wb.save(output)

        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    p = Paginator(res_list, page_size)

    return render(
        request,
        'admin/list_%s.html' % form_name,
        {
            'obj': p.page(page),
            'branch_data': Branch.objects.filter(isenable=1),
            'keyword': keyword,
            'current_branch_id': int(branch_id),
            'rs_count': p.count,
            'page_size': page_size,
            'curr_page': page
        }
    )


def update_port_desc(request):
    id = request.GET.get('id', None)
    port_index = request.GET.get('port_index', None)
    port_desc = request.GET.get('port_desc', None)
    branch_id = request.GET.get('branch_id', None)
    device_id = request.GET.get('device_id', None)

    branch_obj = Branch.objects.get(id=branch_id)
    device_obj = NetworkDevices.objects.get(id=device_id)

    if id:
        res = PortDesc.objects.filter(id=id).update(
            branch=branch_obj,
            device=device_obj,
            desc=port_desc,
            index=port_index
        )
    else:
        res = PortDesc.objects.create(
            branch=branch_obj,
            device=device_obj,
            desc=port_desc,
            index=port_index
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


@login_required()
def get_port_desc_list(request, device_id):
    res = PortDesc.objects.filter(device=device_id)
    return JsonResponse({
        'code': 0,
        'data': list(res.values())
    })


@login_required()
def get_device_list(request, branch_id):
    res = NetworkDevices.objects.filter(branch_id=branch_id)
    return JsonResponse({
        'code': 0,
        'data': list(res.values())
    })