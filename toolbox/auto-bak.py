#!/usr/bin/python
#!coding=utf-8

import telnetlib
import time
import threading
import sys
import os
import yaml
import argparse


class ConfigBackup:
    def __init__(self, ip_addr, debug=False, **kwargs):
        if 'port' in kwargs:
            port = kwargs['port']
        else:
            port = 23

        try:
            tn = telnetlib.Telnet(ip_addr, port, 10)
        except:
            sys.stdout.write('[%s], ip:%s, error:connect to host timeout!\r\n' % (
                time.strftime('%F %T', time.localtime()),
                ip_addr
            ))
            exit()
        else:
            sys.stdout.write('[%s], ip:%s, info:success connected to host\r\n' % (
                time.strftime('%F %T', time.localtime()),
                ip_addr
            ))

        if debug:
            tn.set_debuglevel(2)

        self._tn = tn
        self._ip = ip_addr

    def login(self, **kwargs):
        try:
            if 'username' in kwargs:
                self.exec_cmd(kwargs['username'], b'Username')
            # h3c device don't need username
            self.exec_cmd(kwargs['password'], b'Password')
        except:
            sys.stdout.write('[%s], ip:%s, error:connect to host timeout!\r\n' % (
                time.strftime('%F %T', time.localtime()),
                self._ip
            ))
        else:
            sys.stdout.write('[%s], ip:%s, msg:login to device\r\n' % (
                time.strftime('%F %T', time.localtime()),
                self._ip
            ))

    def get_config(self):
        try:
            self.exec_cmd(b'display current-configuration')
        except:
            sys.stdout.write('[%s], ip:%s, error:exec display current-configuration error\r\n' % (
                time.strftime('%F %T', time.localtime()),
                self._ip
            ))

        time.sleep(.8)
        data = []

        def format_data(s):
            return s if sys.version[0] == '2' else s.decode('ascii')

        cache = format_data(self._tn.read_very_eager())
        while 'return' not in cache and cache:
            try:
                self._tn.write(b' ')
                data.append(cache)
                time.sleep(1)
                cache = format_data(self._tn.read_very_eager())
            except:
                sys.stdout.write('[%s], ip:%s, error:read command execute result failed!\r\n' % (
                    time.strftime('%F %T', time.localtime()),
                    self._ip
                ))
                break
            else:
                sys.stdout.write('[%s], ip:%s, msg:read command execute result\r\n' % (
                    time.strftime('%F %T', time.localtime()),
                    self._ip
                ))

        else:
            data.append(cache)
        self._tn.write(b'quit\r\n')
        return ''.join(data)

    def write_config_to_file(self, data):
        if not data:
            return False

        ignore_str = [
            '---- More ----',
            '\x1b[42D',
            '\x1b[16D#',
            '\x1b[16D',
            '  '
        ]
        for s in ignore_str:
            data = data.replace(s, '')

        lines = data.replace('\r\n', '\n').split('\n')

        sys_name = 'null'
        for line in lines:
            if 'sysname' in line:
                sys_name = line.strip().split(' ')[1]
                break

        filename = '{ip}-{sysname}.txt'.format(ip=self._ip, sysname=sys_name)

        with open(filename, 'w') as fp:
            fp.write(
                '\n'.join(lines[1:-1])
            )
        return True

    def exec_cmd(self, cmd, prompt=b'>'):

        if self._tn is None:
            return
        self._tn.read_until(prompt, 5)
        self._tn.write(b'%s\r\n' % cmd)
        time.sleep(.2)


def AutoBackup(debug=False, **kwargs):
    '''
    background thread process
    '''
    if 'ip' not in kwargs or 'password' not in kwargs:
        return
    cb = ConfigBackup(kwargs['ip'], debug)
    cb.login(**kwargs)
    d = cb.get_config()
    if isinstance(d, str):
        cb.write_config_to_file(d)
        sys.stdout.write('[%s], ip:%s, msg:backup success\r\n' % (
                time.strftime('%F %T', time.localtime()),
                kwargs['ip']
            )
        )
        return
    sys.stdout.write('[%s], ip:%s, error:backup failed\r\n' % (
        time.strftime('%F %T', time.localtime()),
        kwargs['ip']
    ))


def read_config_from_file(file_name):
    if not os.path.exists(file_name):
        exit()

    with open(file_name, 'r') as f:
        d = f.read()

    data = None
    try:
        data = yaml.load(d)
    except:
        sys.stdout.write('error: parse yaml config failed\r\n')
    return data


if __name__ == '__main__':
    '''
    entry
    '''
    av = sys.argv[1:]

    parser = argparse.ArgumentParser(description="huawei network device auto bakcup script")
    parser.add_argument('--config', type=str, default='./conf.yaml',
                        help='host list config file, default "./conf.yaml"')
    parser.add_argument('--timeout', type=int, default=300, help='program execute timeout, default 300 second')
    # sp = parser.add_subparsers(description="sub-command help")
    # sp_debug = sp.add_parser('debug', help='print debug info')
    parser.add_argument('--ip', type=str, help='debug mode, ip address')
    parser.add_argument('--username', type=str, help='debug mode, login username')
    parser.add_argument('--password', type=str, help='debug mode, login password')

    args = parser.parse_args(av)
    TIMEOUT = args.timeout
    CONFIG_FILE = args.config
    IP = args.ip
    USERNAME = args.username
    PASSWORD = args.password

    if USERNAME and PASSWORD and IP:
        kwargs = {
            'ip': IP,
            'username': USERNAME,
            'password': PASSWORD
        }
        AutoBackup(True, **kwargs)
        exit()

    devices = read_config_from_file(CONFIG_FILE)
    if not devices:
        exit()

    for i in devices['data']:
        user = i['username']
        pwd = i['password']
        hosts = i['hosts']

        kwargs = {
            'password': pwd
        }
        if user and user not in ['null', 'none']:
            kwargs['username'] = user
        for ip in hosts:
            kwargs['ip'] = ip
            threading.Thread(target=AutoBackup, args=(False,), kwargs=kwargs).start()
        del kwargs
        del hosts

    times = 0
    while True:
        if threading.active_count() > 1:
            # sys.stdout.write(
            #    'current running thread total is: %s, running total time is %s\r\n' % (
            #        threading.active_count(),
            #        times
            #    )
            # )
            time.sleep(.5)
            times += 0.5
            if times > TIMEOUT:
                break
        else:
            break

