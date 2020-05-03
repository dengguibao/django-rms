FROM hub.c.163.com/library/python:3.6

WORKDIR /django-home
COPY . /django-home
RUN pip --no-cache-dir  install -r requirements.txt --trusted-host mirrors.163.com -i http://mirrors.163.com/pypi/simple
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
