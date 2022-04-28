param(
	[string]$counter,
	[string]$samples,
	[string]$interval,
	[string]$warning,
	[string]$critical
)

$values = (Get-Counter -Counter $counter -SampleInterval $interval -MaxSamples $samples).CounterSamples.CookedValue 

$average = 0
foreach ($value in $values){
	$average += $value 
}

$average = [math]::Round($average / $samples ,1)

if ($average -ge $critical){
	echo "[CRITICAL] The value of the counter $counter is $average | 'Counter'=$average;$warning;$critical"
	exit 2
}
elseif ($average -ge $warning){
	echo "[WARNING] The value of the counter $counter is $average | 'Counter'=$average;$warning;$critical"
	exit 1
}
else{
	echo "[OK] The value of the counter $counter is $average | 'Counter'=$average;$warning;$critical"
	exit 0
}
