from django.http import JsonResponse, Http404, FileResponse
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
                'name': i,
                'size': format_file_size(os.path.getsize(file)),
                'create_date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(file)))
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
    txt_file_type = [
        'md',
        'conf',
        'log',
        'txt',
        'desktop',
        'sh',
        'py',
        'php',
        'js',
        'css',
        'html',
        'htm',
        'go',
        'json',
        'xml'
    ]
    if path.split(',')[-1].split('.')[-1] in txt_file_type:
        try:
            with open(path.replace(',', '/'), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return render(request, 'admin/file_view_text.html', {
                'filename': path.split(',')[-1],
                'content': content
            })
        except:
            raise Http404
    else:
        try:
            file = open(path.replace(',', '/'), 'rb')
            response = FileResponse(file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{}"'.format(
                path.split(',')[-1].encode('utf-8').decode('ISO-8859-1')
            )
            return response
        except:
            raise Http404
