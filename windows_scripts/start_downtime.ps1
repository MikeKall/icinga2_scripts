param(
    [string]$action = "start",
    [string]$master1 = "winmonit-m01.cern.ch",
    [string]$master2 = "winmonit-m02.cern.ch",
    [string]$hostname
    )




if (!$hostname){
    $hostname = ($env:COMPUTERNAME).ToLower()
}

# Create the json with the name and the action(start or stop downtime) 
$body="{ `"name`" : `"$hostname`", `"action`" : `"$action`" }"


function Send_Hook{
    param([string] $target)

    $url = "http://"+$target+":8666"
    try{
        Invoke-WebRequest -Uri $url -Body $body -Method "POST" -ContentType "application/json"
        return $true
    }
    catch [System.Net.WebException]{
        return $false
    }
}


if (Send_Hook $master1){
    "Hook sent to $master1"
}
elseif (Send_Hook $master2){
    "Hook sent to $master2"   
}
else{
    "Failed to send hook to either masters"
}

