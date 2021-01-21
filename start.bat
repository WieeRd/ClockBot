@echo off
cat "src/main.py" "src/*_*.py" "src/run.py" > clockbot.py
python clockbot.py
echo Exit code was %ERRORLEVEL%
pause>nul
@echo on
