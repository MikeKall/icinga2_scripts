## Check Paths with net view, works for shared printers

param([string[]] $unc_paths=@())

$flag = 0

foreach ($path in $unc_paths) {
	$trimmed_path = $path.Trim()
	if (!(net view "$trimmed_path" 2>$null)) {
		$list = , "[WARNING] $trimmed_path does not exist or access is denied" + $list
		$flag = 1
	} 
	else 
	{
		$list = $list + , "[OK] $trimmed_path"
	}
}

$list

if ($flag) {
	$exitCode = 1
}
else {
	$exitCode = 0	
}

exit($exitCode)

