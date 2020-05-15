from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.db.models import Q


@login_required()
def permission_admin_view(request, nid):
    """
    user permission admin for someone user
    
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
                'perms_explain': permission_explain(i.split('.')[1]),
                'codename': i.split('.')[1]
            })
        all_perms_list = Permission.objects.filter(
            Q(codename__contains='vminfo') |
            # Q(codename__contains='fileinfo') |
            Q(codename__contains='clusterinfo') |
            Q(codename__contains='hostinfo') |
            Q(codename__contains='user') |
            Q(codename__contains='dailyreport') |
            Q(codename__contains='troublereport') |
            Q(codename__contains='branch') |
            Q(codename__contains='wannetworks') |
            Q(codename__contains='lannetworks') |
            Q(codename__contains='networkdevices')

        ).values()
        for i in all_perms_list:
            i['permission_explain'] = permission_explain(i['codename'])
        context = {
            'user_url_path': '用户',
            'user': user,
            'user_perms_list': data,
            'all_perm_list': all_perms_list
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

    if request.user.has_perm('auth.add_user') and request.user.has_perm('auth.change_user'):
        data = perms_controller(method, perms, nid)
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
    user = User.objects.get(id=nid)
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


def permission_explain(perm):
    """
    permission chinese explain
    :param perm: permission description
    :return: permission chinese explain
    """
    if not perm:
        return None

    x = perm.split('_')
    act_data = {
        'add': '新增',
        'change': '修改',
        'view': '查看',
        'delete': '删除'
    }
    res_data = {
        'vminfo': '虚拟机',
        'hostinfo': '服务器',
        'user': '用户',
        'fileinfo': '文件',
        'clusterinfo': '集群',
        'dailyreport': '日报',
        'troublereport': '故障报告',
        'branch': '分公司',
        'networkdevices': '网络设备',
        'lannetworks': '网络信息',
        'wannetworks': '互联网信息',
    }
    return act_data[x[0]]+res_data[x[1]]


@login_required()
def init_admin_permission(request):
    """
    init privilege account for current user
    :param request: wsgi request object
    :return: text
    """
    user = request.user
    model_array = [
        'clusterinfo',
        # 'fileinfo',
        'hostinfo',
        'vminfo',
        'user',
        'dailyreport',
        'troublereport',
        'branch',
        'networkdevices',
        'lannetworks',
        'wannetworks',
    ]
    action_flag_array = [
        'add_',
        'change_',
        'delete_',
        'view_'
    ]
    for m in model_array:
        for a in action_flag_array:
            if user.has_perm(a+m):
                continue
            else:
                perm = Permission.objects.get(codename=a+m)
                user.user_permissions.add(perm)
    
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
    user_perms_list = [
        'add_vminfo',
        'change_vminfo',
        'view_vminfo',
        'add_hostinfo',
        'change_hostinfo',
        'view_hostinfo',
        'view_dailyreport',
        'add_dailyreport',
        'view_troublereport',
        'add_troublereport'
    ]
    for perm in user_perms_list:
        if user.has_perm(perm):
            continue
        else:
            p = Permission.objects.get(codename=perm)
            user.user_permissions.add(p)
    return JsonResponse({
        'code': 0,
        'msg': 'success'
    })
