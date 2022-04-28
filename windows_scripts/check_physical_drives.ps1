param(
    [string]$controller,
    [string]$enclosure,
    [string]$slot
)
$ErrorActionPreference = 'SilentlyContinue'
$ok = 0
$warning = 0
$critical = 0
$critical_disk_count = 0 # For influx metrics


$res = (& "C:\Program Files (x86)\MegaRAID Storage Manager\StorCLI.exe" /c$controller/e$enclosure/s$slot show)
if (!$res){
    echo "[WARNING] The StoreCli is not installed"
    exit(1)
}
    else{

    foreach ($line in $res){
        if ($line -like "* Onln *"){
            $list = $list + , "[OK] $line"
            $ok = 1
        }
        elseif ($line -like "* GHS *"){
            $list = $list + , "[OK] $line"
            $ok = 1
        }
        elseif($line -like "* Offln *"){
            $critical_list = , "[CRITICAL] $line" + $critical_list
            $critical = 1
            $critical_disk_count += 1
        }
        elseif($line -like "* F *"){
            $list = , "[WARNING] $line" + $list
            $warning = 1
        }
        elseif($line -like "* UGood *"){
            $list = $list + , "[OK] $line"
            $ok = 1
        }
        elseif($line -like "* UBad *"){
            $critical_list = , "[CRITICAL] $line" + $critical_list
            $critical = 1
            $critical_disk_count += 1
        }
        elseif($line -like "* Rbld *"){
            $critical_list = , "[CRITICAL] $line" + $critical_list
            $critical = 1
            $critical_disk_count += 1
        }
    }

    $res = (& "C:\Program Files (x86)\MegaRAID Storage Manager\StorCLI.exe" /c$controller/bbu show)

    foreach ($line in $res){
        if ($line -like "* Onln *"){
            $list = $list + , "[OK] $line"
        }
        elseif ($line -like "* GHS *"){
            $list = $list + , "[OK] $line"
        }
        elseif($line -like "* Offln *"){
            $critical_list = , "[CRITICAL] $line" + $critical_list
        }
        elseif($line -like "* F *"){
            $list = , "[WARNING] $line" + $list
        }
        elseif($line -like "* UGood *"){
            $list = $list + , "[OK] $line"
        }
        elseif($line -like "* UBad *"){
            $critical_list = , "[CRITICAL] $line" + $critical_list
        }
        elseif($line -like "* Rbld *"){
            $critical_list = , "[CRITICAL] $line" + $critical_list
        }
        elseif($line -like "* Dgd *"){
            $list = , "[WARNING] $line" + $list
        }
    }

    $critical_list
    $list

    if ($critical){
        echo " | 'Critical Physical disks'=$critical_disk_count;"
        exit(2)
    }
    elseif ($warning){
        echo " | 'Critical Physical disks'=$critical_disk_count;"
        exit(1)
    }
    else {
        echo " | 'Critical Physical disks'=$critical_disk_count;"
        exit(0)
    }
}