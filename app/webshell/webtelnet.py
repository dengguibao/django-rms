from channels.generic.websocket import WebsocketConsumer
from .telnet import Telnet
from django.http.request import QueryDict
import json


class WebTelnet(WebsocketConsumer):
    message = {'status': 0, 'message': None}

    def connect(self):
        self.accept()
        query_string = self.scope.get('query_string')
        telnet_args = QueryDict(query_string=query_string, encoding='utf-8')

        host = telnet_args.get('host')
        port = telnet_args.get('port')
        port = int(port)

        self.telnet = Telnet(websocker=self, message=self.message)
        self.telnet.connect(host, port)
        # self.telnet.shell('admin')

    def disconnect(self, close_code):
        try:
            self.telnet.close()
        except:
            pass

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if type(data) == dict:
            status = data['status']
            if status == 0:
                data = data['data']
                self.telnet.shell(data)
