#!/bin/bash
cd "$(dirname -- "${BASH_SOURCE[0]}")"

if [ -d ".venv" ]; then
    echo "Entering .venv"
    source .venv/bin/activate
else
    echo ".venv was not found"
fi

python3 main.py
exitopt=$?

yes = | head -n$(($COLUMNS)) | tr -d '\n'
echo Received exitcode $exitopt

if   [ $exitopt -eq 0 ]; then
	echo "Good bye"
elif [ $exitopt -eq 1 ]; then
	echo "Unexpected shutdown"
elif [ $exitopt -eq 2 ]; then
	echo "Restarting..."
	exec $0
elif [ $exitopt -eq 3 ]; then
	echo "Updating..."
	git fetch --all
	git reset --hard origin/master
	echo "Restarting..."
	exec $0
elif [ $exitopt -eq 4 ]; then
	echo "Shutdown!"
	/sbin/shutdown now
elif [ $exitopt -eq 5 ]; then
	echo "Reboot!"
	/sbin/reboot
else
	echo "Something's wrong... I can feel it"
fi
