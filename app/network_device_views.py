from io import BytesIO
import xlwt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.conf import settings
from .models import NetworkDevices, Branch, LanNetworks, WanNetworks
from .global_views import perms, models


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

    if form_name not in perms:
        return render(
            request, 'admin/error.html',
            {'error_msg': 'Illegal request'}
        )
        
    perm_action_flag = 'view'
    if not request.user.has_perm(perms[form_name] % perm_action_flag ):
        return render(
            request, 'admin/error.html',
            {
                'error_msg': 'permission denied'
            }
        )
    if form_name == 'branch':
        res_list = models[form_name].objects.all().order_by('-id')
    else:
        res_list = models[form_name].objects.all().select_related('branch').order_by('-id')

    if form_name == 'branch' and keyword:
        res_list = res_list.filter(
            Q(name__contains=keyword) |
            Q(address__contains=keyword)
        )
    elif form_name == 'lan_net' and keyword:
        res_list = res_list.filter(
            Q(ip__contains=keyword)
        )
    elif form_name == 'wan_net' and keyword:
        res_list = res_list.filter(
            Q(ip__contains=keyword) |
            Q(bandwidth__contains=keyword) |
            Q(rent__contains=keyword) |
            Q(contact__contains=keyword) |
            Q(isp__contains=keyword)
        )
    elif form_name == 'net_devices' and keyword:
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
        wb = xlwt.Workbook(encoding='utf8')
        sheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)
        # column = 0
        # backup_data_struct = data_struct()
        # for title in backup_data_struct[t]:
        #     sheet.write(0, column, backup_data_struct[t][title])
        #     column += 1

        column = 0
        data_row_num = 0
        for i in res_list.values():
            for key,value in i.items():
                if key == 'branch_id':
                    sheet.write(
                        data_row_num, 
                        column,
                        res_list[data_row_num].branch.name
                    )
                elif key == 'id':
                    sheet.write(
                        data_row_num, 
                        column,
                        data_row_num+1
                    )
                elif key == 'isenable':
                    pass
                else:
                    sheet.write(data_row_num, column, value)
                column += 1
            column = 0
            data_row_num += 1
        
       
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
