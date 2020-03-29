from django.urls import path
from . import global_views, user_views, server_views, perm_views, file_view, script_views, zabbix_info_view, cluster_view


app_name = 'admin'
urlpatterns = [
    path('index', global_views.index_view, name='admin_index'),
    path('', global_views.index_view, name='admin_index'),
    path('render/<str:temp_name>/', global_views.render_static_temp_view, name='render_temp'),
    path('edit/<str:form_name>/<int:nid>/', global_views.render_edit_view, name='edit'),
    path('delete/<str:form_name>/<int:nid>/', global_views.delete, name='delete'),
    path('create-or-update/<str:form_type>/', global_views.create_or_update, name='create-or-update'),
    path('get-cluster-count-info/<str:cluster_name>', global_views.get_cluster_count_info),

    path('get-hosts-list/type/<str:dev_type>/flag/<str:flag>/', server_views.get_hosts_list, name='get_hosts_list'),
    path('search/<str:dev_type>/<str:keyword>/', server_views.search, name='search'),
    path('export-server/<str:dev_type>', server_views.export),

    path('permission-admin/<int:nid>', perm_views.permissin_admin_view, name="permission_admin"),
    path('permission-control/<str:method>/<str:permiss>/<int:nid>', perm_views.permission_control_view, name="permission_control"),

    path('get-user-list/', user_views.get_user_list_view, name="get_user_list"),
    path('user-logout', user_views.user_logout, name="user_logout"),
    path('change-password', user_views.user_change_password, name="change_password"),

    path('upload-file', file_view.upload_file, name='upload_file'),
    path('get-filelist/<str:t>', file_view.get_user_filelist),
    path('file-delete/<int:i>', file_view.file_delete),
    path('create-folder', file_view.create_folder),
    path('media/<int:id>', file_view.file_download),

    path('list-scripts/<str:path>', script_views.get_file_list),
    path('view-script/<str:path>', script_views.view_file),

    path('view-server-info/<int:id>', zabbix_info_view.zabbix_server_info_view),

    path('get-cluster-list/', cluster_view.get_cluster_list_view, name="get_cluster_list"),
    
]
