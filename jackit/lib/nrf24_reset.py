# Workaround to fix problem where device time outs

from __future__ import print_function
import usb.core
import usb.util
try:
    from fcntl import ioctl
except ImportError:
    # Make sure this code does not break platforms without ioctl - if any...
    ioctl = lambda *args: None

# Thanks to https://github.com/Paufurtado/usbreset.py
USBDEVFS_RESET = ord('U') << (4 * 2) | 20


def reset_radio(index, idVendor=0x1915, idProduct=0x0102):
    device = list(usb.core.find(idVendor=idVendor, idProduct=idProduct, find_all=True))[index]
    bus = str(device.bus).zfill(3)
    addr = str(device.address).zfill(3)
    filename = "/dev/bus/usb/%s/%s" % (bus, addr)
    try:
        ioctl(open(filename, "w"), USBDEVFS_RESET, 0)
    except IOError:
        print("Unable to reset device %s" % filename)
