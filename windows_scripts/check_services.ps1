param([string[]] $services=@())

$ok = 0
$warning = 0
$critical = 0

foreach ($service in $services) {
	$status = ((Get-Service -Name "$service" -ErrorAction SilentlyContinue).Status)

	if ($status){
		if ($status -ieq 'Running'){
			$list = $list + , "[OK] SERVICE $service"
			$ok = 1
			
		}
		else {
			$critical = 1
			$critical_list = , "[CRITICAL] SERVICE $service is NOT RUNNING" + $list
		}
	}
	else {
		$warning = 1
		$list = , "[WARNING] SERVICE $service DOES NOT EXIST" + $list 
	
	}
}
	
$critical_list
$list

if($critical){
	exit(2)
}
elseif($warning){
	exit(1)
}
else{
	exit(0)	
}
