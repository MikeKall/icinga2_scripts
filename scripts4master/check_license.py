#!/bin/python3

from ast import If
from datetime import date
import datetime
import argparse
from logging import WARNING
import subprocess, socket, sys
#from subprocess import *


# These lists are used to determine the exit code
feature_criticals = []
feature_warnings = []
daemon_criticals = []



class Check_License:
        
        def __init__(self, args_critical, args_warning): 
                
                self.output_for_icinga = []
                
                if args_critical:
                        self.critical = datetime.timedelta(days=int(args_critical))
                else:
                        self.critical = datetime.timedelta(days=30)
                
                if args_warning:
                        self.warning = datetime.timedelta(days=int(args_warning))
                else:
                        self.warning = datetime.timedelta(days=60)


                if self.warning < self.critical:
                        print("[CRITICAL] Critical threashold can't be greater than warning threshold")
                        sys.exit(2)
                
        
        def RLM(self, daemon):        
                licflag = False 
                ok_flag = True
                expiration_dates_constants = []

                # In this part we check if the license server and daemon are UP and running 
                try:
                        command = subprocess.check_output(['/bin/rlmutil','rlmstat','-a ','-c', daemon], universal_newlines=True)
                        formatted_command = command.split('\n')

                        for index in range(len(formatted_command)):                          
                                # Searching for unique phrases in the output so that
                                # the if case will be accessed only once, when that
                                # unique line is read
                                if  "rlm status on" in formatted_command[index] and "up" in formatted_command[index]:
                                        # License server is ok
                                        licflag = True
                                if 'exp' in formatted_command[index]:
                                        feature = formatted_command[index-1].split(" ")[0].replace('\t', '')
                                        exp_date = formatted_command[index].split(" ")[-1]
                                        status, formatted_expiration = self.checkExpiration(exp_date)     

                                        if status == 'WARNING':
                                                self.output_for_icinga.insert(0, "[WARNING] " + daemon + ": Feature " + feature + " expires on " +  str(formatted_expiration))
                                                feature_warnings.append(True)
                                                ok_flag = False
                                        elif status == 'CRITICAL':
                                                self.output_for_icinga.insert(0, "[CRITICAL] " + daemon + ": Feature " + feature + " expires on " + str(formatted_expiration))
                                                feature_criticals.append(True)
                                                ok_flag = False          

                                        index += 3               

                                
                                                 
                        if not licflag:
                                self.output_for_icinga.insert(0, "[CRITICAL] " + daemon + " license server is down")
                                daemon_criticals.append(True)
                                return
                        if ok_flag:
                                self.output_for_icinga.append("[OK] " + daemon + " " + formatted_command[index].split(" ")[0])
                        
                except(FileNotFoundError):
                        print("File lmutil does not exist")
                        sys.exit(2)
                except(subprocess.CalledProcessError):
                        self.output_for_icinga.insert(0, "[WARNING] Daemon " + daemon + " does not exist")
                        feature_warnings.append(True)
                        return
                except Exception as e:
                        self.output_for_icinga.insert(0, "[CRITICAL] An unexpected error occured while trying to check " + daemon)
                        print(e)
                        daemon_criticals.append(True)
                        return

        
        def FlexLM(self, daemon):
                licflag = False 
                daemonflag = True
                ok_flag = True
                expiration_dates_constants = ['1-jan-0', '25-dec-0000']

                #hostname = daemon.split("@")[1]

                # In this part we check if the license server and daemon are UP and running 
                try:
                        command = subprocess.check_output(['/bin/lmutil', 'lmstat', '-c', daemon], universal_newlines=True)
                        formatted_command = command.split('\n') 

                        for line in formatted_command:
                                
                                # Searching for unique phrases in the output so that
                                # the if case will be accessed only once, when that
                                # unique line is read
                                if  "license server UP" in line:
                                        licflag = True
                                if "daemon is down" in line:
                                        daemonflag = False
                                        
                                                 
                        if not daemonflag:
                                self.output_for_icinga.insert(0, "[CRITICAL] " + daemon + " daemon isn't running")
                                daemon_criticals.append(True)
                                return
                        elif not licflag:
                                self.output_for_icinga.insert(0, "[CRITICAL] " + daemon + " license server is down")
                                daemon_criticals.append(True)
                                return
                except(FileNotFoundError):
                        print("File lmutil does not exist")
                        sys.exit(2)
                except(subprocess.CalledProcessError):
                        self.output_for_icinga.insert(0, "[WARNING] Daemon " + daemon + " does not exist")
                        feature_warnings.append(True)
                        return
                except:
                        self.output_for_icinga.insert(0, "[CRITICAL] An unexpected error occured while trying to check " + daemon)
                        daemon_criticals.append(True)
                        return

                
                
                # =========================================================================================================



                # Checking the expiration of the Features
                try:
                        command = subprocess.check_output(['/bin/lmutil','lmstat', '-i', '-c', daemon], universal_newlines=True)

                        features = self.parse_feature_details(command.split('\n'))

                        for feature in features:

                                if feature[3] in expiration_dates_constants:
                                        continue
                                        

                                status, expiration_date = self.checkExpiration(feature[3])
                                if status == 'WARNING':
                                        self.output_for_icinga.insert(0, "[WARNING] " + daemon + " " + feature[4] + ": Feature " + feature[0] + " expires on " +  str(expiration_date))
                                        feature_warnings.append(True)
                                        ok_flag = False
                                elif status == 'CRITICAL':
                                        self.output_for_icinga.insert(0, "[CRITICAL] " + daemon + " " + feature[4] + ": Feature " + feature[0] + " expires on " + str(expiration_date))
                                        feature_criticals.append(True)
                                        ok_flag = False


                        if ok_flag:
                                self.output_for_icinga.append("[OK] " + daemon + " " + feature[4])
                except(FileNotFoundError):
                        print("File lmutil does not exist")
                        sys.exit(2)
                except(subprocess.CalledProcessError):
                        feature_warnings.append(True)
                except Exception as e:
                        print("An unexpected error occured")
                        return
                
                # ========================================================================================================

        def parse_feature_details(self, command_results):
                """
                The lines that we are interested in are like this:

                Feature			Version	    licenses    Expires		Vendor
                _______			_______	  __________    _______		______ 
                ipsb_5FA2              	1.0	      9999	29-feb-2024	xilinxd
                """
                
                start_reading = False
                skip_next_line = False
                features = []
                formatted_line = []
                for line in command_results:

                        # Skip empty lines
                        if line:
                                if "Feature" in line:
                                        skip_next_line = True
                                        continue
                                if skip_next_line:
                                        start_reading = True
                                        skip_next_line = False
                                        continue
                                if start_reading:

                                        # Remove the spaces and the tabs from the output
                                        # and spit the words in a new array
                                        formatted_line = line.strip().replace("\t", " ").split()
                                        features.append(formatted_line)
                return features



        def checkExpiration(self, expiration):
                # Format dates
                expiration_date = datetime.datetime.strptime(expiration, '%d-%b-%Y').strftime('%d-%m-%Y')

                current_date = date.today().strftime("%d-%m-%Y")
                #===============================================

                # Parse dates and display the difference in days
                date_difference = datetime.datetime.strptime(expiration_date, '%d-%m-%Y') - datetime.datetime.strptime(current_date, '%d-%m-%Y')
                
                
                zero_timeDelta = datetime.timedelta(days=0)

                if date_difference - self.warning <= zero_timeDelta and date_difference - self.critical > zero_timeDelta:
                        return 'WARNING', expiration_date
                elif date_difference - self.critical <= zero_timeDelta:
                        return 'CRITICAL', expiration_date
                else:
                        return 'OK', expiration_date
                                        


                

if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument('-t','--type', required=False, help='License type')
        parser.add_argument('-d','--daemon', required=False, help='Folder name of license', nargs='+')
        parser.add_argument('-c','--critical', required=False, help='Critical threashold in days')
        parser.add_argument('-w','--warning', required=False, help='Warning threashold in days')
        args = parser.parse_args()
        
        license_status = Check_License(args.critical, args.warning)

        if not args.daemon[0]:
                print("[OK] No daemons to check")
                sys.exit(0)
        
        if not args.type:
                args.type = 'flexlm'

        if args.type == 'flexlm':                       

                # Icinga passes the daemons as a string. The daemons are seperated by spaces
                # "2000@lxlicen01 1717@lxlicen01 1710@lxlicen01 27000@lxlicen01 1701@lxlicen01" 
                for daemon in args.daemon[0].split(" "):
                        license_status.FlexLM(daemon)
        if args.type == 'rlm':
                license_status = Check_License( args.critical, args.warning)

                for daemon in args.daemon[0].split(" "):
                        license_status.RLM(daemon)
                

        for info in license_status.output_for_icinga:
                print(info)

        if True in feature_criticals or True in daemon_criticals:
                sys.exit(2)
        elif True in feature_warnings and not True in daemon_criticals:
                sys.exit(1)
        else:
                sys.exit(0)
