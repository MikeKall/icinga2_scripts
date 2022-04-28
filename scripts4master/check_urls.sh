#!/bin/bash

#declare -a sorted

ok=0
warning=0
critical=0
unknown=0

#input=$(echo $@| sed 's/[][]//g') 

IFS=' '     # space is set as delimiter
read -ra urls <<< "$@"
for url in "${urls[@]}"
do
	result=$(curl --head --silent $url | head -n 1|cut -d$' ' -f2)
	echo $result
	if [[ -z "$result" ]]; then
		echo  "[UNKNOWN] Could not resolve host $url"
		unknown=1	
	elif [[ $result == "302" ]] || [[ $result == "200" ]] || [[ $result == "301" ]]; then
		sorted=("${sorted[@]}" "[OK] $url")
		ok=1
	elif [[ $result == "404" ]]; then
		sorted=("[WARNING] $url NOT FOUND (Credentials required?)" "${sorted[@]}")
		warning=1
	elif [[ $result == "401" ]] || [[ $result == "403" ]]; then
		sorted=("${sorted[@]}" "[OK] $url")
		ok=1
	elif [[ $result == "500" ]]; then
		sorted=("[CRITICAL] INTERNAL SERVER ERROR for $url" "${sorted[@]}")
		critical=1 
	elif [[ $result == "503" ]]; then
		sorted=("[CRITICAL] SERVICE UNAVAILABLE for $url" "${sorted[@]}")
		critical=1
	elif [[ $result == "504" ]]; then
		sorted=("[WARNING] GATEWAY TIMEOUT for $url" "${sorted[@]}")
		warning=1
	else
		sorted=("${sorted[@]}" "[UNKNOWN] Status code $result for $url")
		unknown=1
	fi
done

for url in "${sorted[@]}"
do
	echo "$url"
	echo " "
done

if [[ $critical -eq 1 ]]; then
	exit 2
elif [[ $unknown -eq 1 ]]; then
	exit 3
elif [[ $warning -eq 1 ]]; then
	exit 1
else
	exit 0
fi
