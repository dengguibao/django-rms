import paramiko
from threading import Thread
import socket
import json
import time
import random
import hashlib
import time

def get_key_obj(pkeyobj, pkey_file=None, pkey_obj=None, password=None):
    if pkey_file:
        with open(pkey_file) as fo:
            try:
                pkey = pkeyobj.from_private_key(fo, password=password)
                return pkey
            except:
                pass
    else:
        try:
            pkey = pkeyobj.from_private_key(pkey_obj, password=password)
            return pkey
        except:
            pkey_obj.seek(0)

def unique():
    ctime = str(time.time())
    salt = str(random.random())
    m = hashlib.md5(bytes(salt, encoding='utf-8'))
    m.update(bytes(ctime, encoding='utf-8'))
    return m.hexdigest()

    
class SSH:
    channel = None
    def __init__(self, websocker, message):
        self.websocker = websocker
        self.message = message

    def connect(self, host, user, password=None, port=22, term='xterm', pty_width=80, pty_height=24, timeout=10):
        try:
            trans = paramiko.Transport((host, port))
            trans.start_client()
            trans.auth_password(username=user, password=password)
            self.channel = trans.open_session()
            self.channel.get_pty(term=term, width=pty_width, height=pty_height)
            self.channel.invoke_shell()
            Thread(target=self.websocket_to_django).start()
        except Exception as e:
            # print(str(e))
            self.message['status'] = 0
            self.message['message'] = str(e)+'\r\n'
            message = json.dumps(self.message)
            self.websocker.send(message)
            self.close()
        except:
            self.close()

    def resize_pty(self, cols, rows):
        self.channel.resize_pty(width=cols, height=rows)
        pass

    def django_to_ssh(self, data):
        try:
            # print(data)
            self.channel.send(data)
        except:
            self.close()

    def websocket_to_django(self):
        try:
            while True:
                data = self.channel.recv(65535).decode('utf-8')
                if not len(data):
                    time.sleep(.1)
                    # return
                else:
                    self.message['status'] = 0
                    self.message['message'] = data
                    message = json.dumps(self.message)
                    self.websocker.send(message)
        except:
            self.close()

    def close(self):
        if self.channel:
            self.django_to_ssh('exit') # send quit command
            self.channel.close()
        self.websocker.close()

    def shell(self, data):
        Thread(target=self.django_to_ssh, args=(data,)).start()





