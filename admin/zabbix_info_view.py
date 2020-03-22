from django.shortcuts import render
from django.conf import settings
from .models import VmInfo


def zabbix_server_info_view(request, id):
    
    res = VmInfo.objects.get(id=id)


    if not res:
        return render(request, 'admin/error.html')
    else:
        return render(request, 'admin/server_info.html', {
            'ip':res.vm_ip,
            'zabbix_api':settings.ZABBIX_API
        })
        