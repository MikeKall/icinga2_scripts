param ([string[]]$users)

# Check if the users have a process running. If they do they are active/logged in.
foreach($user in $users){
	$res = (query user $user)
	if(($res -like "*Active*") -or ($res -like "*Disc*")){
		$output = $output + , "[OK] User $user is logged in`n"
		$critical = 0
	}else{
		$output = , "[CRITICAL] User $user is not logged in`n" + $output
		$critical = 1
	}
}

if($critical){
	$output
	exit(2)
}else{
	$output
	exit(0)
}
