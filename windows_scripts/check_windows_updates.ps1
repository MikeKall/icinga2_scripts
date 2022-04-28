param(
	[string]$warning,
	[string]$critical
	)

Use-Icinga
exit Invoke-IcingaCheckUpdates -Warning $warning -Critical $critical