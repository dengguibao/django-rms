import os
import time
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings

from .models import FileInfo

TODAY = time.strftime('%Y%m%d', time.localtime())
UPLOAD_PATH = 'uploads'


@login_required()
def upload_file(request):
    if request.method == 'POST':
        local_path = os.path.join(settings.BASE_DIR, UPLOAD_PATH, TODAY)
        if os.path.exists(local_path) is False:
            # os.chdir(UPLOAD_PATH)
            os.makedirs(local_path)

        origin_file_obj = request.FILES.get('file')

        path = request.POST.get('path', '/')
        file_type = 1
        real_path = os.path.join(UPLOAD_PATH, TODAY)
        name = origin_file_obj.name
        file_size = origin_file_obj.size
        if file_size >= 1024 * 1024 * 1024 * 100:
            return JsonResponse({
                'code': 1,
                'msg': 'file to large'
            })
        file_ext = name.split('.')[-1]
        # new file name
        real_name = time.strftime(
            '%Y%m%d%H%M%S', time.localtime()) + '.' + file_ext
        # new file path
        new_file_path = os.path.join(
            settings.BASE_DIR, UPLOAD_PATH, TODAY, real_name)

        with open(new_file_path, 'wb') as f:
            for chunk in origin_file_obj.chunks():
                f.write(chunk)
        user_obj = User.objects.get(id=request.user.id)
        res = FileInfo.objects.create(**{
            'name': name,
            'path': path,
            'owner': user_obj,
            'type': file_type,
            'file_size': format_file_size(file_size),
            'file_type': file_ext,
            'real_name': real_name,
            'real_path': real_path
        })
        if res:
            return JsonResponse({
                'code': 0,
                'msg': 'upload success',
                'data': {
                    'id': res.id,
                    'name': name,
                    'file_size': res.file_size,
                    'real_name': real_name,
                    'real_path': real_path,
                    'pub_date': res.pub_date
                }
            })
        else:
            return JsonResponse({
                'code': 1,
                'msg': 'upload fail'
            })


@login_required()
def get_user_file_list(request, t):
    if t not in ['file', 'folder']:
        return JsonResponse({
            'code': 1,
            'msg': 'type error'
        })
    else:
        file_path = request.POST.get('path', '/')
        user_id = request.user.id

        file_type = {
            'folder': 0,
            'file': 1
        }
        res = FileInfo.objects.filter(
            type=file_type[t], owner=user_id, path=file_path).values()
    if res:
        return JsonResponse({
            'code': 0,
            'message': 'ok',
            'data': list(res)
        })
    else:
        return JsonResponse({
            'code': 1,
            'message': 'fail'
        })


@login_required
def create_folder(request):
    folder_name = request.POST.get('name', '')
    p_path = request.POST.get('path', '/')

    folder = FileInfo.objects.filter(name=folder_name, path=p_path)
    if folder:
        return JsonResponse({
            'code': 1,
            'msg': '文件夹已经存在'
        })

    res = FileInfo.objects.create(**{
        'name': folder_name,
        'type': 0,
        'owner': User.objects.get(id=request.user.id),
        'path': p_path
    })
    if res:
        return JsonResponse({
            'code': 0,
            'msg': 'success',
            'data': {
                'id': res.id,
                'path': res.path,
                'name': res.name,
                'pub_date': res.pub_date
            }
        })
    else:
        return JsonResponse({
            'code': 1,
            'msg': 'fail'
        })


@login_required
def file_edit(request, fid):
    """online edit the file according fid(fileinfo table id field)

    Arguments:
        request {object} -- wsgi request object
        fid {int} -- fileinfo id field

    Returns:
        html -- online edit file of the html response view
    """
    res = FileInfo.objects.get(id=fid)
    if res and res.owner != request.user:
        return render(request, 'admin/error.html')
    file_path = '/'.join([settings.BASE_DIR, res.real_path, res.real_name])
    txt_file_type = [
        'yaml',
        'yam',
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
    file_ext = res.real_name.split('.')[-1]
    if file_ext == 'md':
        temp_name = 'file_edit_md.html'
    elif file_ext in txt_file_type:
        temp_name = 'file_edit_text.html'
    else:
        return render(request, 'admin/error.html', {
            'error_msg': '文件格式不支持在线编辑'
        })

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8', errors="ignore") as f:
            content = f.read()
        return render(request, 'admin/%s' % temp_name, {
            'filename': res.name,
            'content': content,
            'id': res.id
        })


@login_required
def file_save(request):
    """online edit file save event

    Arguments:
        request {object} -- wsgi request object

    Returns:
        str -- json object of the event description
    """
    fid = request.POST.get('id', 0)
    content = request.POST.get('content', None)
    res = FileInfo.objects.get(id=fid)

    if res and res.owner != request.user:
        return render(request, 'admin/error.html')

    file_path = '/'.join([settings.BASE_DIR, res.real_path, res.real_name])
    txt_file_type = [
        'md',
        'yaml',
        'yam',
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
    file_ext = res.real_name.split('.')[-1]
    if file_ext in txt_file_type and os.path.exists(file_path):
        with open(file_path, 'w+', encoding='utf-8', errors="ignore") as f:
            f.write(content)
        return JsonResponse({
            'code': 0,
            'msg': '写入成功'
        })
    else:
        return JsonResponse({
            'code': 1,
            'msg': '写入失败'
        })


@login_required
def file_delete(request, fid):
    """according fid delete record and file

    Arguments:
        request {object} -- wsgi request object
        fid {int} -- fileinfo talbe id field

    Returns:
        str -- event description json
    """
    res = FileInfo.objects.get(id=fid)
    # delete file
    if res and res.type == 1:
        file = res.real_path + '/' + res.real_name
        affect = res.delete()
        try:
            os.remove(file)
        except:
            return JsonResponse({
                'code': '0',
                'msg': '文件不存在'
            })
    # delete folder and file
    if res and res.type == 0:
        p_path = res.path + res.name
        sub_res = FileInfo.objects.filter(
            path__startswith=p_path, owner=request.user.id)

        for i in sub_res:
            if i.type == 1:
                os.remove(i.real_path + '/' + i.real_name)
        affect = sub_res.delete()
        res.delete()
    if affect:
        return JsonResponse({
            'code': 0,
            'msg': 'ok'
        })
    else:
        return JsonResponse({
            'code': 1,
            'msg': 'fail'
        })


# @login_required
def file_download(request, fid):
    """according fid(fileinfo talbe id field) download or view file

    Arguments:
        request {object} -- wsgi request object
        fid {int} -- fileinfo table id

    Raises:
        Http404: file does not exist

    Returns:
        html -- html response view
    """
    res = FileInfo.objects.get(id=fid)
    down = request.GET.get('d', 0)
    # if res and res.owner != request.user:
    if not res:
        return render(request, 'admin/error.html')

    if res.file_type == 'md':
        temp_name = 'file_view_md.html'
    else:
        temp_name = 'file_view_text.html'

    txt_file_type = [
        'md',
        'yaml',
        'yam',
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

    file_path = '/'.join([settings.BASE_DIR, res.real_path, res.real_name])
    if not os.path.exists(file_path):
        raise Http404()

    if res.file_type in txt_file_type and down == 0:
        with open(file_path, 'r', encoding='utf-8', errors="ignore") as f:
            content = f.read()
        return render(request, 'admin/%s' % temp_name, {
            'filename': res.name,
            'content': content
        })
    else:
        file = open(file_path, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(
            res.name.encode('utf-8').decode('ISO-8859-1'))
        return response


def format_file_size(size):
    """according file size return human format

    Arguments:
        size {int} -- file size

    Returns:
        str -- human format file size
    """
    if size < 1024:
        return '%i' % size + 'B'
    elif 1024 <= size < 1024 ** 2:
        return '%.1f' % float(size / 1024) + 'K'
    elif 1024 ** 2 <= size < 1024 ** 3:
        return '%.1f' % float(size / 1024 ** 2) + 'M'
    elif 1024 ** 3 <= size < 1024 ** 4:
        return '%.1f' % float(size / 1024 ** 3) + 'G'
