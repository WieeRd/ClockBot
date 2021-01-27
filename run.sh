#!/bin/bash

python ./main.py
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
fi
