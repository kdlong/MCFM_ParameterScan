#!/bin/bash

for file_name in $(ls jobs | grep "$1"); do
  ./formatScaleInfo.py -f jobs/$file_name -p WZ --format_as_data
done
