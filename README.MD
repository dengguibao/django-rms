# 运维信息管理平台
## 功能说明  
- 创建集群分类并管理  
- 服务器信息管理  
- 虚拟机信息管理，支持使用ZABBIX API新增，删除，查询主机信息  
- 配置文件、日志、markdown、脚本集中管理  
- 浏览服务器指定目录的文件  
- 支持为系统创建不同的用户及不同的及别管理  
- 服务器资源的导出  
- 支持虚拟机web ssh和telnet方式远程登陆  
- 支持上传文件在线编辑，类似于web vim  
- 支持工作日报、故障报告管理以及导出功能  
- 服务器、虚拟机、用户、集群进行生命周期管理，以及日志回滚功能  
- 网络设备以及分子公司的管理  

## 部署  
### 安装依懒  
> pip install -r requirements.txt -i http://mirrors.163.com/pypi/simple --trusted-host mirrors.163.com  

### 安装uwsgi  
> pip install uwsgi

### 创建systemd  

修改PROJECT_DIR为项目所在目录

```bash
PROJECT_DIR=/usr/local/www/dms
cat > /etc/systemd/system/ops.service<<<EOF
[Unit]
Description=ops daemon

[Service]
Type=notify
StandardError=syslog
NotifyAccess=all
ExecStart=/usr/local/bin/uwsgi --http 127.0.0.1:8080 --chdir $PROJECT_DIR  --wsgi-file home/wsgi.py --master --processes 4
KillSignal=SIGQUIT
Restart=always

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/ops-channels.service<<<EOF
[Unit]
Description=ops daemon

[Service]
WorkingDirectory=$PROJECT_DIR
StandardError=syslog
NotifyAccess=all
ExecStart=/usr/local/bin/daphne -p 8081  home.asgi:application
KillSignal=SIGQUIT
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```
### 启动项目
> systemctl start ops ops-channels

### 设置nginx反向代理
安装nginx  
> yum install nginx  

修改/etc/nginx/nginx.conf配置文件
```conf
server {
        listen       80;
        server_name  _;
        root         /usr/share/nginx/html;

	client_max_body_size 1024m;
        # Load configuration files for the default server block.
        include /etc/nginx/default.d/*.conf;

        location ~ /(webtelnet|webssh) {
		proxy_pass http://127.0.0.1:8081;
        	proxy_redirect     off;
        	proxy_set_header   Host                 $http_host;
        	proxy_set_header   X-Real-IP            $remote_addr;
        	proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
        	proxy_set_header   X-Forwarded-Proto    $scheme;
		
	        proxy_http_version 1.1;
	    	proxy_set_header Upgrade $http_upgrade;
	    	proxy_set_header Connection "upgrade";
	}

        location / {
		proxy_pass http://127.0.0.1:8080;
        	proxy_redirect     off;
        	proxy_set_header   Host                 $http_host;
        	proxy_set_header   X-Real-IP            $remote_addr;
        	proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
        	proxy_set_header   X-Forwarded-Proto    $scheme;
        }

	location /static {
		alias /usr/local/www/dms/static;
	}


        error_page 404 /404.html;
            location = /40x.html {
        }

        error_page 500 502 503 504 /50x.html;
            location = /50x.html {
        }
    }
```





## 截图预览  

![01](https://raw.githubusercontent.com/dengguibao/django-rms/master/screenshot/01.png)

![02](https://raw.githubusercontent.com/dengguibao/django-rms/master/screenshot/02.png)

![03](https://raw.githubusercontent.com/dengguibao/django-rms/master/screenshot/03.png)

![04](https://raw.githubusercontent.com/dengguibao/django-rms/master/screenshot/04.png)

![05](https://raw.githubusercontent.com/dengguibao/django-rms/master/screenshot/05.png)

![06](https://raw.githubusercontent.com/dengguibao/django-rms/master/screenshot/06.png)