#! /usr/bin/env python

# *
# * Copyright (c) 2015 Cisco Systems, Inc. and others.  All rights reserved.
# *
# * This program and the accompanying materials are made available under the
# * terms of the Eclipse Public License v1.0 which accompanies this
# * distribution, and is available at http://www.eclipse.org/legal/epl-v10.html
# *

# * Given a *.virl file print node names and addresses.  Assumes virl flat
# * network configuration with static_ip for every node.

# * python rtr_addr.py -f IWAN-SRBR-EIGRP.virl

import logging
import getopt
import sys
import os
import subprocess
import rtrlib
from xml.dom import minidom

logging.basicConfig(level=logging.WARNING)

fn_virl = None
element_address = None
router = None
username = None
password = "cisco"

def parse_command_line(args):
    """
    Parse the command line options. If the required argument "-a" for element address or FQDN is not provided,
    this method displays the proper usage information and calls sys.exit(1).

    @param args  The args string passed into the main(...) method.
    
    @return true if parsing the command line succeeds, false otherwise.
    """
    try:
        opts, args = getopt.getopt(args[1:],"hf:r:p:",["file=","router==", "password="])
    except getopt.GetoptError as err:
        print str(err)
        logger.info(get_usage())
        sys.exit(2)
    
    """
     * options:
     *       -r, --router <name of router> must be privelege level 15
     *       -p, --password <password of user>
    """     
    for option, arg in opts:
        if option == '-h':
            logger.info(get_usage())
            sys.exit()
        elif option in ("-f", "--file"):
            global fn_virl
            fn_virl = arg
        elif option in ("-r", "--router"):
            global router 
            router = arg
        elif option in ("-p", "--password"):
            global password 
            password = arg

    if(fn_virl==None):
        logger.error(get_usage())
        return False
    
    return True
    
def get_usage():
        return " Usage: -f <virl filename *.virl> [-r <router name>]"

if __name__=='__main__':
   logger = logging.getLogger('telnet')
   logger.setLevel(logging.INFO)
   if not parse_command_line(sys.argv):
      logger.error("Error in parsing arguments")
      sys.exit(1)
   
#   print "this is the virl filename %s" % fn_virl

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
           
#           print router.__repr__()

               if (router == 'all'):
                   os.system("xterm -title {} -e telnet {} &".format(nodeName,
                                                                     d))
               elif (router == nodeName):
                   os.system("xterm -title {} -e telnet {} &".format(nodeName,
                                                                     d))
                   break;
               else:
                   invalid = router
                   break;
#   if (invalid != None):
#       logger.error("Invalide node name {}".format(invalid))
           

   print "*********Finished"
