from django.shortcuts import render


def webssh(request):    
    return render(request, 'admin/shell.html', {
        'host':request.GET.get('host', ''),
        'port':request.GET.get('port', '22'),
        'user':request.GET.get('user', 'root'),
        'password': request.GET.get('password', None)
    })