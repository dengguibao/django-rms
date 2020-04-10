from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import VmInfo, HostInfo, FileInfo, ClusterInfo
from django.db.models import Count
from django.contrib.auth.models import User
import datetime


@login_required()
def list_summary_view(request):
    """admin module default page,and this is search page too
    
    Arguments:
        request {object} -- wsgi http request object
    
    Returns:
        html -- html template
    """
    vms_count = VmInfo.objects.all().count()
    hosts_count = HostInfo.objects.all().count()

    res_cluster = ClusterInfo.objects.filter(is_active=0).values('name','tag')
    cluster_array = {i['tag']:i['name'] for i in res_cluster}

    cluster_count = ClusterInfo.objects.all().count()
    vms_count_data = []
    for i in cluster_array:
        d = VmInfo.objects.filter(host__cluster_tag=i).count()
        vms_count_data.append(d)

    esxi_count_data = []   
    for i in cluster_array:
        d = HostInfo.objects.filter(cluster_tag=i).count()
        esxi_count_data.append(d)

    esxi_none_count = HostInfo.objects.filter(cluster_tag='none').count()
    
    user_count = User.objects.all().count()
    file_count = FileInfo.objects.all().count()
    
    now = datetime.datetime.now()
    start = now - datetime.timedelta(hours=23, minutes=59, seconds=59)
    in_guarantee_count = HostInfo.objects.filter(end_svc_date__gte=start).count()

    return render(request, 'admin/list_summary.html', {
        'user_url_path': '管理',
        'data':{
            'vms_count':vms_count,
            'hosts_count':hosts_count,
            'vms_count_data':vms_count_data,
            'esxi_count_data':esxi_count_data,
            'cluster_count':cluster_count,
            'cluster_data':res_cluster,
            'file_count': file_count,
            'user_count': user_count,
            'esxi_none_count': esxi_none_count,
            'in_guarantee_count': in_guarantee_count,
            'out_guarantee_count': hosts_count-in_guarantee_count
        }
    })


@login_required()
def get_cluster_count_info(request, cluster_name):
    """get cluster virtual mechine count info and then render bar chart
    
    Arguments:
        request {object} -- request
        cluster_name {str} -- cluster name
    
    Returns:
        str -- return json str
    """
    res_cluster = ClusterInfo.objects.filter(is_active=0).values('name','tag')
    cluster_array = {i['tag']:i['name'] for i in res_cluster}
    if cluster_name not in cluster_array:
        return JsonResponse({
            'code':1,
            'msg': 'cluster name error'
        })
    else:
        res = HostInfo.objects.\
            filter(cluster_tag=cluster_name).\
            annotate(count=Count("vminfo__vm_hostname")).\
            values_list("hostname", "count")
        return JsonResponse({
            'code':0,
            'name': cluster_array[cluster_name],
            'msg':'success',
            'data':list(res)
        })


@login_required
def get_guarantee_info(request, cluster_name):
    """get cluster host server guarantee info and then render pie chart
    
    Arguments:
        request {object} -- request
        cluster_name {str} -- cluster name
    
    Returns:
        str -- return json str
    """
    res_cluster = ClusterInfo.objects.filter(is_active=0).values('name','tag')
    cluster_array = {i['tag']:i['name'] for i in res_cluster}
    cluster_array['none']='独立服务器'
    if cluster_name not in cluster_array:
        return JsonResponse({
            'code':1,
            'msg': 'cluster name error'
        })
    else:
        now = datetime.datetime.now()
        start = now - datetime.timedelta(hours=23, minutes=59, seconds=59)
        in_guarantee_count = HostInfo.objects.filter(end_svc_date__gte=start, cluster_tag=cluster_name).count()
        all_res = HostInfo.objects.filter(cluster_tag=cluster_name).count()
        return JsonResponse({
            'code':0,
            'name': cluster_array[cluster_name],
            'msg':'success',
            'data':[
                {
                    'name':'在保',
                    'y': in_guarantee_count
                },{
                    'name':'过保',
                    'y': all_res-in_guarantee_count
                }
            ]
        })