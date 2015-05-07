#! /usr/bin/env python

# *
# * Copyright (c) 2015 Cisco Systems, Inc. and others.  All rights reserved.
# *
# * This program and the accompanying materials are made available under the
# * terms of the Eclipse Public License v1.0 which accompanies this
# * distribution, and is available at http://www.eclipse.org/legal/epl-v10.html
# *
# * python show_tech.py -v IWAN-SRBR-EIGRP.virl -t IWAN -r all
# * python show_tech.py -v IWAN-SRBR-EIGRP.virl -t IWAN -r MCBRbranch

import logging
import getopt
import sys
import rtrlib
from xml.dom import minidom

logging.basicConfig(level=logging.WARNING)

fn_virl = None
element_address = None
username = "cisco"
password = "cisco"
tech_type = "IWAN"

def parse_command_line(args):
    """
    Parse the command line options. If the required argument "-a" for element address or FQDN is not provided,
    this method displays the proper usage information and calls sys.exit(1).

    @param args  The args string passed into the main(...) method.
    
    @return true if parsing the command line succeeds, false otherwise.
    """
    try:
        opts, args = getopt.getopt(args[1:],"hav:t:r:u:p:",
                                   ["address=","virl=",
                                    "type=","router=","username=","password="])
    except getopt.GetoptError as err:
        print str(err)
        logger.info(get_usage())
        sys.exit(2)
    
    """
     * options:
     *       -a, --address <network element address or FQDN>
     *       -v, --virl <virl file>
     *       -r, --router <router name>
     *       -u, --username <name of user> must be privelege level 15
     *       -p, --password <password of user>
    """     
    for option, arg in opts:
        if option == '-h':
            logger.info(get_usage())
            sys.exit()
        elif option in ("-a", "--address"):
            global element_address
            element_address = arg
        elif option in ("-v", "--virl"):
            global fn_virl
            fn_virl = arg
        elif option in ("-r", "--router"):
            global router
            router = arg
        elif option in ("-u", "--username"):
            global username 
            username = arg
        elif option in ("-p", "--password"):
            global password 
            password = arg
        elif option in ("-t", "--type"):
            global tech_type 
            tech_type = arg

    if((element_address==None) and (fn_virl==None)):
        logger.error(get_usage())
        return False
    
    return True
    
def get_usage():
        return " Usage: -a <address or FQDN> -t <type> -v <virl file> -r <router name>"

if __name__=='__main__':
   logger = logging.getLogger('telnet')
   logger.setLevel(logging.INFO)
   if not parse_command_line(sys.argv):
      logger.error("Error in parsing arguments")
      sys.exit(1)

   virldoc = minidom.parse(fn_virl)
   nodelist = virldoc.getElementsByTagName('node')
   invalid = None
   for n in nodelist:
       nodeName = n.attributes['name'].value
       entries = n.getElementsByTagName('entry')
       for e in entries:
           k = e.attributes['key'].value
           t = e.attributes['type'].value
           d = "none"
           if (e.firstChild != None):
               d = e.firstChild.data

           if (k == 'static_ip'):
               print('{0:20} {1:16}'.format(nodeName, d))
               if (router == 'all'):
                   rtr = rtrlib.Rtr(d, password)
                   str = rtr.show_version()
                   print str
                   str = rtr.show_health(tech_type)
                   print str

               elif (router == nodeName):
                   rtr = rtrlib.Rtr(d, password)
                   str = rtr.show_version()
                   print str
                   str = rtr.show_health(tech_type)
                   print str
                   break;
               else:
                   invalid = router
                   break;
   
   print "*********Finished"
