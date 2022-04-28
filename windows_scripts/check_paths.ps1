## Check paths with Test-Path, works for file paths locally and network shares

param([string[]] $unc_paths=@())

$flag = 0

foreach ($path in $unc_paths) {
	$trimmed_path = $path.Trim()
	if (!(Test-Path "$trimmed_path" 2>$null)) {
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

