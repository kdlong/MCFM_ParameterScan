#!/bin/bash
process=$1
begin=$2
end=$3
count=$4

iter=$begin
while [ $iter -lt $end ]; do
    DATE=`date +%Y-%m-%d`
    ./MCFM_scan.py -n ${process}_${DATE}_${iter}GeV -e ${iter} -r $[ 1 + $[ RANDOM % 500 ]] -p $process
    iter=$(( iter + count ))
done
