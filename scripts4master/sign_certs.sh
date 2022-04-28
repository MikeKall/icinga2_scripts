certs=$(icinga2 ca list | cut -c -65 | sed '1d'| sed '1d')

IFS=" " 
for cert in ${certs[@]}; do
	cert=${cert//$'\n'/}
	icinga2 ca sign $cert
	#echo $cert
done
