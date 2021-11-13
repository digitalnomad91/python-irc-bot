#1/bin/sh

pybot_pid=$(ps aux | grep "python ./pybot.py")
kill -9 $pybot_pid
sudo -u pybot ./pybot.py > /dev/null &
