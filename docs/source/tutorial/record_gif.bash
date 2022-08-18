#!/usr/bin/env bash

if [ $# -lt 2 ]; then
	echo "Usage: record_gif.sh time filename"
	exit 1
fi

sleeptime=$1
filename=$2

echo "Using time=$sleeptime and filename=$filename"
echo
echo -e "Instructions:
1. Click on lintrans (we assume you've set up SimpleScreenRecorder to record it already)
2. Hover mouse over SimpleScreenRecorder button (we assume you're saving to ~/Videos/lintrans.mkv)
3. Wait until recording has finished
4. Save video. It will then be converted to ./filename.gif after 5 seconds"

windowid=$(xdotool selectwindow)
sleep 3
rm -f ~/Videos/lintrans.mkv

xdotool windowactivate $windowid
xdotool key ctrl+r
sleep 0.5

xdotool click 1

sleep 0.5
xdotool windowactivate $windowid
xdotool key Control_L+Shift_L+Return
sleep $sleeptime

xdotool click 1

sleep 5

rm -f $filename.gif
mv ~/Videos/lintrans.mkv ./tmp.mkv
ffmpeg -i tmp.mkv $filename.gif
rm tmp.mkv
