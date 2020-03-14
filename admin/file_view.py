from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
import os
import time

from .models import FileInfo

today = time.strftime('%Y%m%d', time.localtime())
upload_path = 'uploads'


@login_required()
def upload_file(request):
    if request.method == 'POST':
        local_path = os.path.join(settings.BASE_DIR, upload_path, today)
        print(os.path.exists(local_path))
        if os.path.exists(local_path) is False:
            # os.chdir(upload_path)
            os.makedirs(local_path)

        origin_file_obj = request.FILES.get('file')

        path = request.POST.get('path', '/')
        file_type = 1
        real_path = os.path.join(upload_path, today)
        name = origin_file_obj.name

        file_ext = name.split('.')[-1]
        # new file name
        real_name = time.strftime(
            '%Y%m%d%H%M%S', time.localtime())+'.'+file_ext
        # new file path
        new_file_path = os.path.join(
            settings.BASE_DIR, upload_path, today, real_name)

        with open(new_file_path, 'wb') as f:
            for chunk in origin_file_obj.chunks():
                f.write(chunk)
        user_obj = User.objects.get(id=request.user.id)
        res = FileInfo.objects.create(**{
            'name': name,
            'path': path,
            'owner': user_obj,
            'type': file_type,
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
def get_user_filelist(request, t):
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
    folder_name = request.POST.get('name','')
    p_path = request.POST.get('path','/')

    folder = FileInfo.objects.filter(name=folder_name, path=p_path)
    print(folder)
    if folder:
        return JsonResponse({
            'code':1,
            'msg':'文件夹已经存在'
        })


    res=FileInfo.objects.create(**{
        'name':folder_name,
        'type':0,
        'owner':User.objects.get(id=request.user.id),
        'path':p_path
    })
    if res:
        return JsonResponse({
            'code':0,
            'msg':'success',
            'data':{
                'id':res.id,
                'path':res.path,
                'name':res.name,
                'pub_date':res.pub_date
            }
        })
    else:
        return JsonResponse({
            'code':1,
            'msg':'fail'
        })


@login_required
def file_delete(request, i):
    res = FileInfo.objects.get(id=i)
    # delete file
    if res and res.type == 1:
        file = res.real_path+'/'+res.real_name
        os.remove(file)
        affect = res.delete()
    # delete folder and file
    if res and res.type == 0:
        p_path = res.path + res.name
        sub_res = FileInfo.objects.filter(path__startswith=p_path, owner=request.user.id)

        for i in sub_res:
            if i.type == 1:
                os.remove(i.real_path+'/'+i.real_name)
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
    

@login_required
def file_download(request, id):
    res=FileInfo.objects.get(id=id)
    if res and res.owner != request.user:
        return render(request, 'admin/error.html')
    else:
        try:
            file = open('/'.join([res.real_path,res.real_name]), 'rb')
            response = FileResponse(file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{}"'.format(res.name.encode('utf-8').decode('ISO-8859-1'))
            return response
        except Exception:
            raise Http404