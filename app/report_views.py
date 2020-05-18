import xlwt
import time
import datetime
from io import BytesIO
from .models import TroubleReport, DailyReport
from .global_views import data_struct
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http.response import HttpResponse


@login_required
def report_manage(request):
    """daily report manage

    Arguments:
        request {object} -- wsgi request object

    Returns:
        html -- html response
    """
    t = request.GET.get('t', None)
    if t not in ['trouble', 'daily']:
        return render(request, 'admin/error.html')
    export = request.GET.get('export', None)
    model = {
        'trouble': TroubleReport,
        'daily': DailyReport,
    }
    user_id = request.POST.get('user_id', None)

    if user_id is None and \
            request.user.has_perm('auth.add_user') and \
            request.user.has_perm('auth.view_user'):
        user_id = 0

    if user_id is None and \
            not request.user.has_perm('auth.add_user') and \
            not request.user.has_perm('auth.view_user'):
        user_id = request.user.id
    user_id = int(user_id)

    if user_id == 0 and \
            not request.user.has_perm('auth.add_user') and \
            not request.user.has_perm('auth.view_user'):
        return render(request, '/admin/error.html')
    first_name = None
    if user_id > 0:
        user_info = User.objects.get(id=user_id)
        first_name = user_info.first_name

    work_type = request.POST.get('type', None)
    if work_type == '':
        work_type = None
    start_date = request.POST.get(
        'start_date', (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
    )
    end_date = request.POST.get(
        'end_date', time.strftime('%Y-%m-30', time.localtime())
    )
    fmt = '%Y-%m-%d'
    start_date_tuple = time.strptime(start_date, fmt)
    end_date_tuple = time.strptime(end_date, fmt)
    s_date = datetime.date(
        start_date_tuple[0], start_date_tuple[1], start_date_tuple[2]
    )
    e_date = datetime.date(
        end_date_tuple[0], end_date_tuple[1], end_date_tuple[2]
    )

    res = model[t].objects.filter(
        pub_date__range=(s_date, e_date)
    )

    if user_id != 0:
        res = res.filter(owner=user_id)
    
    if work_type:
        res = res.filter(type=work_type)

    # if user_id == 0 and work_type is None:
    #     res = model[t].objects.filter(
    #         pub_date__range=(s_date, e_date)
    #     )
    # elif user_id == 0 and work_type is not None:
    #     res = model[t].objects.filter(
    #         pub_date__range=(s_date, e_date),
    #         type=work_type
    #     )
    # elif user_id != 0 and work_type is None:
    #     res = model[t].objects.filter(
    #         pub_date__range=(s_date, e_date),
    #         owner=user_id
    #     )
    # elif user_id != 0 and work_type is not None:
    #     res = model[t].objects.filter(
    #         type=work_type,
    #         pub_date__range=(s_date, e_date),
    #         owner=user_id
    #     )
    # print(user_id, work_type)
    if export:
        wb = xlwt.Workbook(encoding='utf8')
        sheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)
        column = 0
        backup_data_struct = data_struct()
        for title in backup_data_struct[t]:
            sheet.write(0, column, backup_data_struct[t][title])
            column += 1

        column = 0
        data_row_num = 1
        for res_row in res.values():
            for key in backup_data_struct[t]:
                if key == 'owner':
                    sheet.write(data_row_num, column, res[data_row_num-1].owner.first_name)
                else:
                    sheet.write(data_row_num, column, res_row[key])
                column += 1
            column = 0
            data_row_num += 1
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=%sReport.xls' % t
        output = BytesIO()
        wb.save(output)

        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    user_data = User.objects.all()
    return render(request, 'admin/list_%s_report.html' % t, {
        'users': user_data,
        'data': res.order_by('-id'),
        'start_date': start_date,
        'end_date': end_date,
        'work_type': work_type,
        'first_name': first_name
    })


@login_required
def view_trouble_report(request, t_id):
    """view trouble report

    Arguments:
        request {object} -- wsgi request object
        t_id {int} -- trouble report table id

    Returns:
        html -- response html
    """
    res = TroubleReport.objects.get(id=t_id)
    duration = res.end_date - res.start_date
    duration_minute = duration.days*24+duration.seconds/60
    # print(duration.days*24+duration.seconds/60)
    if not res:
        return render(request, 'admin/error.html', {'error_msg': 'not found resource!'})
    # administrator not verify own
    if request.user.has_perm('auth.add_user') and request.user.has_perm('auth.view_user'):
        return render(request, 'admin/view_trouble_report.html', {'data': res, 'duration': int(duration_minute)})
    # verify object own
    if res.owner_id != request.user.id:
        return render(request, 'admin/error.html')
    else:
        return render(request, 'admin/view_trouble_report.html', {'data': res, 'duration': int(duration_minute)})
