param(
	[string[]]$usb_devices=@(),
	[switch]$check_untrusted
	)

$plugged_in_usb_devices=(gwmi Win32_USBControllerDevice |%{[wmi]($_.Dependent)} | Select-Object Name).'Name'



foreach ($device in $usb_devices){
	if ($plugged_in_usb_devices -contains $device){
		$list = $list + , "[OK] $device is plugged in"
		$ok = 1
	}
	else{
		$list = , "[WARNING] $device is missing" + $list 
		$ok = 0
	}
}


# Search for unrecognised devices
if ($check_untrusted){
	foreach ($device in $plugged_in_usb_devices){
		if (!($usb_devices -contains $device)){
			$list = , "[WARNING] $device might be untrusted device" + $list
			$ok = 0
		}
	}	
}
	


$list

if ($ok){
	exit(0)
}
else{
	exit(1)
}