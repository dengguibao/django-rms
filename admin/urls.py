from django.urls import path

from . import views
app_name = 'admin'
urlpatterns = [
    path('', views.index, name='admin_index'),
    path('render/<str:temp_name>/', views.render_temp, name='render_temp'),
    path('edit/<str:form_name>/<str:nid>/', views.render_edit, name='edit'),
    path('search/<str:dev_type>/<str:keyword>/', views.search, name='search'),
    path('delete/<str:form_name>/<str:nid>/', views.delete, name='delete'),
    path('create-or-update/<str:form_type>/', views.create_or_update, name='create-or-update'),
    path('get-hosts-list/type/<str:dev_type>/flag/<str:flag>/', views.get_hosts_list, name='get_hosts_list'),
    path('get-user-list/', views.get_user_list, name="get_user_list"),
]
