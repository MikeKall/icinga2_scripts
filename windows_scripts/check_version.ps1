param(
	[string]$target_framework_version,
	[string]$target_plugins_version,
	[string]$target_icinga_version
	)


$current_framework_version = (Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\icinga-powershell-framework').DisplayVersion

$current_plugins_version = (Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\icinga-powershell-plugins').DisplayVersion

$current_icinga_version = (Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{124C420D-D80B-49F4-9FE7-3C8E51E41FA0}').DisplayVersion


$warning = 0

if ($current_framework_version -ne $target_framework_version){
	$list = , "[WARNING] Framework version is $current_framework_version. It should be $target_framework_version" + $list
	$warning = 1
}
else{
	$list = $list + , "[OK] Framework version is $current_framework_version"	
}

if ($current_plugins_version -ne $target_plugins_version){
	$list = , "[WARNING] Plugins version is $current_plugins_version. It should be $target_plugins_version" + $list
	$warning = 1
}
else{
	$list = $list + , "[OK] Plugins version is $current_plugins_version"	
}

if ($current_icinga_version -ne $target_icinga_version){
	$list = , "[WARNING] Icinga version is $current_icinga_version. It should be $target_icinga_version" + $list
	$warning = 1
}
else{
	$list = $list + , "[OK] Icinga version is $current_icinga_version"	
}

$list

if ($warning -eq 1){
	exit 1
}
else{
	exit 0
}

