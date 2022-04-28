param(
    [string[]]$databases=@()
)

# Today minus 7 days
$pastdate = (Get-Date).AddDays(-7).ToString('yyyy/MM/dd')
$text

# Loop through the databases received from param
foreach ($db in $databases) {
    # Get code and date from file, it will be in format 'code - date'
    $res = Get-Content "D:\MSSQL\checks\$db.txt"
    $code = $($res.Split(' '))[0]
    $date = [datetime]::parseexact($($res.Split(' '))[2], 'yyyy/MM/dd', $null)

    # If restore date is older than 7 days, raise 1 WARNING
    if ($date -lt $pastdate) {
        $exitCode = 1
    # If restore date is within limits, return original status code
    } else {
        $exitCode = $code
    }

    # Prepare the text per DB depending on its exitCode
    # Also raise flag per type of alarm level for later exit
    switch ($exitCode) {
        0 { $text_ok += , "[OK] $db"}
        1 { $text_warning += , "[WARNING] $db restore needs to be checked"; $flagW = $true }
        2 { $text_critical += , "[CRITICAL] $db restore went wrong"; $flagC = $true }
    }
}

# Printout text, icinga will take it for the notification
# Exit with the higher flag/code raised, or 0 if none
if ($flagC) { $text_critical; $text_warning; $text_ok; Exit 2 }
if ($flagW) { $text_warning; $text_ok; Exit 1 }
$text_ok;
Exit 0