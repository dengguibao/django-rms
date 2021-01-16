from io import BytesIO
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .common import *

from django.db.models import Q


@login_required()
def list_monitor_info(request):
    branch_id = request.GET.get('branch_id', 0)
    keyword = request.GET.get('keyword', None)
    page_size = settings.PAGE_SIZE
    page = int(request.GET.get('page', 1))
    export = request.GET.get('export', None)

    perm_action_flag = 'view'
    model = register_form['monitor']['model']
    perm = register_form['monitor']['perm'] % perm_action_flag
    if not request.user.has_perm(perm):
        return render(
            request, 'admin/error.html',
            {
                'error_msg': 'permission denied'
            }
        )

    res_list = model.objects.all().select_related('branch').order_by('-id')

    if keyword:
        res_list = res_list.filter(
            Q(dev_model__contains=keyword) |
            Q(ip__contains=keyword) |
            Q(desc=keyword)
        )

    if int(branch_id) == 0:
        pass
    else:
        res_list = res_list.filter(branch_id=branch_id)

    if export:
        wb = export_to_file('monitor', res_list)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=monitor.xls'
        output = BytesIO()
        wb.save(output)

        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    p = Paginator(res_list, page_size)

    return render(
        request,
        'admin/list_monitor.html',
        {
            'obj': p.page(page),
            'branch_data': register_form['branch']['model'].objects.filter(isenable=1),
            'keyword': keyword,
            'current_branch_id': int(branch_id),
            'rs_count': p.count,
            'page_size': page_size,
            'curr_page': page
        }
    )


@login_required()
def get_monitor_account_list(request, monitor_id):
    res = MonitorAccount.objects.filter(monitor_id=monitor_id)
    return JsonResponse({
        'code': 0,
        'data': list(res.values())
    })


@login_required()
def update_monitor_account(request):
    id = request.GET.get('id', None)
    username = request.GET.get('username', None)
    password = request.GET.get('password', None)
    channel = request.GET.get('channel', None)
    desc = request.GET.get('desc', None)
    monitor = request.GET.get('monitor_id', None)
    if id:
        res = MonitorAccount.objects.update(
            username=username,
            password=password,
            channel=channel,
            desc=desc
        )
    else:
        res = MonitorAccount.objects.create(
            monitor=Monitor.objects.get(id=monitor),
            username=username,
            password=password,
            channel=channel,
            desc=desc
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
