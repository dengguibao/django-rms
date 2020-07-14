# FROM hub.c.163.com/library/python:3.6
FROM django-ops:latest

WORKDIR /django-home
COPY . /django-home
# RUN pip --no-cache-dir  install -r requirements.txt --trusted-host mirrors.163.com -i http://mirrors.163.com/pypi/simple --proxy http://172.31.10.84:2345
CMD ["/bin/sh", "docker-run.sh"]
