$parentID=(Get-CimInstance -Class Win32_Process -Filter "Name = 'icinga2.exe'").ProcessId
$powershell_checks=(Get-CimInstance Win32_Process | Where-Object { ($_.ParentProcessId -eq $parentID[0]) -or ($_.ParentProcessId -eq $parentID[1])})

foreach ($check in $powershell_checks){
    if($check.Name -like "powershell*"){
        Stop-Process -Id $check.ProcessId
     }
}

