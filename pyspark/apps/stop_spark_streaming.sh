#! /bin/bash

top -b -n 1 | grep python3 | awk '{print $1}' | xargs kill -9 