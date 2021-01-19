# according python basic container image build project dependent environment

# FROM hub.c.163.com/library/python:3.6
# RUN pip --no-cache-dir  install -r requirements.txt --trusted-host mirrors.163.com -i http://mirrors.163.com/pypi/simple --proxy http://172.31.10.84:2345

# bash
# docker export -o foo.tar CONTAINER_ID
# docker import foo.bar REPOSITORY_NAME:TAG


FROM django-ops:latest

WORKDIR /django-home
COPY . /django-home
CMD ["/bin/sh", "docker-run.sh"]
