#! /usr/bin/env python

# *
# * Copyright (c) 2015 Cisco Systems, Inc. and others.  All rights reserved.
# *
# * This program and the accompanying materials are made available under the
# * terms of the Eclipse Public License v1.0 which accompanies this
# * distribution, and is available at http://www.eclipse.org/legal/epl-v10.html
# *

import telnetlib
import StringIO
import sys
import time
import logging

class Rtr:

   tn = None

   def __init__(self, addr, password, port):
      self.logger = logging.getLogger('Router ' + addr)
      self.logger.setLevel(logging.DEBUG)
      self.mgmt_addr = addr
      self.password = password
      self. port = port

   def open(self):
      if self.tn is None:
         if (self.port > 1):
            #  port exists, this is console access
            print "console access"
            try:
               self.tn = telnetlib.Telnet(self.mgmt_addr, self.port, 5)
            except:
               self.logger.error("telnet console failed\n")
               self.tn = None;
               sys.exit(1)
         else:
            try:
               self.tn = telnetlib.Telnet(self.mgmt_addr)
            except:
               self.logger.error("telnet vty failed\n")
               self.tn = None;
               sys.exit(1)
      else:
         self.logger.debug("Session exists: addr " + self.mgmt_addr)
         return self.tn

   def close(self):
      if self.tn is not None:
         self.tn.close()
         self.tn = None

   def write(self, str):
      if self.tn is not None:        
         print "Writing " + str
         self.tn.write(str)
      else:
         self.logger.error("No session")
      
   def enable_mode(self):
      if True:
         self.write("\r\n")
#         tn.read_until(">",5)         
#         tn.write("enable\n")
#         tn.read_until("Password: ",5)
#         tn.write(self.password + "\n")
         print "waiting for #"
         try:
            self.tn.read_until("#", 5)
         except EOFerror as e:
            print "timed out"
            sys.exit(1)
            return None
         self.tn.write("terminal length 0\r\n")
         str = self.tn.read_until("#", 5)
         print "enable mode read until " + str
         return self.tn
      else:
         print "vty access"
         # port does not exist, this is vty access
         tn = telnetlib.Telnet(self.mgmt_addr)         
         tn.read_until("Password: ")
         tn.write(self.password + "\n")
         tn.read_until(">")
         tn.write("enable\n")
         tn.read_until("Password: ")
         tn.write(self.password + "\n")
         tn.read_until("#")
         tn.write("terminal length 0\n")
         tn.read_until("#")
         return tn
      
      return None

   def show_version(self,pipe=""):
      sess = self.enable_mode()
      print "get show version"
      sess.write("show version" + pipe +"\r\n")
#      sess.write("show version" + pipe +"\n")
#      sess.read_until("#")      
      str = sess.read_eager()
      return str

   def show_running(self, pipe=""):
      sess = self.enable_mode()
      self.write("show running" + pipe + "\n")
      str = sess.read_until("#")
      return str      

#  configStr must have \n for each line of config
   def write_config(self, config_str):
      sess = self.enable_mode()
      sess.write("config terminal\n")
      sess.read_until("#")
      buf = StringIO.StringIO(config_str)
      
      line = buf.readline()
      while (line != ''):
#         print line
         sess.write(line)
         line = buf.readline()

      sess.write("end\n")
      sess.read_until("#")
      sess.close()

   def __show_health_dmvpn(self):
      sess = self.enable_mode()
      sess.write("show dmvpn\n") 
      str = sess.read_until("#")
      sess.close()
      return str

   def __show_health_eigrp(self):
      sess = self.enable_mode()
      sess.write("show eigrp address-family ipv4 neighbors\n") 
      str = sess.read_until("#")
      sess.close()
      return str

   def __show_health_saf(self):
      sess = self.enable_mode()
      sess.write("show eigrp service-family ipv4 neighbors\n") 
      str = sess.read_until("#")
      sess.close()
      return str

   def __show_health_bgp(self):
      sess = self.enable_mode()
      sess.write("show ip bgp neighbors\n") 
      str = sess.read_until("#")
      sess.close()
      return str

   def __show_health_pfr(self):      
      sess = self.enable_mode()
      sess.write("show domain IWAN master status\n") 
      str = sess.read_until("#")
      sess.close()
      return str

   def __show_health_qos(self):
      sess = self.enable_mode()
      sess.write("show policy-map interface\n") 
      str = sess.read_until("#")
      sess.close()
      return str

   def __show_health_perfmon(self):
      str = "PERFMON not UP\n"
      return str

   def show_health(self, tech_type):
      str = "Sick"
      if (tech_type == "IWAN"):
         str = self.__show_health_pfr()
         str = str + self.__show_health_dmvpn()
         str = str + self.__show_health_eigrp()
         str = str + self.__show_health_bgp()
         str = str + self.__show_health_pfr()
         str = str + self.__show_health_qos()
         str = str + self.__show_health_perfmon()
      elif (tech_type == "DMVPN"):
         str = self.__show_health_dmvpn();
      elif (tech_type == "EIGRP"):
         str = self.__show_health_eigrp();
      elif (tech_type == "BGP"):
         str = self.__show_health_bgp();
      elif (tech_type == "PFR"):
         str = self.__show_health_pfr();
      elif (tech_type == "QOS"):
         str = self.__show_health_qos();
      elif (tech_type == "PERFMON"):
         str = self.__show_health_perfmon();
      else:
         str = "show health does NOT support %s\n" % (tech_type)
         str = str + 'Try IWAN, DMVPN, EIGRP, BGP, PFR, QOS, or PERFMON'

      return str
