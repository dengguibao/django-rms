from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import NetworkDevices


@login_required()
def list_net_devices_view(request):
    """render net_devices list
    
    Arguments:
        request {object} -- wsgi http request object
    
    Returns:
        html -- render html template
    """
    if request.user.has_perm('app.view_networkdevices'):
        res_list = NetworkDevices.objects.all()

        print(res_list)
        temp_name = 'admin/list_net_devices.html'
        context = {
            'obj': res_list
        }
    else:
        temp_name = 'admin/error.html'
        context = {}

    return render(
        request,
        temp_name,
        context=context
    )