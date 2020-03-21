from django.shortcuts import render
from .models import VmInfo


def zabbix_server_info_view(request, id):
    
    res = VmInfo.objects.get(id=id)


    if not res:
        return render(request, 'admin/error.html')
    else:
        return render(request, 'admin/server_info.html', {
            'ip':res.vm_ip,
            'url':'http://172.31.19.254/zabbix/api_jsonrpc.php'
        })
        