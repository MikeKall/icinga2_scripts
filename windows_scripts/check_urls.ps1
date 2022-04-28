param (
    [string[]]
         [Parameter(ValueFromRemainingArguments)]
         $urls
)
$warning=0
$critical=0
$unknown=0

foreach($url in $urls){
    [net.httpWebRequest] $request= [net.httpWebRequest]::Create($url)
    $request.Method = "HEAD"
    try {
        $response = $request.getResponse()
        if (($response.StatusCode -eq "200") -or  ($response.StatusCode -eq "302") -or ($response.StatusCode -eq "301")) {
            $ok_list = $ok_list + , "[OK] $url (code $([int] $response.StatusCode))"
        }
        elseif (($response.StatusCode -eq "401") -or ($response.StatusCode -eq "403")) {
            $ok_list = $ok_list + , "[OK] $url (code $([int] $response.StatusCode))"
        }
        else{
            $ok_list = , "[UNKNOWN] Status code $response.StatusCode for $url" + $ok_list
            $unknown = 1
        }
    }
    catch [System.Net.WebException]{
		$statusCode = ([int]$_.Exception.Response.StatusCode.value__ ).ToString().Trim();
		if ($statusCode -eq "404") {
			$warning_list = $warning_list + , "[WARNING] $url not found (code $statusCode)"
			$warning = 1
		}
		elseif (($statusCode -eq "401") -or ($statusCode -eq "403")) {
			$ok_list = $ok_list + , "[OK] $url (code $statusCode)"
		}
		elseif($statusCode -eq "500"){
			$critical_list = $critical_list + , "[CRITICAL] Internal server error for $url (code $statusCode)"
			$critical = 1
		}
		elseif($statusCode -eq "503"){
			$critical_list = $critical_list + , "[CRITICAL] Service unavailable for $url (code $statusCode)"
			$critical = 1
		}
		elseif($statusCode -eq "504"){
			$warning_list = $warning_list + , "[WARNING] Gateway timeout for $url (code $statusCode)"
			$warning = 1
		}
		else{
			$ok_list = , "[UNKNOWN] Status code $statusCode for $url" + $ok_list
			$unknown = 1
		}
    }
}

$critical_list
$warning_list
$ok_list

if ($critical){
    exit(2)
}
elseif ($warning) {
    exit(1)
}
elseif ($unknown) {
    exit(3)
}
else {
    exit(0)
}
