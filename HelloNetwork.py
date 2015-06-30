#! /usr/bin/env python

# *
# * Copyright (c) 2015 Cisco Systems, Inc. and others.  All rights reserved.
# *
# * This program and the accompanying materials are made available under the
# * terms of the Eclipse Public License v1.0 which accompanies this
# * distribution, and is available at http://www.eclipse.org/legal/epl-v10.html
# *

# * python HelloNetwork.py -a 172.16.1.10

import logging
import getopt
import sys
import rtrlib

logging.basicConfig(level=logging.WARNING)

element_address = None
port = None
username = "cisco"
password = "cisco"

def parse_command_line(args):
    """
    Parse the command line options. If the required argument "-a" for element address or FQDN is not provided,
    this method displays the proper usage information and calls sys.exit(1).

    @param args  The args string passed into the main(...) method.
    
    @return true if parsing the command line succeeds, false otherwise.
    """
    try:
        opts, args = getopt.getopt(args[1:],"ha:u:p:n:",["address=","username=", "password=", "netapp=", "transport=", "rootcert=", "clientcert=", "key="])
    except getopt.GetoptError as err:
        print str(err)
        logger.info(get_usage())
        sys.exit(2)
        return False

    print args
    print opts

    if (len(args) == 0):
        logger.error(get_usage())
        return False

    if (len(args) > 2):
        logger.error(get_usage())
        return False

    global element_address
    element_address = args[0]

    if (len(args) == 2):
        global port
        port = args[1]
        
    print element_address
    print port

    
    """
     * options:
     *       -a, --address <network element address or FQDN>
     *       -u, --username <name of user> must be privelege level 15
     *       -p, --password <password of user>
    """     
    for option, arg in opts:
        if option == '-h':
            logger.info(get_usage())
            sys.exit()
        elif option in ("-u", "--username"):
            global username 
            username = arg
        elif option in ("-p", "--password"):
            global password 
            password = arg

    if(element_address==None):
        logger.error(get_usage())
        return False
    
    return True
    
def get_usage():
        return " Usage: [-u <username> -p <password>] host [port]"

if __name__=='__main__':
   logger = logging.getLogger('telnet')
   logger.setLevel(logging.INFO)
   if not parse_command_line(sys.argv):
      logger.error("Error in parsing arguments")
      sys.exit(1)
   
   print element_address, password, port   
   rtr = rtrlib.Rtr(element_address, password, port)
   rtr.open()
   str = rtr.show_version()
   print str
   str = rtr.show_running()
   print str
   rtr.close()
   print "*********Finished"
   sys.exit(0)
   rtr.write_config("logging buffered 1000000\n")
   str = rtr.show_running(" | i logging buffered")
   print str
   rtr.write_config("default logging buffered\n")
   str = rtr.show_running(" | i logging buffered")
   print str
   print "*********Finished"
