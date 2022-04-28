# To be run in each DC, Failure count > 0 , because when DCs are patching, it is very likely that they can hit a replicaiton fail in the meantime, nothing to worry about.
$replication = Get-ADReplicationFailure -Target $env:COMPUTERNAME
$status = $replication | where {$_.Failurecount -gt 0}

# To check for errors in repadmin, if lines > 7 means that there are errors, we show the output in icinga2
$repadmin = repadmin /showrepl "$($env:COMPUTERNAME):389" /errorsonly 
$repadmin_lines = $repadmin | Measure-Object -Line | select Lines -ExpandProperty Lines

if (!$status -and $repadmin_lines -le 7 ){
	echo "[OK] No AD Replication Failures on $env:COMPUTERNAME"
    echo "| 'Replication fail'=0"
	exit(0)
}
else {
	echo  "[CRITICAL] AD Replication Failure with:"  $($replication)
    echo $($repadmin)
    echo "| 'Replication fail'=1"
	exit(2)
}