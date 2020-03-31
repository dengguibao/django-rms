from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect


def user_logout(request):
    """user logout and remove session
    
    Arguments:
        request {object} -- wsgi http request object
    
    Returns:
        none -- django remove all session
    """
    request.session.clear()
    logout(request)
    return HttpResponseRedirect('/login')


@login_required()
def user_change_password(request):
    """current user change login password
    
    Arguments:
        request {object} -- wsgi http request object
    
    Returns:
        json -- json object
    """
    user = request.user
    if request.method != 'POST':
        return JsonResponse({
            'code': 1,
            'msg': 'illegal request'
        })
    old_password = request.POST.get("old_password", None)
    new_password = request.POST.get('new_password', None)
    re_password = request.POST.get('re_password', None)

    if user.check_password(old_password) and\
            old_password and new_password and \
            re_password and new_password == re_password:

        user.set_password(new_password)
        user.save()
        return JsonResponse({
            'code': 0,
            'msg': 'success'
        })
    else:
        return JsonResponse({
            'code': 1,
            'msg': 'failed'
        })


@login_required()
def get_user_list_view(request):
    """render user admin view
    
    Arguments:
        request {object} -- wsgi http request object
    
    Returns:
        html -- render html template
    """
    if request.user.has_perm('auth.view_user'):
        user_list = User.objects.all()
        temp_name = 'admin/list_users.html'
        context = {
            'user_url_path': '用户',
            'obj': user_list
        }
    else:
        temp_name = 'admin/error.html'
        context = {}

    return render(
        request,
        temp_name,
        context=context
    )
