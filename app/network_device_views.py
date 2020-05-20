from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
from .models import NetworkDevices, Branch, LanNetworks, WanNetworks


@login_required()
def list_device_info(request, form_name):
    """render lannetworks list
    
    Arguments:
        request {object} -- wsgi http request object
    
    Returns:
        html -- render html template
    """
    branch_id = request.GET.get('branch_id', 0)
    keyworyd = request.GET.get('keyword', None)
    page_size = settings.PAGE_SIZE
    page = int(request.GET.get('page', 1))

    app_name = 'app'
    perm_action = 'view'

    perms = {
        'branch': '%s.%s_branch',
        'lan_net': '%s.%s_lannetworks',
        'wan_net': '%s.%s_wannetworks',
        'net_devices': '%s.%s_networkdevices',
    }

    models = {
        'branch': Branch,
        'lan_net': LanNetworks,
        'wan_net': WanNetworks,
        'net_devices': NetworkDevices,
    }

    if form_name not in perms:
        return render(
            request, 'admin/error.html',
            {'error_msg': 'Illegal request'}
        )

    if not request.user.has_perm(perms[form_name] % (app_name, perm_action)):
        return render(
            request, 'admin/error.html',
            {
                'error_msg': 'permission denied'
            }
        )

    res_list = models[form_name].objects.all().order_by('-id')

    if form_name == 'branch' and keyworyd:
        res_list = res_list.filter(
            Q(name__contains=keyworyd) |
            Q(address__contains=keyworyd)
        )
    elif form_name == 'lan_net' and keyworyd:
        res_list = res_list.filter(
            Q(ip__contains=keyworyd)
        )
    elif form_name == 'wan_net' and keyworyd:
        res_list = res_list.filter(
            Q(ip__contains=keyworyd) |
            Q(bandwidth__contains=keyworyd) |
            Q(rent__contains=keyworyd) |
            Q(contact__contains=keyworyd) |
            Q(isp__contains=keyworyd)
        )
    elif form_name == 'net_devices' and keyworyd:
        res_list = res_list.filter(
            Q(sn__contains=keyworyd) |
            Q(ip__contains=keyworyd) |
            Q(device_model__contains=keyworyd) |
            Q(brand__contains=keyworyd) |
            Q(device_type__contains=keyworyd) |
            Q(hostname__contains=keyworyd)
        )

    if not keyworyd:
        pass

    if int(branch_id) == 0:
        pass
    else:
        res_list = res_list.filter(branch_id=branch_id)

    p = Paginator(res_list, page_size)

    return render(
        request, 
        'admin/list_%s.html' % form_name, 
        {
            'obj': p.page(page),
            'branch_data': Branch.objects.filter(isenable=1),
            'keyword': keyworyd,
            'current_branch_id': int(branch_id),
            'rs_count': p.count,
            'page_size': page_size,
            'curr_page': page
        }
    )
