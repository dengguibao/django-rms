from django.urls import path
from . import (
    global_views,
    user_views,
    server_views,
    perm_views,
    file_view,
    script_views,
    zabbix_info_view,
    cluster_view,
    summary_view,
    webshell_views,
)

urlpatterns = [
    path('index', summary_view.list_summary_view, name='list_summary'),
    path('', summary_view.list_summary_view, name='list_summary'),
    path('get-cluster-count-info/<str:cluster_name>', summary_view.get_cluster_count_info),
    path('get-guarantee-info/<str:cluster_name>', summary_view.get_guarantee_info),

    path('render/<str:temp_name>/', global_views.render_static_temp_view),
    path('edit/<str:form_name>/<int:nid>/', global_views.render_edit_view),
    path('delete/<str:form_name>/<int:nid>/', global_views.delete),
    path('create-or-update/<str:form_name>/', global_views.create_or_update),
    path('view-logs/<str:content_type>/<int:object_id>',global_views.view_log_view),

    path('get-hosts-list/type/<str:dev_type>/flag/<str:flag>/', server_views.get_hosts_list),
    path('search/<str:dev_type>/<str:keyword>/', server_views.search),
    path('export-server/<str:dev_type>', server_views.export),

    path('permission-admin/<int:nid>', perm_views.permission_admin_view),
    path('permission-control/<str:method>/<str:perms>/<int:nid>', perm_views.permission_control_view),
    # init administrator permissions
    path('init-admin-perm', perm_views.init_admin_permission),
    path('init-user-perms/<int:user_id>', perm_views.init_user_permission),
    path('log-rollback/<int:log_id>',global_views.log_rollback_view),

    path('get-user-list/', user_views.get_user_list_view),
    path('user-logout/', user_views.user_logout),
    path('change-password/', user_views.user_change_password),

    path('upload-file', file_view.upload_file),
    path('get-file-list/<str:t>', file_view.get_user_file_list),
    path('file-delete/<int:i>', file_view.file_delete),
    path('create-folder', file_view.create_folder),
    path('media/<int:id>', file_view.file_download),
    path('edit/<int:id>', file_view.file_edit),
    path('save/', file_view.file_save),

    path('list-scripts/<str:path>', script_views.get_file_list),
    path('view-script/<str:path>', script_views.view_file),

    path('view-server-info/<int:id>', zabbix_info_view.zabbix_server_info_view),

    path('get-cluster-list/', cluster_view.get_cluster_list_view),
    
    path('web-shell/', webshell_views.web_ssh),
]