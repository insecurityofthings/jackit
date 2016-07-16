# JackIt

## What

This is a partial implementation of Bastille's MouseJack exploit. See [mousejack.com](https://www.mousejack.com) for more details. Full credit goes to [Bastille's team](https://www.bastille.net/meet-mousejack-researchers) for discovering this issue and writing the libraries to work with the CrazyRadio PA dongle. Also, thanks to Samy Kamkar for [KeySweeper](http://samy.pl/keysweeper/), to Thorsten Schroeder and Max Moser for their work on [KeyKeriki](http://www.remote-exploit.org/articles/keykeriki_v2_0__8211_2_4ghz/) and to [Travis Goodspeed](http://travisgoodspeed.blogspot.ca/2011/02/promiscuity-is-nrf24l01s-duty.html). We stand on the shoulders of giants.

To our knowledge, it should work on all Microsoft and Logitech devices based on the NRF24L01-series RFICs.

We tested with the following hardware:
- Microsoft Wireless Mouse 1000
- [Microsoft All-In-One Media Keyboard](https://www.microsoft.com/accessories/en-ca/products/keyboards/all-in-one-media-keyboard/n9z-00002)
- [Microsoft Sculpt Ergonomic Mouse](https://www.microsoft.com/accessories/en-ca/products/mice/sculpt-ergonomic-mouse/l6v-00002)
- [Logitech Marathon M705 Mouse](http://www.logitech.com/en-us/product/marathon-mouse-m705)

Tested on Windows 8.1, Windows 10 and macOS 10.11. Let us know if it works or doesn't work on your device. If you can see the frames with the CrazyRadio PA dongle, chances are we can build support for it.

## Why

We work in the security industry and often it is necessary to demonstrate risk in order to create action. Unfortunately, these kinds of issues don't show up on Nessus scans, so we wrote an exploit. Please use this code responsibly.

## How

To use these scripts, you will need a [CrazyRadio PA adapter from Seed Studio](https://www.seeedstudio.com/item_detail.html?p_id=2104). You will also need to flash the firmware of the adapter using [Bastille's MouseJack research tools](https://github.com/RFStorm/mousejack). Please follow their instructions for updating the firmware before continuing.

After installing the firmware, you can install the Python 2 requirements via:

```
sudo pip install -r requirements.txt
```

Once your CrazyRadio PA is ready, you can launch JackIt via:

```
sudo ./jackit.py
```

Let the script run and detect the nearby devices, then press Ctrl-C to start your attack. The workflow is similar to [Wifite](https://github.com/derv82/wifite). By default, it will only monitor for devices. If you would like to inject, specify a Duckyscript payload file using --script. The payload should be in plain text, not compiled using the Duckyscript encoder.

If you have no idea what Duckyscript is, see the [Hak5 USB Rubber Ducky Wiki](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Duckyscript).

For practical usage instructions and gotchas, check on [the Wiki page](https://github.com/phikshun/jackit/wiki).

## Who

This implementation was written by phikshun and infamy. Our code is all BSD license. All the files in the lib directory were written by Bastille's research team and are GPLv3 license.
