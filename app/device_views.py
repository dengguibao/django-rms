from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import NetworkDevices, Branch, LanNetworks, WanNetworks

@login_required()
def list_device_info(request, form_name):
    """render lannetworks list
    
    Arguments:
        request {object} -- wsgi http request object
    
    Returns:
        html -- render html template
    """
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
        return render(request, 'admin/error.html', {
            'error_msg': 'Illegal request'
        })

    if not request.user.has_perm(perms[form_name] % (app_name, perm_action)):
        return render(request, 'admin/error.html', {
            'error_msg': 'permission denied'
        })
    
    res_list = models[form_name].objects.all()

    return render(
        request,
        'admin/list_%s.html' % form_name,
        {
            'obj': res_list
        }
    )