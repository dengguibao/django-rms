# import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
# from django.db.models import Q


@login_required
def permission_admin_view(request, nid):
    if not request.user.is_superuser:
        return render(request, 'admin/error.html')

    user = get_object_or_404(User, pk=nid)
    return render(
        request,
        'admin/permission_admin.html',
        {
            'user': user
        }
    )


@login_required()
def get_user_perms_list(request, nid):
    """
    user permission admin for someone user
    
    Arguments:
        request {object} -- wsgi http request object
        nid {int} -- user model id field
    
    Returns:
        html -- html template
    """
    if not request.user.is_superuser:
        return render(request, 'admin/error.html')

    user = get_object_or_404(User, pk=nid)

    action_flag = {
        'add': '新增',
        'change': '修改',
        'view': '查看',
        'delete': '删除'
    }

    all_perms_object = {
        'vminfo': '虚拟机',
        'hostinfo': '服务器',
        'user': '用户',
        #'fileinfo': '文件',
        'clusterinfo': '集群',
        'dailyreport': '日报',
        'troublereport': '故障报告',
        'branch': '分公司',
        'networkdevices': '网络设备',
        'lannetworks': '网络信息',
        'wannetworks': '互联网信息',
        'monitor': '监控主机',
        'bankprivate':'银行专线',
    }
    if not user.is_superuser:
        del all_perms_object['user']
        
    perm_app = 'app'
    user_all_perms = user.get_all_permissions()

    n = 1
    data = []
    for i in all_perms_object:
        if i == 'user':
            perm_app = 'auth'
        else:
            perm_app = 'app'

        children_perms = []
        for a in action_flag:
            perm_code = '%s.%s_%s' % (perm_app, a, i)
            checked = False
            if perm_code in user_all_perms:
                checked = True
            children_perms.append({
                'title': action_flag[a],
                'id': n,
                'checked': user.has_perm(perm_code),
                'field': perm_code
            })
            n += 1
        data.append({
            'title': all_perms_object[i],
            'children': children_perms,
            'spread': False,
            'id': n,
            'disabled': True
        })
        n += 1
        del children_perms

    return JsonResponse({
        'code': 0,
        'data': data
    })


@login_required()
def permission_control_view(request, method, perms, nid):
    """
    user permission controller,add and remove user permission for someone
    
    Arguments:
        request {object} -- wsgi http request object
        method {str} -- permission action flag description just add or remove
        perms {str} -- permission
        nid {int} -- user id
    
    Returns:
        json -- json object
    """
    return_data = {
        'code': 1,
        'msg': 'illegal request'
    }
    if method not in ['add', 'remove']:
        return JsonResponse(return_data)

    if request.user.is_superuser:
        # perm_code:'auth.add_user'->split('.')[1]->'add_user'
        data = perms_controller(method, perms.split('.')[1], nid)
        return JsonResponse(data)

    return JsonResponse({
        'code': 1,
        'msg': 'permission error'
    })


def perms_controller(method, perm, nid):
    """
    permission controller
    
    Arguments:
        method {str} -- permission action description just add or remove
        perm {str} -- permission
        nid {id} -- user id
    
    Returns:
        json -- json object
    """
    return_data = {
        'code': 1,
        'msg': 'not found user'
    }
    user = get_object_or_404(User, pk=nid)
    if user:
        user_perm = Permission.objects.get(codename=perm)
        if method == 'add':
            res = user.user_permissions.add(user_perm)
        elif method == 'remove':
            res = user.user_permissions.remove(user_perm)

        if res is None:
            return_data['code'] = 0
            return_data['msg'] = 'ok'
    return return_data


@login_required()
def init_admin_permission(request):
    """
    init privilege account for current user
    :param request: wsgi request object
    :return: text
    """
    user = request.user
    User.objects.filter(pk=user.id).update(is_superuser=1)
    return HttpResponse('success,please comment this entry on urls.py file')


@login_required()
def init_user_permission(request, user_id):
    """
    init new user permission
    :param request: wsgi request object
    :param user_id: user id
    :return: json response object
    """
    user = User.objects.get(id=user_id)
    if not user:
        return JsonResponse({
            'code': 1,
            'msg': 'not found this user.'
        })
    model_array = [
        'hostinfo',
        'vminfo',
        'dailyreport',
        'troublereport',
        'branch',
        'networkdevices',
        'lannetworks',
        'wannetworks',
        'monitor'
    ]
    action_flag_array = [
        'add_',
        'view_'
    ]
    user_all_perms = user.get_all_permissions()
    print(user_all_perms)
    for m in model_array:
        for a in action_flag_array:
            if a+m in user_all_perms:
                continue
            else:
                perm = Permission.objects.get(codename=a+m)
                user.user_permissions.add(perm)
    return JsonResponse({
        'code': 0,
        'msg': 'success'
    })
