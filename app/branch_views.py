from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Branch


@login_required()
def get_branch_list_view(request):
    """render branch list
    
    Arguments:
        request {object} -- wsgi http request object
    
    Returns:
        html -- render html template
    """
    if request.user.has_perm('app.view_branch'):
        res_list = Branch.objects.all()

        print(res_list)
        temp_name = 'admin/list_branch.html'
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