from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required()
def webssh(request):    
    return render(request, 'admin/shell.html', {
        'host':request.GET.get('host', ''),
        'type':request.GET.get('type', ''),
        'port':request.GET.get('port', '22'),
        'user':request.GET.get('user', 'root'),
        'password': request.GET.get('password', None)
    })