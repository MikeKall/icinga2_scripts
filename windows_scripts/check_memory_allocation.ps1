param(
	[string]$process,
	[int]$warning = 65,
	[int]$critical = 72
	)

$proc_mem =  ((get-wmiobject -cl Win32_PerfFormattedData_PerfProc_Process | Where-Object {$_.Name -like '*sqlservr*'}).WorkingSetPrivate)/1MB

$RAM = [math]::round((Get-WMIObject Win32_PhysicalMemory | Measure -Property capacity -Sum | %{$_.sum/1MB}),1)

$Percentage = [math]::round(($proc_mem*100/$RAM),1)

if ($Percentage -gt $critical){
	echo "[CRITICAL] Process $process allocates $Percentage% of memory"
	$exitCode = 2
}
elseif ($Percentage -gt $warning){
	echo "[WARNING] Process $process allocates $Percentage% of memory"
	$exitCode = 1
}
else {
	echo "[OK] Process $process allocates $Percentage% of memory"
	$exitCode = 0
}
exit($exitCode)
