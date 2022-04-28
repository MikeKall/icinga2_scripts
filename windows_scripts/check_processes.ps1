param([string[]]$processes=@())

foreach ($process in $processes){
	$isRunning = (Get-Process $process -ErrorAction SilentlyContinue)
	if($isRunning) {
		$list = $list + , "[OK] The process $process is running"
		$exitCode = 0
	}
	else {
		$list = , "[CRITICAL] The process $process is not running" + $list
		$exitCode = 2
	}	
}

$list

exit($exitCode)