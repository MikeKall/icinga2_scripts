#!/bin/bash
cluster=(
    "cerntsvac.cern.ch"
    "cerntscryo.cern.ch"
    "cerntscv.cern.ch"
    "cerntsel.cern.ch"
    "cerntsice.cern.ch"
    "cerntsen.cern.ch"
    "cerntsgs.cern.ch"
    "cernts-abt.cern.ch"
    "cerntsmpe.cern.ch"
    "cerntstim.cern.ch"
    "cerntsbe-lhcb.cern.ch"
    "cerntsremus.cern.ch"
    "lightts.cern.ch"
    "cerntscms.cern.ch"
    "cerntsatldcs.cern.ch"
    "cerntsna62.cern.ch"
    "cerntsna62dcs.cern.ch"
    "cerntsepc.cern.ch"
    "cerntslmf.cern.ch")


declare -i critical_count
critical=0
critical_count=0
for server in "${cluster[@]}"; do
    result=`nmap -p 3389 $server | awk '/3389\/tcp/' | awk '{print $2;}'`
    current_date=`date +"%D %T"`
    if [[ $result == *"open"* ]];then
        output=("${output[@]}" "[OK] $server - $current_date") 
    else
        output=("[CRITICAL] $server on port 3389 is not responding - $current_date" "${output[@]}")
	critical=1
	critical_count+=1
    fi
done

for res in "${output[@]}"
do
	echo "$res"
	echo " "
done

echo "| criticals=${critical_count}"

if [ $critical == 1 ];then
    exit 2
else
    exit 0
fi
