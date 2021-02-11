@echo off
pushd %~dp0

main.py
set exitopt=%ERRORLEVEL%
echo "Received exitcode %exitopt%"

if %exitopt% EQU 0 (
	echo "Good bye"
) else if %exitopt% EQU 1 (
	echo "Unexpected shutdown"
) else if %exitopt% EQU 2 (
	echo "Restarting..."
	start main.py
) else if %exitopt% EQU 3 (
	echo "Updating..."
	git fetch --all
	git reset --hard origin/master
	echo "Restarting..."
	start main.py
) else if %exitopt% EQU 4 (
	echo "Shutdown!"
	shutdown -s -t 0
) else if %exitopt% EQU 5 (
	echo "Reboot!"
	shutdown -r -t 0
) else (
	echo "Something's wrong... I can feel it"
)

popd
@echo on
