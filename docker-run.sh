#!/bin/bash

/usr/local/bin/uwsgi --chdir /django-home --static-map /static=static --http 0.0.0.0:8080 --wsgi-file home/wsgi.py --master --processes 4 &
/usr/local/bin/daphne -b 0.0.0.0 -p 8081  home.asgi:application