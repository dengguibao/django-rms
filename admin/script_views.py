from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from admin.file_view import format_file_size
import time
import os

@login_required
def get_file_list(request, path):
    path=path.replace(',', '/')
    if os.path.isdir(path) is False:
        return JsonResponse({
            'code':1,
            'msg':'path is not directory'
        })

    file_list = os.listdir(path)

    data = {
        'data': [],
        'code': 0,
        'msg': 'success'
    }
    for i in file_list:
        file = os.path.join(path, i)
        if os.path.isdir(file):
            data['data'].append({
                'type': 'dir',
                'name': i
            })
        if os.path.isfile(file):
            data['data'].append({
                'type': 'file',
                'name': i,
                'size': format_file_size(os.path.getsize(file)),
                'create_date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(file)))
            })
    return JsonResponse(data)


@login_required
def view_file(request, path):
    try:
        with open(path.replace(',', '/'), 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return render(request, 'admin/file_view_text.html', {
            'filename': path.split(',')[-1],
            'content': content
        })
    except:
        raise Http404
