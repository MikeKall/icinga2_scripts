param(
	[string]$name,
	[string]$state
)

$state = (Get-ScheduledTask -TaskName $name -ErrorAction 'SilentlyContinue' | select-object State).'State'
$results = (Get-ScheduledTaskInfo -TaskName $name -ErrorAction 'SilentlyContinue' | select-object LastTaskResult).'LastTaskResult'

if ($results -eq 0 -and $state -like '*Disabled*') {
    '[WARNING] Last run completed successfuly but task "' + $name + '" is disabled'
	exit(1)
}
elseif ($results -ne 0) {
    '[CRITICAL] Last run was unsuccessfull for task "' + $name + '"'
	exit(2)
}
else {
	'[OK] Last run completed successfuly for task "' + $name + '"'
	exit(0)
}
