import xlwt

from .models import *
from django.contrib.auth.models import User


register_form = {
    'host': {
        'model': HostInfo,
        'perm': 'app.%s_hostinfo',
    },
    'hostif': {
        'model': HostInterface,
        'perm': 'app.%s_hostinfo',
    },
    'vm': {
        'model': VmInfo,
        'perm': 'app.%s_vminfo',
    },
    'cluster': {
        'model': ClusterInfo,
        'perm': 'app.%s_clusterinfo',
    },
    'user': {
        'model': User,
        'perm': 'auth.%s_user',
    },
    'trouble_report': {
        'model': TroubleReport,
        'perm': 'app.%s_troublereport',
    },
    'daily_report': {
        'model': DailyReport,
        'perm': 'app.%s_dailyreport',
    },
    'branch': {
        'model': Branch,
        'perm': 'app.%s_branch',
    },
    'lan_net': {
        'model': LanNetworks,
        'perm': 'app.%s_lannetworks',
    },
    'wan_net': {
        'model': WanNetworks,
        'perm': 'app.%s_wannetworks',
    },
    'net_devices': {
        'model': NetworkDevices,
        'perm': 'app.%s_networkdevices',
    },
    'monitor': {
        'model': Monitor,
        'perm': 'app.%s_monitor',
    },
    'monitor_account': {
        'model': MonitorAccount,
        'perm': 'app.%s_monitor',
    },
    'bank_private': {
        'model': BankPrivate,
        'perm': 'app.%s_bankprivate',
    },
}


def get_model_fields(form_name):
    if form_name not in register_form:
        return

    model = register_form[form_name]['model']

    data = {
    }
    for i in model._meta.get_fields():
        if i.is_relation:
            field_name = '%s_id' % i.name
        else:
            field_name = i.name

        field_type = i.get_internal_type()

        try:
            verbose_name = i.verbose_name
            choice = i.choices
        except:
            verbose_name = field_name
            choice = None

        data[field_name] = {}
        data[field_name]['verbose_name'] = verbose_name
        data[field_name]['field_type'] = field_type
        data[field_name]['choice'] = choice
        data[field_name]['relate_name'] = i.name

    return data


def export_to_file(form_name, resource):
    wb = xlwt.Workbook(encoding='utf8')
    sheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)
    column = 0
    struct = get_model_fields(form_name)
    for title in struct:
        if hasattr(resource[0],title):
            sheet.write(0, column, struct[title]['verbose_name'])
            column += 1

    column = 0
    data_row_num = 1
    for res_row in resource:
        for key in struct:
            field_value = 'NULL'
            try:
                if struct[key]['field_type'] == 'ForeignKey':
                    foreign_model = eval('res_row.%s' % struct[key]['relate_name'])
                    if hasattr(foreign_model, 'username'):
                        field_value = foreign_model.first_name
                    if hasattr(foreign_model, 'name'):
                        field_value = foreign_model.name
                    if hasattr(foreign_model, 'hostname'):
                        field_value = foreign_model.hostname
                    # field_value = foreign_model.first_name
                elif struct[key]['choice'] is not None:
                    field_value = eval('res_row.get_%s_display()' % key)
                else:
                    field_value = eval('res_row.%s' % key)
                sheet.write(data_row_num, column, field_value)
                column += 1
            except:
                continue
        column = 0
        data_row_num += 1
    return wb
