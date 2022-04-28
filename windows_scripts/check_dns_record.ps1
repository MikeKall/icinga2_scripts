# Script to check if a given Computer shows up in a give DNS Name record
# Script is tailored to icinga2, if one wants to run it manually, comment out the exit codes

[CmdletBinding()]
param (
    [Parameter(Mandatory = $true)][String[]]$DnsName,
    [Parameter(Mandatory = $false)][string]$ComputerName,
    [Parameter()][string]$DnsSection = "Answer",
    [Parameter()][ValidateSet("IPv4", "IPv6", "All")]$IPvType="All",
    [Parameter()][string]$DnsServer

)
$ErrorActionPreference = "Stop"

if (!$ComputerName) { $ComputerName = $env:COMPUTERNAME }

$DnsRecord = $null
$Hosts = $null
$RecordType = $null

foreach ($i in $DnsName) {

# Get DNS Record, filtered out some garbage
try {
    if($DnsServer){
    $DnsRecord = Resolve-DnsName $i -Server $DnsServer | Select-Object * | Where-Object { $_.Name.StartsWith($i) -and $_.Section -eq $DnsSection }
    }
    else
    {
    $DnsRecord = Resolve-DnsName $i | Select-Object * | Where-Object { $_.Name.StartsWith($i) -and $_.Section -eq $DnsSection }
    }
    
    #CNAME and other records cannot co-exist, so we pull the record type from the first item (AAAA and A are considered the same for the purpose of this script)

    $RecordType = $DnsRecord[0].Type
}
catch {
    Write-Host "[WARNING] $_" 
    $warning = $true
}

# AAAA or A Records
if($RecordType -notmatch "CNAME"){

    switch ($IPvType) {

        "IPv4" {
            # Get hosts in DNS Record with IPv4
            $Hosts = $DnsRecord |  ForEach-Object { if ($_.IPAddress) { [System.Net.Dns]::GetHostEntry($_.IPAddress).HostName } }   
        }

        "IPv6" {
            # Get hosts in DNS Record with IPv6
            $Hosts = $DnsRecord |  ForEach-Object { if ($_.IPAddress) { [System.Net.Dns]::GetHostEntry($_.IPAddress).HostName } }
        }

        default {
            # Get hosts in DNS Record with both IPv4 and IPv6
            $Hosts = $DnsRecord |  ForEach-Object { if ($_.IPAddress) { [System.Net.Dns]::GetHostEntry($_.IPAddress).HostName } }
        }
    }
}
# CNAME Records
else {   
    $Hosts = $DnsRecord.Server
}

# Select unique hostnames
$Hosts = $Hosts | Select-Object -Unique | Sort-Object -Descending


# If there are no hosts in the DNS record this is Critical
if ($Hosts.Count -lt 1) {
    Write-Host "[CRITICAL] There are no hosts in $RecordType $i - admins should take a look inmmediately!" 
    $critical = $true
}

# Check if the give Computer is not included in the DNS record. Exception for Domain Controllers, where "CERN.CH"is hardcoded in the hosts file, thus they will look up there first.
if ($Hosts -contains "CERN.CH") {
    # It's a DC
    Write-Host "[OK] $ComputerName is in $RecordType $i`nThere are currently $($Hosts.Count) host(s) in $i`n$($Hosts -join "`r`n" | Out-String)"
}
elseif ($Hosts -match $ComputerName) {
    # It's not a DC
    Write-Host "[OK] $ComputerName is in $RecordType $i`nThere are currently $($Hosts.Count) host(s) in $i`n$($Hosts -join "`r`n" | Out-String)"

}
else {
    Write-Host "[WARNING] $ComputerName is not in $RecordType $i`nThere are currently $($Hosts.Count) host(s) in $i`n$($Hosts -join "`r`n" | Out-String)" 
    $warning = $true
}
}

if($critical){exit(2)}
elseif($warning){exit(1)}
else{ exit(0)}
