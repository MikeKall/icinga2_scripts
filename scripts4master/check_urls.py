#!/usr/bin/python3
import argparse, sys, time, requests
from threading import *

warning=0
critical=0
unknown=0
sorted_output = []

def exit_code(warning,critical,unknown):
    #print("--- %s seconds ---" % (time.time() - start_time))
    for output in sorted_output: 
        print(output)
    if critical:
        sys.exit(2)
    elif warning:
        sys.exit(1)
    elif unknown:
        sys.exit(3)
    else:
        sys.exit(0)



def Get_Status(url):
    global warning
    global critical
    global unknown
    
    try:
        resp = requests.get(url)
        status_code = resp.status_code
        print(status_code)
        if not status_code:
            print("[UNKNOWN] Could not resolve host" + url)
            unknown=1	
        elif status_code == 302 or status_code == 200 or status_code == 301:
            sorted_output.append("[OK] " + url)
        elif status_code == 404:
            sorted_output.insert(0, "[WARNING] " + url + " NOT FOUND")
            warning=1
        elif status_code == 401 or status_code == 403:
            sorted_output.append("[OK] " + url)
        elif status_code == 500:
            sorted_output.insert(0, "[CRITICAL] Internal server error for " + url)
            critical=1
        elif status_code == 503:
            sorted_output.insert(0, "[CRITICAL] Service unavailable for " + url)
            critical=1
        elif status_code == 504:
            sorted_output.insert(0, "[WARNING] Gateway timeout for " + url)
            warning=1
        else:
            sorted_output.insert(0, "[UNKNOWN] Status code " + str(status_code) + " for " + url)
            unknown=1
    except(requests.exceptions.SSLError):
        sorted_output.append("[OK] " + url)
    except(requests.exceptions.ConnectionError):
        sorted_output.append("[CRITICAL] Failed to establish a new connection: " + url)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #parser.add_argument('--check_all',required=False, help="check all hostgroups or define which with --hostgroups argument")
    parser.add_argument('-u','--urls', required=True, help="URLs to be checked", nargs = '+')
    args = parser.parse_args()
    #start_time = time.time()
    threads = []
    try:
        for url in args.urls:
            threads.append(Thread(target=Get_Status, args=[url]))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    except Exception as e:
        raise
    exit_code(warning,critical,unknown)
