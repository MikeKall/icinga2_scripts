param(
	[string]$days=-7
)

$date = (Get-Date).AddDays($days)

$definition_date = (Get-WmiObject -Namespace root\Microsoft\SecurityClient -class AntimalwareHealthStatus -Property "AntivirusSignatureUpdateDateTime" | Select "AntivirusSignatureUpdateDateTime" -ExpandProperty "AntivirusSignatureUpdateDateTime")

if  ((Get-Date $definition_date) -lt $date){
	"[CRITICAL] Virus definitions are not updated. Last update: " + $definition_date
	exit(2)
}
else{
	"[OK] Virus definitions are up to date"
	exit(0)
}
