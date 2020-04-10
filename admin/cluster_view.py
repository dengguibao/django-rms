from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ClusterInfo


@login_required()
def get_cluster_list_view(request):
    """render cluster list
    
    Arguments:
        request {object} -- wsgi http request object
    
    Returns:
        html -- render html template
    """
    if request.user.has_perm('admin.view_clusterinfo'):
        res_list = ClusterInfo.objects.all()
        temp_name = 'admin/list_cluster.html'
        context = {
            'user_url_path': '集群',
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