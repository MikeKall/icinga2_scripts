param ([double]$threshold = 5)


$LastBootDate = (Get-CimInstance -ClassName win32_operatingsystem | Select-Object -ExpandProperty lastbootuptime)
$CurrentDate = (Get-Date)
$RebootReason = (Get-CimInstance -ClassName win32_operatingsystem | Select-Object Reason)

if (($CurrentDate - $LastBootDate).TotalMinutes -lt $threshold) {
	echo "[WARNING] The server has been rebooted on $LastBootDate | 'Last boot'=1;1;-1;0;1"
	$RebootReason
	$exitCode = 1 
}
else {
	echo "[OK] The server has not been rebooted in the last $threshold minutes | 'Last boot'=0;1;-1;0;1"
	$exitCode = 0 
}

exit($exitCode)