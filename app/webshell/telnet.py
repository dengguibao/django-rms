import telnetlib
import sys
import json
from threading import Thread
import time

class Telnet:

    def __init__(self, websocker, message):
        self.websocker = websocker
        self.message = message

    def connect(self, host, port=23):
        try:
            tn = telnetlib.Telnet(host, port)
            self.channel = tn
            Thread(target=self.django_to_websocket).start()
        except Exception as e:
            self.message['status'] = 0
            self.message['message'] = str(e)+'\r\n'
            message = json.dumps(self.message)
            self.websocker.send(message)
            self.close()
    
    def close(self):
        if self.channel:
            self.channel.close()
        self.websocker.close()

    def django_to_telnet(self, data):
        try:
            self.channel.write(data.encode('ascii'))
        except:
            self.close()

    def format_data(self, s):
            return s if sys.version[0] == '2' else s.decode('ascii')

    def django_to_websocket(self):
        try:
            while True:
                data = self.channel.read_very_eager()
                # print(data)
                if not len(data) and data == b'':
                    pass
                    # time.sleep(0.1)
                    # return
                else:
                    self.message['status'] = 0
                    self.message['message'] = self.format_data(data)
                    message = json.dumps(self.message)
                    self.websocker.send(message)
        except:
            self.close()

    def shell(self, data):
        Thread(target=self.django_to_telnet, args=(data,)).start()
