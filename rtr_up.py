#! /usr/bin/env python

# *
# * Copyright (c) 2015 Cisco Systems, Inc. and others.  All rights reserved.
# *
# * This program and the accompanying materials are made available under the
# * terms of the Eclipse Public License v1.0 which accompanies this
# * distribution, and is available at http://www.eclipse.org/legal/epl-v10.html
# *

# * Given a *.virl file verify that all nodes are reachable. Assumes virl flat
# * network configuration with static_ip for every node. 

# * python rtr_up.py -f IWAN-SRBR-EIGRP.virl

import logging
import getopt
import sys
import subprocess
import rtrlib
from xml.dom import minidom

logging.basicConfig(level=logging.WARNING)

fn_virl = None
element_address = None
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
        opts, args = getopt.getopt(args[1:],"hf:u:p:n:",["file=","username=", "password=", "netapp=", "transport=", "rootcert=", "clientcert=", "key="])
    except getopt.GetoptError as err:
        print str(err)
        logger.info(get_usage())
        sys.exit(2)
    
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
        elif option in ("-f", "--file"):
            global fn_virl
            fn_virl = arg
        elif option in ("-u", "--username"):
            global username 
            username = arg
        elif option in ("-p", "--password"):
            global password 
            password = arg

    if(fn_virl==None):
        logger.error(get_usage())
        return False
    
    return True
    
def get_usage():
        return " Usage: -f <virl filename *.virl> [-u <username> -p <password>]"

if __name__=='__main__':
   logger = logging.getLogger('telnet')
   logger.setLevel(logging.INFO)
   if not parse_command_line(sys.argv):
      logger.error("Error in parsing arguments")
      sys.exit(1)
   
#   print "this is the virl filename %s" % fn_virl

   virldoc = minidom.parse(fn_virl)
   nodelist = virldoc.getElementsByTagName('node')
   print(len(nodelist))
   while True:
       fail_cnt = 0
       for n in nodelist:
           nodeName = n.attributes['name'].value
           print('\nNode name is {} \n'.format(nodeName))
           entries = n.getElementsByTagName('entry')
           for e in entries:
               k = e.attributes['key'].value
               t = e.attributes['type'].value
               d = "none"
               if (e.firstChild != None):
                   d = e.firstChild.data
                   
#           print('  entry is {} type {} data {}'.format(k, t, d))
                   
#           print e.firstChild.__repr__()
                   
#           print "  entry is ", k
               if (k == 'static_ip'):
                   res = subprocess.call(['ping', '-c', '1', d])
                   if res != 0:
                       print "\nNO RESPONSE FROM %s \n" % nodeName
                       fail_cnt = fail_cnt + 1
       
       if (fail_cnt == 0):
           break;
           

   print "*********Finished"
