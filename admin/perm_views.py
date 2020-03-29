from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.db.models import Q


@login_required()
def permissin_admin_view(request, nid):
    """user permissoin admin for someone user
    
    Arguments:
        request {object} -- wsgi http request object
        nid {int} -- user model id field
    
    Returns:
        html -- html template
    """
    if request.user.has_perm('auth.add_user') and request.user.has_perm('auth.change_user'):
        user = User.objects.get(id=nid)
        user_permission_list = user.get_all_permissions()
        data = []
        for i in user_permission_list:
            data.append({
                'permiss_explain': permission_explain(i.split('.')[1]),
                'codename': i.split('.')[1]
            })
        all_permiss_list = Permission.objects.filter(
            Q(codename__contains='vminfo') |
            # Q(codename__contains='fileinfo') |
            Q(codename__contains='clusterinfo') |
            Q(codename__contains='hostinfo') |
            Q(codename__contains='user') 
        ).values()
        for i in all_permiss_list:
            i['permission_explain'] = permission_explain(i['codename'])
        context = {
            'user_url_path': '用户',
            'user': user,
            'user_permiss_list': data,
            'all_permiss_list': all_permiss_list
        }
        temp_name = 'admin/permission_admin.html'
    else:
        context = {}
        temp_name = 'admin/error.html'
    return render(
        request,
        temp_name,
        context=context
    )


@login_required()
def permission_control_view(request, method, permiss, nid):
    """ user permissoin controller,add and remove user permisson for someone
    
    Arguments:
        request {object} -- wsgi http request object
        method {str} -- permission action description just add or remove
        permiss {str} -- permission
        nid {int} -- user id
    
    Returns:
        [type] -- [description]
    """
    return_data = {
        'code': 1,
        'msg': 'illegal request'
    }
    if method not in ['add', 'remove']:
        return JsonResponse(return_data)

    if request.user.has_perm('auth.add_user') and request.user.has_perm('auth.change_user'):
        data = perms_controll(method, permiss, nid)
        return JsonResponse(data)

    return JsonResponse({
        'code': 1,
        'msg': 'permission error'
    })


def perms_controll(method, perm, nid):
    """permission controller
    
    Arguments:
        method {str} -- permission action descripton just add or remove
        perm {str} -- permission
        nid {id} -- user id
    
    Returns:
        json -- json object
    """
    return_data = {
        'code': 1,
        'msg': 'not found user'
    }
    user = User.objects.get(id=nid)
    if user:
        user_permiss = Permission.objects.get(codename=perm)
        if method == 'add':
            res = user.user_permissions.add(user_permiss)
        elif method == 'remove':
            res = user.user_permissions.remove(user_permiss)

        if res is None:
            return_data['code'] = 0
            return_data['msg'] = 'ok'
    return return_data


def permission_explain(permiss):
    """permission chinese explain
    
    Arguments:
        permiss {str} -- permission description
    
    Returns:
        str -- permission chinese explain
    """
    if not permiss:
        return None

    x = permiss.split('_')
    act_data = {
        'add': '新增',
        'change': '修改',
        'view': '查看',
        'delete': '删除'
    }
    res_data = {
        'vminfo': '虚拟机',
        'hostinfo': '主机',
        'user': '用户',
        'fileinfo': '文件',
        'clusterinfo': '集群'
    }
    return act_data[x[0]]+res_data[x[1]]
