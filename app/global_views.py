import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.admin.options import get_content_type_for_model
from django.conf import settings
from .common import *


@login_required()
def render_static_temp_view(request, temp_name):
    """according parameter render static html template

    Arguments:
        request {object} -- wsgi http request object
        temp_name {str} -- template name

    Returns:
        html -- html template
    """
    view_subject = request.GET.get('view', 0)
    res_cluster = ClusterInfo.objects.filter(is_active=0)
    is_virt = request.GET.get('is_virt', 0)
    context = {
        'cluster_data': res_cluster.filter(is_virt=is_virt),
        'branch_data': Branch.objects.filter(isenable=1),
        'args': request.GET.get('args', None),
        'view': view_subject
    }
    return render(request, 'admin/%s.html' % temp_name, context)


@login_required()
def render_edit_view(request, form_name, nid):
    """according resource primary key,render edit view
    
    Arguments:
        request {object} -- wsgi http request object
        form_name {str} -- resources type name
        nid {int} -- resources id
    
    Returns:
        html -- html template
    """
        
    if form_name not in register_form:
        return render(request, 'admin/error.html', {'error_msg': 'illegal request!'})
    perm_action_flag = 'change'
    view_subject = request.GET.get('view', 0)
    if view_subject == "1":
        perm_action_flag = 'view'

    perm = register_form[form_name]['perm'] % perm_action_flag
    model = register_form[form_name]['model']
    # permission verify
    if not request.user.has_perm(perm):
        return render(request, 'admin/error.html')

    temp_name = 'admin/add_or_edit_%s.html' % form_name

    edit_obj = get_object_or_404(model, id=nid)

    # get all foreigenkey data
    cluster_data = ClusterInfo.objects.filter(is_active=0)
    branch_data = Branch.objects.filter(isenable=1)
    esxi_data = None
    if form_name == 'vm':
        esxi_data = HostInfo.objects.filter(cluster_tag=edit_obj.host.cluster_tag)

    context = {
        'obj': edit_obj,
        'view': view_subject
    }

    extra_context = {
        'vm': {
            'esxi_list': esxi_data,
            'zabbix_api': settings.ZABBIX_API,
            'cluster_data': cluster_data
        },
        'host': {
            'cluster_data': cluster_data,
            'branch_data': branch_data
        },
        'lan_net': {
            'branch_data': branch_data
        },
        'wan_net': {
            'branch_data': branch_data
        },
        'net_devices': {
            'branch_data': branch_data
        },
        'monitor': {
            'branch_data': branch_data
        }
    }
    # append default object
    if form_name in extra_context:
        context.update(extra_context[form_name])

    return render(
        request,
        temp_name,
        context
    )


@login_required()
def delete(request, form_name, nid):
    """delete some resources by form name and primary key

    Arguments:
        request {object} -- wsgi http request object
        form_name {str} -- resource form name
        nid {int} -- resource model primary key

    Returns:
        json -- json object
    """
    return_data = {
        'code': 1,
        'msg': 'illegal request'
    }
    if not request.is_ajax():
        return JsonResponse(return_data)

    if form_name not in register_form:
        return JsonResponse(return_data)

    perm_action_flag = 'delete'
    perm = register_form[form_name]['perm'] % perm_action_flag
    model = register_form[form_name]['model']
    # permission verify
    if not request.user.has_perm(perm):
        return JsonResponse({
            'msg': 'permission denied',
            'code': 1
        })
    # delete record
    res = model.objects.get(id=nid).delete()

    if res:
        return_data['msg'] = 'ok'
        return_data['code'] = 0

    return JsonResponse(return_data)


@login_required()
def create_or_update(request, form_name):
    """user post form event

    Arguments:
        request {object} -- wsgi http request object
        form_name {str} -- form name

    Returns:
        json -- json object
    """
    return_data = {
        'code': 1,
        'msg': 'fail'
    }
    if not request.is_ajax() and form_name not in register_form:
        return JsonResponse({
            'code': 1,
            'msg': 'illegal request!'
        })
    
    # permission verify
    perm_action_flag = 'add'
    perm = register_form[form_name]['perm'] % perm_action_flag
    model = register_form[form_name]['model']

    if not request.user.has_perm(perm):
        return JsonResponse({
            'code': 1,
            'msg': 'permission denied'
        })

    if request.user.is_superuser and form_name != 'user':
        return JsonResponse({
            'code': 1,
            'msg': '管理员不允许创建业务数据'
        })

    origin_post_data = request.POST.dict()

    log = request.GET.get('log', True)
    nid = int(request.POST.get('id', 0))
    # according id defined action
    act = 'create' if nid == 0 else 'update'

    # get all fields and fields attr by model _meta
    model_fields = {}
    for f in model._meta.get_fields():

        if f.is_relation:
            field_name = '%s_id' % f.name.split('.')[-1]
        else:
            field_name = f.name.split('.')[-1]
        field_type = f.get_internal_type()
        try:
            field_verbose_name = f.verbose_name
            choice = f.choices
        except:
            field_verbose_name = field_name
            choice = None

        model_fields[field_name] = {}
        model_fields[field_name]['verbose_name'] = field_verbose_name
        model_fields[field_name]['field_type'] = field_type
        model_fields[field_name]['choice'] = choice

    # according chang_field build change log
    change_fields = request.GET.get('change_field', None)
    if change_fields:
        change_fields = change_fields.split(',')

    log_msg = []
    post_data = {}
    for item in origin_post_data.keys():
        v = origin_post_data[item]

        if item not in ['id', 'ID'] and item in model_fields:
            post_data[item] = v

        if change_fields and item in change_fields:

            if model_fields[item]['field_type'] == 'ForeignKey':
                rel_model = model._meta.get_field(item).related_model
                try:
                    rel_obj = list(rel_model.objects.filter(id=v))[0]
                except ValueError as e:
                    # 为了适应hostinfo表前期设计时的不足，暂时硬编码
                    rel_obj = list(rel_model.objects.filter(tag=v))[0]
                except:
                    rel_obj = None

                if rel_obj:
                    if hasattr(rel_obj, 'hostname'):
                        v = rel_obj.hostname
                    if hasattr(rel_obj, 'name'):
                        v = rel_obj.name

            if model_fields[item]['choice']:
                for s, l in model_fields[item]['choice']:
                    if str(s) == v:
                        v = l
                        break

            log_msg.append('%s: %s' % (
                model_fields[item]['verbose_name'],
                v
            ))

    # write post data to database
    res = None
    try:
        if act == 'create':
            res = model.objects.create(**post_data)

        if act == 'update':
            model.objects.filter(id=nid).update(**post_data)
            res = model.objects.get(id=nid)
            if form_name == 'user':
                update_session_auth_hash(request, request.user)

    except Exception as e:
        return_data['msg'] = '%s' % e
        return_data['code'] = 1

    # write log
    if log != 'no' and res and log_msg:
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(model).pk,
            object_id=res.id,
            object_repr=str(res) if act == 'create' else ' '.join(log_msg),
            action_flag=ADDITION if act == 'create' else CHANGE,
            change_message=json.dumps(post_data, ensure_ascii=True)
        )
    # according return object judge create or update
    if act in ['update', 'create'] and res:
        return_data['code'] = 0
        return_data['msg'] = '%s success' % act

    return JsonResponse(return_data)


@login_required()
def view_log_view(request, model_name, object_id):
    """view log view

    Arguments:
        request {object} -- wsgi request object
        content_type {str} -- content type
        object_id {int} -- admin_log id

    Returns:
        retun  -- html view
    """

    if model_name not in register_form:
        return render(request, 'admin/error.html', {'error_msg': 'illegal request!'})
    model = register_form[model_name]['model']

    res = get_object_or_404(model, pk=object_id)
    
    log_entries = LogEntry.objects.filter(
        content_type_id=get_content_type_for_model(model).pk,
        object_id=res.id
    )
    return render(request, 'admin/view_log.html', {
        'log_data': log_entries
    })


@login_required()
def log_rollback_view(request, log_id):
    """rollback log, according the content of chang_message(**post_data) field in the admin_log table

    Arguments:
        request {object} -- wsgi request object
        log_id {int} -- admin_log id

    Returns:
        str -- rollback state json
    """
    log_res = LogEntry.objects.get(id=log_id)
    if not log_res:
        return JsonResponse({
            'code': 1,
            'msg': 'not found this log resource!'
        })
    # user_id = request.user.id
    # if user_id != log_res.user_id:
    #     return JsonResponse({
    #         'code': 1,
    #         'msg': 'permission denied'
    #     })

    if not log_res.change_message:
        return JsonResponse({
            'code': 1,
            'msg': 'not found rollback data'
        })

    post_data = json.loads(log_res.change_message)
    model_name = log_res.content_type.model
    model = ContentType.objects.get(app_label="app", model=model_name).model_class()
    origin_res = model.objects.get(id=log_res.object_id)
    if not origin_res:
        res = model.objects.create(**post_data)
    else:
        model.objects.filter(id=log_res.object_id).update(**post_data)
        res = model.objects.get(id=log_res.object_id)

    if res:
        return JsonResponse({
            'code': 0,
            'msg': 'rollback success'
        })
    # else action
    return JsonResponse({
        'code': 0,
        'msg': 'rollback failed'
    })


@login_required()
def navigation(request):
    return render(request, 'admin/navigation.html')
