if [ "$1" = "restart" ]; then
	sudo kill `sudo cat twistd.pid`
	sudo twistd web --class=pyapns.server.APNSServer --port=8077
fi
if [ "$1" = "stop" ]; then
	sudo kill `sudo cat twistd.pid`
fi
if [ "$1" = "start" ]; then
	sudo twistd web --class=pyapns.server.APNSServer --port=8077
fi