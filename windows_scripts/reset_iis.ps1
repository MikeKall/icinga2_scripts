param (
    [string[]]$state
)

if(($state -eq "WARNING") -or ($state -eq "CRITICAL") -or ($state -eq "UNKNOWN")){
    echo "[$(Get-Date -Format 'yyyy/MM/dd HH:mm:ss]') IIS Handler: Starting" >> C:\ProgramData\icinga2\var\log\icinga2\event_handler.log
    try {
        iisreset /noforce
        echo "[$(Get-Date -Format 'yyyy/MM/dd HH:mm:ss]') IIS Handler: Executed" >> C:\ProgramData\icinga2\var\log\icinga2\event_handler.log
    }
    catch {
        echo "[$(Get-Date -Format 'yyyy/MM/dd HH:mm:ss]') IIS Handler: Failed to reset IIS" >> C:\ProgramData\icinga2\var\log\icinga2\event_handler.log
    }	
}
