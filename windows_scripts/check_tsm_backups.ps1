param(
    [string]$days=-1
)

try{
	if (Test-Path 'C:\Program Files\Tivoli\TSM\baclient\dsmsched.log'){
		
		$logs = ((Get-Content 'C:\Program Files\Tivoli\TSM\baclient\dsmsched.log').Split([Environment]::NewLine))
		$date = (Get-Date).AddDays($days)

		$ok_flag = 0
		$error_flag = 0
		$date_index = 0
		$report_counts = 0
		$current_date_errors = 0
		$errors_counter = 0
		$missing_report_flag = $false
		
		# Start reading the file from the bottom up
		for ($x = $logs.Length; $x -ge 0; $x--){
			# Skip empty lines
			if ($logs[$x] -ne ""){
				
				# split on space
				$splitUp = $logs[$x] -split "\s+"

				# Parse the dates
				if ([string]$($splitUp[0] + " " + $splitUp[1]) -as [DateTime]){
					$log_date += , ($splitUp[0] + " " + $splitUp[1])

					<#
					# Debugging
					" "
					"Log date is: " + $log_date[$date_index]
					"Date is: $date"
					" "
					"Log date is greater that given date: " + ($log_date[$date_index] -gt $date)
					" "
					" "
					# ===============
					#>
					# Checks the logs from log date to given date
					if ($log_date[$date_index] -gt $date){

						if ($logs[$x] -like "*completed successfully*"){
							$ok_flag = 1
							break
						}
						if ($logs[$x] -like "* failed.*"){
							$current_date_errors++
							$output += , "=== Error $current_date_errors ===" + " "
							for ($prev_lines = 35; $prev_lines -ge 0; $prev_lines--){
								$output = $output + , $logs[$x - $prev_lines]
							}
							$x -= 35
							$error_flag = 1
							$output += , "`n"
						}
						
						# A very unlikely case but it may happen 
						If ((New-Timespan -Start $log_date[$date_index] -End $log_date[$date_index - 1]).Days -ge 1){
							$missing_reports += , ("Missing report between: " + $log_date[$date_index - 1] + " and " + $log_date[$date_index])
							$missing_report_flag = $true
							$report_counts++
						}
					} 
					# If the first if case returns false and the x is checking the 
					# first line of the file then there is a missing report.
					elseif (($x -ge $logs.Length - 1) -or ($report_counts -gt 0)){
						$missing_reports += , ("Missing report between: " + $log_date[$date_index - 1] + " and " + $date)
						$missing_report_flag = $true
					}
					else{
						break
					}
					
					# ============================================================================================
                    
                   
					# If the first date isn't in the given range it means that there are missing reports
					# I check the 1/4 of the file since to do a check in accordance with the dates it's very tricky possible.
					# To check the dates we need to have the current date and to compare it with the next one. This is a linear 
					# search so if I try to access the next date in the list (meaning the one that it's not yet read by the script) it will return null 

					if ($missing_report_flag -and ($x -gt ($logs.Length)*3/4)){
						if ($logs[$x] -like "*completed successfully*"){
							$ok_flag = 1
							break
						}
						elseif ($logs[$x] -like "*failed*"){
							$errors_counter++
							$output += , "=== Error $errors_counter ===" + " "
							for ($prev_lines = 35; $prev_lines -ge 0; $prev_lines--){
								$output = $output + , $logs[$x - $prev_lines]
							}
							$error_flag = 1
							$output += , "`n"
							$x -= 35
						}
					}
					elseif ($x -lt ($logs.Length)*3/4){
						break
					}
					$date_index++
				}
			}
		}

		$total_errors = $errors_counter + $current_date_errors
		$output = "Found $total_errors error(s) `n" , $output
		
		$critical = 0
		$warning = 0	
		if ($error_flag){
			$critical = 1
		}
		if($missing_report_flag){
			$warning = 1
		}

		if($critical -and $warning){
			echo "[CRITICAL] TSM Backup Failed, please review: "
			echo " "
			$output
			echo ""
			echo "================================="
			echo ""
			echo "[WARNING] There are missing report(s)"
			$missing_reports
			echo ""
			echo "================================="
			echo "| Backup fails=$total_errors"
			exit(2)
		}
		elseif($critical){
			echo "[CRITICAL] TSM Backup Failed, please review: "
			echo " "
			$output
			echo "| Backup fails=$total_errors"
			exit(2)
		}
		elseif($warning){
			echo "[WARNING] There are missing report(s)"
			$missing_reports
			echo "| Backup fails=$total_errors"
			exit(1)
		}
		else{
			echo "[OK] No errors found"
			echo "| Backup fails=$total_errors"
			exit(0)
		}

	}
	else{
		echo "[OK] The client isn't installed"
		exit (0)
	}
}
catch{
	echo "An error occured"
    echo $_
    exit(2)
}