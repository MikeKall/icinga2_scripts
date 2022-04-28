param(
	[string]$warning,
	[string]$critical)

#Specify the units(d for days)
$warning += 'd:'
$critical += 'd:'

Use-Icinga
exit Invoke-IcingaCheckCertificate -CertStore 'LocalMachine' -CertStorePath 'My' -CertSubject '*' -WarningEnd "$warning" -CriticalEnd "$critical"