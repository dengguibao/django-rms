from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import WanNetworks


@login_required()
def list_wan_net_view(request):
    """render wannetworks list
    
    Arguments:
        request {object} -- wsgi http request object
    
    Returns:
        html -- render html template
    """
    if request.user.has_perm('app.view_wannetworks'):
        res_list = WanNetworks.objects.all()

        print(res_list)
        temp_name = 'admin/list_wan_net.html'
        context = {
            'obj': res_list
        }
    else:
        temp_name = 'admin/error.html'
        context = {}

    return render(
        request,
        temp_name,
        context=context
    )