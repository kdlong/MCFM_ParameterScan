#!/bin/bash

for filename in $(ls jobs | grep "^$1"); do
  ./formatScaleInfo.py -f jobs/$filename -p ${1%_*} --format_as_data $2
done
