#! coding=utf-8
#! /usr/bin/python

import telnetlib
import time
import threading
import sys
import os
import yaml


class ConfigBackup:
    '''
    auto backup huawei switch or route config file
    '''

    # telnet object
    __tn = None
    # config data
    _confData = None
    # ip address
    _ip = None

    def __init__(self, ipaddr, debug=False):
        '''
        init Telnet object by ipaddress
        @param ipaddr str ip address
        @param debug bool whether print debug info
        '''
        self._ip = ipaddr
        try:
            tn = telnetlib.Telnet(ipaddr, 23, 10)
        except Exception as e:
            raise Exception('host:'+str(ipaddr)+', errorcode: '+str(e.args[0]))
        if debug:
            tn.set_debuglevel(2)
        self.__tn = tn

    def login(self, username, password):
        '''
        login device by username and password
        @param username str login username
        @param passwore str login password
        '''
        if username:
            self.exec_cmd(username, b'Username')
        self.exec_cmd(password, b'Password')
        # self.exec_cmd('system_view', '>')

    def get_config(self):
        '''
        get switch or router current config
        '''
        tn = self.__tn

        try:
            self.exec_cmd(b'display current-configuration')
        except Exception as e:
            print self._ip

        time.sleep(.8)
        data = []
        def format_data(s):
            return s if sys.version[0] == '2' else s.decode('ascii')
        cache = format_data(tn.read_very_eager())
        while 'return' not in cache:
            tn.write(b' ')
            data.append(cache)
            time.sleep(1)
            try:
                cache = format_data(tn.read_very_eager())
            except Exception as e:
                print self._ip
            
        else:
           data.append(cache)
        tn.write(b'quit'+b'\r\n')
        configData = ''.join(data)
        self._confData = configData
        return configData

    def backup(self):
        '''
        auto backup start
        '''
        data = self.get_config()
        rs = self.write_file(data)
        if rs is False:
            return 'backup Fail'
        else:
            return 'backup success'

    def write_file(self, data):
        '''
        write config info to backup file.
        @param data str device config data
        '''
        if data is None:
            return False
        else:
            ignore_str = [
                '---- More ----',
                '\x1b[42D',
                '\x1b[16D#',
                '\x1b[16D',
                '  '
            ]
            for s in ignore_str:
                data = data.replace(s,'')

            lines =  data.replace('\r\n','\n').split('\n')
              
            for line in lines:
                if 'sysname' in line:
                    sysname = line.strip().split(' ')[1]
                    break

            filename = '{ip}-{sysname}.txt'.format(ip=self._ip, sysname=sysname)

            with open(filename, 'w') as fp:
                fp.write(
                    '\n'.join(lines[1:-1])
                )
            return True

    def exec_cmd(self, cmd, prompt=b'>'):
        '''
        execute command
        @param cmd bytes excute command
        @param prompt bytes waitfor string
        '''
        tn = self.__tn
        if tn is None:
            return
        tn.read_until(prompt, 5)
        tn.write(cmd+b'\r\n')
        time.sleep(.2)


success_list = []


def AutoBackup(ip, user, pwd, debug=False):
    '''
    background thread process
    '''
    cb = ConfigBackup(ip, debug)
    cb.login(user, pwd)
    # h3c device
    if user is None:
        cb.exec_cmd(b' ',b'ENTER')
    cb.backup()
    print('%15s backup success' % ip)
    success_list.append(ip)


if __name__ == '__main__':
    '''
    entry
    '''
    config_file = './conf.yaml'
    if os.path.exists(config_file) == False:
        exit()
    else:
        f = open(config_file, 'r')
        device_list = yaml.load(f.read())

    if '--help' in sys.argv or '-h' in sys.argv:
        print(
            '华为网络设备自动备份脚本\n \
            --debug <ip> --user <username> --pass <password> 单台设备调试模式\n \
            --help, -h                                       打印该帮助信息\n\
            '
        )
        exit()

    if '--debug' in sys.argv and '--user' in sys.argv and '--pass' in sys.argv:
        ip = sys.argv[sys.argv.index('--debug')+1]
        user = sys.argv[sys.argv.index('--user')+1]
        pwd = sys.argv[sys.argv.index('--pass')+1]
        debug = True
        AutoBackup(ip, user, pwd, debug)
        exit()

    for i in device_list['data']:
        user = i['username']
        pwd = i['password']
        for ip in i['hosts']:
            threading.Thread(target=AutoBackup, args=(ip, user, pwd,)).start()
        # th.start()
        
    xx=0
    while True:
        if threading.activeCount() > 1:
            # print('current running thread total is:'+str(threading.activeCount))
            time.sleep(.5)
            xx =+ 1
            if xx > 600:
                break
        else:
            break

    for i in device_list['data']:
        for h in i['hosts']:
            if h not in success_list:
                print('%15s backup failed' % h)
