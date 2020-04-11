from django.urls import path
from .webssh import WebSSH

websocket_urlpatterns = [
    path('webssh/', WebSSH),
]