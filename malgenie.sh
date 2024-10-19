#!/bin/bash

#Malgenie

if [ -z "$1" ]; then
	echo "No malware description provided"
	exit 1
fi

echo "Generating Malware..."

if [ -n "$2" ]; then
	python3 query_model.py "$1" "$2" > malware.c
else
	python3 query_model.py "$1" > malware.c
fi

x86_64-w64-mingw32-gcc malware.c -o malware.exe
status=$?

if [ $status -eq 0 ]; then
	echo "Malware succesfully generated"
else
	echo "compilation error, prompting model for fix..."
	output=$(x86_64-w64-mingw32-gcc malware.c 2>&1)
	echo "$output" > "error_log.txt"
        error_contents=$(cat "error_log.txt")
	code_contents=$(cat "malware.c")
	$0 "$1" "$error_contents" "$code_contents"
fi
