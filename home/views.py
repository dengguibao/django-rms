from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import JsonResponse



def index_view(request):
    """default page
    
    Returns:
        html -- html template
    """
    return render(request, 'home/index.html')


def login_view(request):
    """user login view
    
    Arguments:
        request {object} -- wsgi http request object
    
    Returns:
        html -- html template
    """
    return render(request, 'home/login.html')


def user_login(request):
    """login form post event
    
    Arguments:
        request {object} -- wsgi http request object
    
    Returns:
        json -- json object
    """
    if request.method != 'POST':
        return JsonResponse(
            {
                'code': 1,
                'msg': 'illegal request'
            }
        )
    url_next = request.GET.get('next', '/admin/index')
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)

    if username or password:
        user = authenticate(username=username, password=password)

        if user and user.is_active:
            login(request, user)
            return JsonResponse({
                'code': 0,
                'msg': 'login success',
                'jump': url_next
            })
        else:
            return JsonResponse(
                {
                    'code': 1,
                    'msg': 'username or password is wrong!'
                }
            )
    else:
        return JsonResponse(
            {
                'code': 1,
                'msg': 'username or password is none'
            }
        )
