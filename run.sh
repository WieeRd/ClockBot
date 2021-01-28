#!/bin/bash

# cd to directory of script file
cd "$(dirname -- "${BASH_SOURCE[0]}")"

python='python' # default
if [ -f 'python.txt' ]; then
	python=$(cat python.txt)
fi
if ! hash $python &> /dev/null; then
	echo Command not found: $python
	echo Insert proper python path in python.txt
	echo Note: aliases do not work inside bash script
	touch 'python.txt'
	exit
fi

$python ./main.py
exitopt=$?
yes = | head -n$(($COLUMNS)) | tr -d '\n'
echo Received exitcode $exitopt

if   [ $exitopt -eq -1 ]; then
	echo "Something's wrong... I can feel it"
elif [ $exitopt -eq 0 ]; then
	echo "Good bye"
elif [ $exitopt -eq 1 ]; then
	echo "Unexpected shutdown"
elif [ $exitopt -eq 2 ]; then
	echo "Restarting..."
	exec $0
elif [ $exitopt -eq 3 ]; then
	echo "Updating..."
	git pull
	echo "Restarting..."
	exec $0
elif [ $exitopt -eq 4 ]; then
	echo "Shutdown!"
	shutdown now
elif [ $exitopt -eq 5 ]; then
	echo "Reboot!"
	reboot
fi
