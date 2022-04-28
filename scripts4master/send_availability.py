#!/usr/bin/python3
import subprocess, json, math, argparse, time, threading
from threading import *

__author__ = "Mike Kalliafas"


statuses_dict = {
    "hostgroup-dfs-servers": {"id": "dfs", "status": None},
    "hostgroup-IIS-availability": {"id": "WebIIS","status": None},
    "hostgroup-cmf-servers": {"id": "windowsdesktop","status": None},
    "hostgroup-wsus-servers": {"id": "windowsdesktop","status": None},
    "hostgroup-afs": {"id": "WebAFS","status": None},
}


class Get_Services_Availability:


    def __init__(self, args_services, args_hostgroups, args_degraded_h, args_unavailable_h, args_degraded_s, args_unavailable_s): # 0
        with open("/root/icinga2_ldap_bind") as f:
            self.password = f.read().strip()

        global statuses_dict

        self.icinga_hostgroups = subprocess.check_output('curl --silent -u icinga2:\'' + self.password + '\' -H "Accept: application/json" http://winmonit-w01.cern.ch/icingaweb2/monitoring/list/hostgroups | python3 -m json.tool', shell=True, universal_newlines=True)
        self.hostgroups = json.loads(self.icinga_hostgroups)
        self.critical_services = args_services
        self.hostgroups_to_check = args_hostgroups

        # Hosts degraded/unavailable threasholds
        if not args_degraded_h is None:
            self.host_degraded_threashold = int(args_degraded_h[0])
        else:
            self.host_degraded_threashold = 80

        if not args_unavailable_h is None:
            self.host_unavailable_threashold = int(args_unavailable_h[0])
        else:
            self.host_unavailable_threashold = 100
        
        # Services degraded/unavailable threasholds
        if not args_degraded_s is None:
            self.service_degraded_threashold = int(args_degraded_s[0])
        else:
            self.service_degraded_threashold = 80

        if not args_unavailable_s is None:
            self.service_unavailable_threashold = int(args_unavailable_s[0])
        else:
            self.service_unavailable_threashold = 60


    def get_hostgroup_status(self): # 1
        """
        Itterates through given hostgroup and checks if the hosts and the services are available.
        If the percentage is below the given unavailable_threshold then it returns Unavailable, If it's below the given degraded_threshold it returns degraded.
        Above the given degrade_threshold it will return available if there is no critical service specified.
        If there are critical services then they are checked. If their status is not ok then
        a degraded or an unavailable status is returned
        """

        for index in range(len(self.hostgroups)):

            if self.hostgroups[index]["hostgroup_name"] in self.hostgroups_to_check:
                
                percentage_hostalive = self.convert_to_percentage(int(self.hostgroups[index]["hosts_total"]), int(self.hostgroups[index]["hosts_up"])
                    + int(self.hostgroups[index]["hosts_down_handled"])
                    + int(self.hostgroups[index]["hosts_unreachable_handled"]))

                if int(self.hostgroups[index]["services_total"]) == 0:
                    percentage_servicesOK = 100
                else:
                    percentage_servicesOK = self.convert_to_percentage(int(self.hostgroups[index]["services_total"]), int(self.hostgroups[index]["services_ok"])
                        + int(self.hostgroups[index]["services_critical_handled"])
                        + int(self.hostgroups[index]["services_warning_handled"])
                        + int(self.hostgroups[index]["services_unknown_handled"]))

                
                if  percentage_hostalive < self.host_unavailable_threashold or percentage_servicesOK <= self.service_unavailable_threashold:
                    statuses_dict[self.hostgroups[index]["hostgroup_name"]]["status"] = "unavailable"

                elif percentage_hostalive < self.host_degraded_threashold or percentage_servicesOK <= self.service_degraded_threashold:
                    statuses_dict[self.hostgroups[index]["hostgroup_name"]]["status"] = "degraded"
                else:
                    if not self.critical_services is None:
                        statuses_dict[self.hostgroups[index]["hostgroup_name"]]["status"] = self.check_host_services(index)
                    else:
                        statuses_dict[self.hostgroups[index]["hostgroup_name"]]["status"] = "available"


    def convert_to_percentage(self, total_entities, ok_entities): # 2
        """
        Converts total entities and available entities to percentage.
        """

        if total_entities <= 0:
            return 0
        else:
            return (math.floor((100*ok_entities)/total_entities))


    def check_host_services(self, index): # 3
        """
        Get the hosts from each hostgroup and request from icinga the services, that we have defined, for every host.
        If there is a service that is warning or critical it returns the availability of the service
        """
        services_warning = 0
        services_critical = 0
        icinga_hosts = subprocess.check_output('curl --silent -u icinga2:\'' + self.password + '\' -H "Accept: application/json" http://winmonit-w01.cern.ch/icingaweb2/monitoring/list/hosts?hostgroup_name='+ self.hostgroups[index]["hostgroup_name"] + ' | python3 -m json.tool', shell=True, universal_newlines=True)
        hosts = json.loads(icinga_hosts)
        for index in range(len(hosts)):
            icinga_host_services = subprocess.check_output('curl --silent -u icinga2:\'' + self.password + '\' -H "Accept: application/json" http://winmonit-w01.cern.ch/icingaweb2/monitoring/list/services?host=' + hosts[index]["host_name"] + ' | python3 -m json.tool', shell=True, universal_newlines=True)
            host_services = json.loads(icinga_host_services)
            for index2 in range(len(host_services)):
                if host_services[index2]["service_display_name"] in self.critical_services:
                    if int(host_services[index2]["service_state"]) == 1 or int(host_services[index2]["service_state"]) == 3:
                        services_warning += 1
                    elif int(host_services[index2]["service_state"]) == 2:
                        services_critical += 1


        if services_critical != 0 or services_warning != 0:
            if services_critical >= services_warning:
                return "unavailable"
            else:
                return "degraded"
        else:
            return "available"


def pass_args(services, hostgroupargs, degraded_h, unavailable_h, degraded_s, unavailable_s):
    availability = Get_Services_Availability(services, hostgroup, degraded_h, unavailable_h, degraded_s, unavailable_s)
    availability.get_hostgroup_status()


def format_statuses():
    flipped = {}
    """
    Add the ID of each hostgroup as the dictionary key in the flipped dict and as value the statuses of the hostgroup.
    This helps in cases such as the windoesdesktop id which corresponds to 2 hostgroups and by extention to two statuses.
    So having the ID as the key we can easily decide which status can be the value.
    """
    for key,value in statuses_dict.items(): 
        if not value["status"] == None:
            if value["id"] not in flipped:
                flipped[value["id"]] = [value["status"]]
            else:
                flipped[value["id"]] += [value["status"]]
    for key,value in flipped.items():
        for status in value:
            if status == "unavailable":
                flipped[key] = "unavailable"
                break # It doesn't matter if there are other statuses in the list, this is the worst case so we can break the loop
            elif status == "degraded":
                flipped[key] = "degraded"
            else:
                flipped[key] = "available"

    return flipped


def send_availability():
    # Grafana parameters
    ids_dict = format_statuses()
    producer = "wininfra"
    type = "availability"
    timestamp = ""
    availabilityinfo = ""
    availabilitydesc = ""
    contact = "service-desk@cern.ch"
    webpage = ""
    endpoint = "http://monit-metrics:10012/"

    # Send the availability for each ID in the dict
    for id,status in ids_dict.items():
        availability_json = json.dumps({
          "producer": producer,
          "type": type,
          "serviceid": id,
          "service_status": status,
          #"timestamp": datetime.now().isoformat(),
          "contact": contact
        })
        #print(availability_json)
        subprocess.check_output('curl --silent --header "Content-Type: application/json; charset=UTF-8" --request POST --data \'' + availability_json + '\' ' + endpoint, shell=True, universal_newlines=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #parser.add_argument('--check_all',required=False, help="check all hostgroups or define which with --hostgroups argument")
    parser.add_argument('-s','--services', required=False, help="The services you want to check for availability", nargs = '+')
    parser.add_argument('-H', '--hostgroups',required=True, help="Define which hostgroups to check", nargs = '+')
    parser.add_argument('-Dh', '--degraded_h',required=False, help="Set the degraded threashold for the hosts", nargs = '+')
    parser.add_argument('-Uh', '--unavailable_h',required=False, help="Set the unavailable threashold for the hosts", nargs = '+')
    parser.add_argument('-Ds', '--degraded_s',required=False, help="Set the degraded threashold for the services", nargs = '+')
    parser.add_argument('-Us', '--unavailable_s',required=False, help="Set the unavailable threashold for the services", nargs = '+')
    args = parser.parse_args()
    threads = []

    """
    Since we want to have all the threads finished before we start sending the availability,
    we start each thread seperatly and then we use join() to wait for all of them to finish. 
    This way we prevent a thread that depends on another to send the availability of a service
    that it's not yet determined. 
    Ex. Two hostgroups can answer under a common service ID, which means that we want the availability
    of both of the hostgroups to determine the availability of the service. So we want both of these 
    threads to be finished in order to have both of the statuses in the dictionary anf then to be able
    to figure out the overall service status.  
    """
    try:
        #start = time.time()
        for hostgroup in args.hostgroups:
            print(hostgroup)
            threads.append(Thread(target=pass_args, args=(args.services, hostgroup, args.degraded_h, args.unavailable_h, args.degraded_s, args.unavailable_s)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    except Exception as e:
        raise
    send_availability()


    #print(time.time()- start)
