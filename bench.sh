#!/bin/bash

SERVER_IP="127.0.0.1"
PORT="20516"
WORKSPACE=$1
MESSAGE="<165>1 2003-10-11T22:14:15.003Z mymachine.example.com evntslog - ID47 [exampleSDID@32473 iut="3" eventSource="Application" eventID="1011"] BOMAn application event log entry..."
COUNT=0

if [ $# -eq 0 ]; then
    >&2 echo "No arguments provided, you have to specify the concentrator docker compose file"
    exit 1
fi

function output {
    echo "Send events : $COUNT"
    INPUT=$(sudo docker compose -f $WORKSPACE logs | grep -o Input | wc -l)
    OUTPUT=$(sudo docker compose -f $WORKSPACE logs | grep -o Output | wc -l)
    echo "Concentrator Input : $INPUT"
    echo "Concentrator Output : $OUTPUT"
    exit 0
}

trap output SIGINT

while true; do
    echo "$MESSAGE" | nc -q 0 "$SERVER_IP" "$PORT"
    ((COUNT++))
done