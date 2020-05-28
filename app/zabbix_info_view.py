from django.shortcuts import render
from .models import VmInfo


def zabbix_server_info_view(request, vm_id):
    """get vminfo object according vm_id,and then get vm running status accord vminfo.vm_ip

    Arguments:
        request {object} -- wsgi request object
        vm_id {int} -- vminfo.id

    Returns:
        html -- html response view
    """
    res = VmInfo.objects.get(id=vm_id)

    if not res:
        return render(request, 'admin/error.html')
    else:
        return render(request, 'admin/server_info.html', {
            'ip': res.vm_ip
        })
