import datetime
import time
import calendar
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from .common import *


@login_required()
def list_summary_view(request):
    """
    admin module default page,and this is search page too

    Arguments:
        request {object} -- wsgi http request object

    Returns:
        html -- html template
    """
    vms_count = VmInfo.objects.all().count()
    hosts_count = HostInfo.objects.all().count()

    res_cluster = ClusterInfo.objects.filter(is_active=0, is_virt=1)
    # 分子公司总数减去总部
    branch_count = Branch.objects.filter(isenable=1).count()-1
    monitor_count = Monitor.objects.all().count()
    camera_count = Monitor.objects.aggregate(Sum('camera_nums'))
    net_device_annotate = NetworkDevices.objects.values("device_type").annotate(count=Count("id"))
    esxi_none_count = HostInfo.objects.filter(cluster_tag__is_virt=0).count()
    esxi_count = hosts_count-esxi_none_count

    start_date = time.strftime('%Y-%m-01', time.localtime())
    end_date = time.strftime('%Y-%m-', time.localtime())
    x=end_date.split('-')
    end_date = end_date + '%s' % calendar.monthrange(
        int(x[0]),int(x[1])
    )[1]

    fmt = '%Y-%m-%d'

    start_date_tuple = time.strptime(start_date, fmt)
    end_date_tuple = time.strptime(end_date, fmt)

    s_date = datetime.date(
        start_date_tuple[0], start_date_tuple[1], start_date_tuple[2]
    )
    e_date = datetime.date(
        end_date_tuple[0], end_date_tuple[1], end_date_tuple[2]
    )

    trouble_annotate_count = TroubleReport.objects.filter(
        pub_date__range=(s_date, e_date)
    ).values('type').annotate(count=Count('id'))

    user_work_annotate_count = User.objects.filter(
        dailyreport__pub_date__range=(s_date, e_date)
    ).annotate(count=Count('dailyreport__owner_id')).values('first_name', 'count')

    # camera_sumary=Branch.objects.annotate(sum=Sum('monitor__camera_nums')).values('name','sum')

    # print(user_work_annotate_count.query)

    # print(user_work_annotate_count.query)

    user_count = User.objects.all().count()
    file_count = FileInfo.objects.all().count()

    now = datetime.datetime.now()
    start = now - datetime.timedelta(hours=23, minutes=59, seconds=59)
    in_guarantee_count = HostInfo.objects.filter(
        end_svc_date__gte=start
    ).count()

    return render(
        request, 
        'admin/list_summary.html', 
        {
        'data': {
            'trouble_count_data': trouble_annotate_count,
            'user_work_count_data': user_work_annotate_count,
            'branch_count': branch_count,
            'monitor_count': monitor_count,
            'camera_count': camera_count['camera_nums__sum'],
            'vms_count': vms_count,
            'hosts_count': hosts_count,
            'esxi_count': esxi_count,
            'net_device_data': net_device_annotate,
            'cluster_data': res_cluster,
            'file_count': file_count,
            'user_count': user_count,
            'esxi_none_count': esxi_none_count,
            'in_guarantee_count': in_guarantee_count,
            'out_guarantee_count': hosts_count - in_guarantee_count
        }
    })


@login_required()
def get_cluster_count_info(request, cluster_name):
    """
    get cluster virtual machine count info and then render bar chart

    Arguments:
        request {object} -- request
        cluster_name {str} -- cluster name

    Returns:
        str -- return json str
    """
    res_cluster = ClusterInfo.objects.filter(is_active=0).values('name', 'tag')
    cluster_array = {i['tag']: i['name'] for i in res_cluster}
    if cluster_name not in cluster_array:
        return JsonResponse({
            'code': 1,
            'msg': 'cluster name error'
        })

    res = HostInfo.objects. \
        filter(cluster_tag=cluster_name). \
        annotate(count=Count("vminfo__vm_hostname")). \
        values_list("hostname", "count")
    return JsonResponse({
        'code': 0,
        'name': '%s - 虚拟机分布' % cluster_array[cluster_name],
        'msg': 'success',
        'data': list(res)
    })


@login_required
def get_camera_info(request, dev_type):
    res=name=None
    if dev_type == 'camera':
        name = "视频监控 - 摄像头"
        res = Branch.objects.annotate(y=Sum('monitor__camera_nums'))
    elif dev_type == 'recorder':
        name = "视频监控 - 监控主机"
        res = Branch.objects.annotate(y=Count('monitor__camera_nums'))

    if not res:
        return JsonResponse({
            'code': 1,
            'msg': 'failed'
        })

    return JsonResponse({
        'code': 0,
        'msg': 'success',
        'name': name,
        'data': list(res.values('name', 'y'))  # pie
        #'data': list(res.values_list('name', 'y'))
    })


@login_required
def get_guarantee_info(request, cluster_name):
    """
    get cluster host server guarantee info and then render pie chart

    Arguments:
        request {object} -- request
        cluster_name {str} -- cluster name

    Returns:
        str -- return json str
    """
    res_cluster = ClusterInfo.objects.filter(is_active=0).values('name', 'tag')
    cluster_array = {i['tag']: i['name'] for i in res_cluster}
    if cluster_name not in cluster_array:
        return JsonResponse({
            'code': 1,
            'msg': 'cluster name error'
        })

    now = datetime.datetime.now()
    start = now - datetime.timedelta(hours=23, minutes=59, seconds=59)
    in_guarantee_count = HostInfo.objects.filter(
        end_svc_date__gte=start,
        cluster_tag=cluster_name
    ).count()
    all_res = HostInfo.objects.filter(cluster_tag=cluster_name).count()
    return JsonResponse({
        'code': 0,
        'name': '%s' % cluster_array[cluster_name],
        'msg': 'success',
        'data': [
            {
                'name': '在保',
                'y': in_guarantee_count
            }, {
                'name': '过保',
                'y': all_res - in_guarantee_count
            }
        ]
    })
