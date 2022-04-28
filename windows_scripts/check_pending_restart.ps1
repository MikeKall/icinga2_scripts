if (Test-Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired"){
	echo "[WARNING] There is a pending restart"
	exit(1)
}
else{
	echo "[OK] No pending restart"	
	exit(0)
}