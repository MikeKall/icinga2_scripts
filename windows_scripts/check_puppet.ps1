$warning = 0
if (Test-Path -Path 'C:\ProgramData\PuppetLabs\puppet\var\state\agent_disabled.lock'){
    echo '[WARNING] Puppet is disabled'
    $warning = 1
}

$fqdn = [System.Net.Dns]::GetHostByName($env:computerName).HostName

$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
if (Test-Path -Path "C:\ProgramData\PuppetLabs\puppet\etc\ssl\certs\$fqdn.pem"){
    $cert.Import("C:\ProgramData\PuppetLabs\puppet\etc\ssl\certs\$fqdn.pem")
}
else{
    echo "[WARNING] $fqdn.pem does not exist"
    exit(1)
}

if ($cert.NotAfter -lt (Get-Date)) {
    echo "[CRITICAL] $fqdn.pem is expired"
    $critical = 1
}
else{
	echo "[OK] $fqdn.pem is ok"
}

if ($critical){
    exit(2)
}
elseif ($warning) {
    exit(1)
}
else {
    exit(0)
}