#!/bin/sh
venv_path='/home/dgb/Documents/django_project/.venv'
project_home='/home/dgb/Documents/django_project/dms'
wsgi_module='home.wsgi'
listen="0.0.0.0:8080"
user=dgb
worker_num=4


source ${venv_path}/bin/activate
cd ${project_home}


start(){
	gunicorn ${wsgi_module}:application -w ${worker_num} -u ${user} -g ${user} -b ${listen} --pid gunicorn.pid -D
	echo "*** start service ***"
}
stop(){
	kill `cat gunicorn.pid`
	rm -rf gunicorn.pid

	sleep 2
	P_ID=`ps -ef | grep -w "${wsgi_module}" | grep -v "grep" | awk '{print $2}'`
	if [ "$P_ID" == "" ]; then
		echo
	else
		kill -9 $P_ID
	fi
	echo "*** stop service ***"
}
f_usage() {
	echo "USAGE: restart [options]"
	echo "OPTIONS:"
	echo "       start"
	echo "       stop "
	echo "       restart"
}

case "$1" in

	"start")
		start
	;;
	"stop")
		stop
	;;
	"restart")
		stop
		sleep 2
		start
		echo "*** restart service ***"
	;;
	*)
		f_usage
	;;
esac
exit 0
