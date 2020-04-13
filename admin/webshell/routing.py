from django.urls import path
from .webssh import WebSSH
from .webtelnet import WebTelnet

websocket_urlpatterns = [
    path('webssh/', WebSSH),
    path('webtelnet/', WebTelnet)
]