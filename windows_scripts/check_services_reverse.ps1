param([string[]] $services=@())

$ok = 0
$warning = 0
$critical = 0

# If the service is running return a critical message

foreach ($service in $services) {
	$status = ((Get-Service -Name "$service" -ErrorAction SilentlyContinue).Status)

	if ($status){
		if ($status -ieq 'Running'){
			$critical = 1
			$list = , "[CRITICAL] SERVICE $service is RUNNING" + $list
		}
		else {
			$list = $list + , "[OK] SERVICE $service is NOT RUNNING"
			$ok = 1
		}
	}
	else {
		$list = $list + , "[OK] SERVICE $service does not exist"
		$ok = 1
	
	}
}	

$list

if($critical){
	$exitCode = 2
}
else{
	$exitCode = 0	
}

exit($exitCode)