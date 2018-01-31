#!/bin/bash

# This counts to 6

i="0"
# Create a funktion for error out
echoerr() { echo "$@" 1>&2; }

while [ $i -lt 6 ]
do
	i=$[$i+1]
	echo "i is: " + $i
	echoerr "i is: " + $i + "error"
	sleep 1
done
