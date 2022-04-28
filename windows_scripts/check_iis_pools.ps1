param(
	[string[]]$poolNames=@(),
	[bool]$checkAllpools
	)

Import-Module WebAdministration

if ($checkAllpools){
	$pools = (Get-ChildItem -Path IIS:\AppPools | Select-Object Name).'Name'
	foreach ($pool in $pools){
		$pool_state = (Get-WebAppPoolState -Name $pool).'Value'
		if($pool_state -like "*Started*"){
			$list = $list + , "[OK] $pool"
		}
		else{
			$list = , "[WARNING] $pool is not active" + $list
			$warning = 1
		}	
	}	
}
else{
	$pools = (Get-ChildItem -Path IIS:\AppPools | Select-Object Name).'Name'
	foreach ($pool in $poolNames){
		if($pools -contains $pool){
			$pool_state = (Get-WebAppPoolState -Name $pool).'Value'
			if($pool_state -like "*Started*"){
				$list = $list + , "[OK] $pool"
			}
			else{
				$list = , "[WARNING] $pool is not active" + $list
				$warning = 1
			}
		}
		else{
			$list = , "[WARNING] $pool does not exist" + $list
			$warning = 1
		}		
	}	
}


$list

if ($warning){
	exit(1)
}
else{
	exit(0)
}