param([string]$time)

$events = (Get-EventLog -LogName System -Source Microsoft-Windows-WHEA-Logger -After (Get-Date).AddHours(-$time) -ErrorAction SilentlyContinue)

$NoEvents = 1
$warning = 0
$critical = 0
$events_count = 0

foreach ($event in $events) {
    if ((($event | Select-Object -ExpandProperty Message) -like "*Component: Memory*")) {
        if (($event | Select-Object -Property EntryType) -like "*Warning*") {
            $MemWarningList = $MemWarningList + , ($event | Format-Table -Property @{L = "State"; E = { echo "[WARNING]" }; width = 10 }, @{L = "Hardware"; E = { echo "Memory" }; width = 10 }, @{L = "Index"; E = { $_.Index }; width = 10; align = 'left' }, @{L = "Time"; E = { $_.TimeGenerated }; width = 25 }, @{L = "Message"; E = { $_.Message }; width = 40 } -Wrap)
        }
        elseif (($event | Select-Object -Property EntryType) -like "*Error*") {
            $MemCriticalList = $MemCriticalList + , ($event | Format-Table -Property @{L = "State"; E = { echo "[CRITICAL]" }; width = 10 }, @{L = "Hardware"; E = { echo "Memory" }; width = 10 }, @{L = "Index"; E = { $_.Index }; width = 10; align = 'left' }, @{L = "Time"; E = { $_.TimeGenerated }; width = 25 }, @{L = "Message"; E = { $_.Message }; width = 40 } -Wrap)
        }
        $NoEvents = 0
        $events_count += 1
    }
    elseif (($event | Select-Object -ExpandProperty Message) -like "*Component: CPU*") {
        if (($event | Select-Object -Property EntryType) -like "*Warning*") {
            $CPUWarningList = $CPUWarningList + , ($event | Format-Table -Property @{L = "State"; E = { echo "[WARNING]" }; width = 10 }, @{L = "Hardware"; E = { echo "CPU" }; width = 10 }, @{L = "Index"; E = { $_.Index }; width = 10; align = 'left' }, @{L = "Time"; E = { $_.TimeGenerated }; width = 25 }, @{L = "Message"; E = { $_.Message }; width = 40 } -Wrap)
        }
        elseif (($event | Select-Object -Property EntryType) -like "*Error*") {
            $CPUWarningList = $CPUWarningList + , ($event | Format-Table -Property @{L = "State"; E = { echo "[CRITICAL]" }; width = 10 }, @{L = "Hardware"; E = { echo "CPU" }; width = 10 }, @{L = "Index"; E = { $_.Index }; width = 10; align = 'left' }, @{L = "Time"; E = { $_.TimeGenerated }; width = 25 }, @{L = "Message"; E = { $_.Message }; width = 40 } -Wrap)
        }
        $NoEvents = 0
        $events_count += 1
    }
}

# The blocks below are used to print the critical messages first and then the warning
#If ($NoEvents){
# echo "[OK] No events found in the last $time hour(s)"
#}
#else{
if ($MemCriticalList.Count -ne 0) {
    foreach ($item in $MemCriticalList) {
        $item
    }
    $critical = 1
}

if ($CPUCriticalList.Count -ne 0) {
    foreach ($item in $CPUCriticalList) {
        $item
    }
    $critical = 1
}

if ($MemWarningList.Count -ne 0) {
    foreach ($item in $MemWarningList) {
        $item
    }
    $warning = 1
}

if ($CPUWarningList.Count -ne 0) {
    foreach ($item in $CPUWarningList) {
        $item
    }
    $warning = 1
}
#}

if ($critical) {
    echo " | 'Events'=$events_count"
    exit(2)
}
elseif ($warning) {
    echo " | 'Events'=$events_count"
    exit(1)
}
else {
    echo " | 'Events'=$events_count"
    exit(0)
}