#!/bin/bash
#curl http://172.31.12.254/admin/media/27?d=1 | bash


rpm -ivh http://172.31.12.254/admin/media/26
mv /etc/zabbix/zabbix_agentd.conf{,~}
cat >> /etc/zabbix/zabbix_agentd.conf << EOF
PidFile=/var/run/zabbix/zabbix_agentd.pid
LogFile=/var/log/zabbix/zabbix_agentd.log
LogFileSize=0
Server=172.31.19.254
ServerActive=172.31.19.254
Hostname=$(hostname)
Include=/etc/zabbix/zabbix_agentd.d/*.conf
EOF
systemctl enable zabbix-agent
systemctl start zabbix-agent


