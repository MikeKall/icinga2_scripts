$AUOptions = (Get-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU' | Select-Object -ExpandProperty AUOptions -ErrorAction SilentlyContinue)
if ($AUOptions -ge 3){
	echo "[OK] Auto updates are enabled | 'Auto Updates'=1;0;-1;0;1"
	exit(0)
}
else {
	echo "[WARNING] Auto updates are disabled | 'Auto Updates'=0;0;-1;0;1"
	exit(1)
}

