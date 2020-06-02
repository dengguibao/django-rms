import datetime, time, calendar
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from .models import (
    VmInfo, HostInfo, FileInfo, 
    ClusterInfo, Branch, NetworkDevices,
    TroubleReport, DailyReport
)


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

    res_cluster = ClusterInfo.objects.filter(is_active=0)
    # cluster_array = {i['tag']: i['name'] for i in res_cluster}

    # cluster_count = ClusterInfo.objects.all().count()
    # vms_count_data = []
    # for i in cluster_array:
    #     d = VmInfo.objects.filter(host__cluster_tag=i.tag).count()
    #     vms_count_data.append(d)

    # esxi_count_data = []
    # for i in cluster_array:
    #     d = HostInfo.objects.filter(cluster_tag=i.tag).count()
    #     esxi_count_data.append(d)

    # 分子公司总数减去总部
    branch_count = Branch.objects.filter(isenable=1).count()-1
    net_device_annotate = NetworkDevices.objects.values("device_type").annotate(count=Count("id"))
    esxi_none_count = HostInfo.objects.filter(cluster_tag='none').count()

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
    ).annotate(count=Count('dailyreport__owner_id')).values('first_name','count')

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
            'vms_count': vms_count,
            'hosts_count': hosts_count,
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
        'name': cluster_array[cluster_name],
        'msg': 'success',
        'data': list(res)
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
    cluster_array['none'] = '独立服务器'
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
        'name': cluster_array[cluster_name],
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
