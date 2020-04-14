# JackIt

_Do you like JackIt but don't want to carry around a laptop? Check [this](https://github.com/phikshun/uC_mousejack) out._

## What

This is a partial implementation of Bastille's MouseJack exploit. See [mousejack.com](https://www.mousejack.com) for more details. Full credit goes to [Bastille's team](https://www.bastille.net/meet-mousejack-researchers) for discovering this issue and writing the libraries to work with the CrazyRadio PA dongle. Also, thanks to Samy Kamkar for [KeySweeper](http://samy.pl/keysweeper/), to Thorsten Schroeder and Max Moser for their work on [KeyKeriki](http://www.remote-exploit.org/articles/keykeriki_v2_0__8211_2_4ghz/) and to [Travis Goodspeed](http://travisgoodspeed.blogspot.ca/2011/02/promiscuity-is-nrf24l01s-duty.html). We stand on the shoulders of giants.

We have successfully tested with the following hardware:
- Microsoft Wireless Keyboard 800 (including keystroke logging)
- Microsoft Wireless Mouse 1000
- [Microsoft Wireless Mobile Mouse 3500](https://www.microsoft.com/accessories/fr-fr/products/mice/wireless-mobile-mouse-3500/gmf-00277?part=GMF-00277)
- [Microsoft All-In-One Media Keyboard](https://www.microsoft.com/accessories/en-ca/products/keyboards/all-in-one-media-keyboard/n9z-00002)
- [Microsoft Sculpt Ergonomic Mouse](https://www.microsoft.com/accessories/en-ca/products/mice/sculpt-ergonomic-mouse/l6v-00002)
- [Logitech Wireless Touch Keyboard K400r](http://www.logitech.com/en-ca/product/wireless-touch-keyboard-k400r)
- [Logitech Marathon M705 Mouse](http://www.logitech.com/en-us/product/marathon-mouse-m705)
- [Logitech Wave M510 Mouse](http://www.logitech.com/en-ca/product/wireless-mouse-m510)
- [Logitech Wireless Gaming Mouse G700s](http://gaming.logitech.com/en-ca/product/g700s-rechargeable-wireless-gaming-mouse)
- [Logitech Wireless M325 Mouse](http://www.logitech.com/en-us/product/wireless-mouse-m325)
- [Logitech K830 Illuminated Wireless Keyboard](https://www.logitech.com/en-au/product/living-room-keyboard-k830)
- [Logitech K750 Wireless Keyboard](https://www.logitech.com/en-ca/product/k750-keyboard)
- [Logitech K320 Wireless Keyboard](http://support.logitech.com/en_us/product/wireless-keyboard-k320)
- [Logitech K270 Wireless Keyboard](https://www.logitech.com/en-roeu/product/wireless-keyboard-k270)
- [Dell KM636 Wireless Mouse and Keyboard](http://www.dell.com/en-us/shop/dell-wireless-keyboard-and-mouse-km636-black/apd/580-adty/pc-accessories)
- [AmazonBasics MG-0975 Wireless Mouse](https://www.amazon.com/AmazonBasics-Wireless-Mouse-Receiver-MGR0975/dp/B005EJH6Z4)

Known to not work with:
- Logitech M185 and M187 mice (red unifying dongle C-U0010)
- All older 27MHz devices, such as:
  - Microsoft Wireless Optical Mouse 2.0
  - Microsoft Wireless Notebook Optical Mouse 3000
- Dell KM632 (on the roadmap)
- HP wireless devices (on the roadmap)
- Lenovo wireless devices (on the roadmap)

Tested on Windows 7/8.1/10 and macOS 10.11/10.12. Not tested against Linux. Let us know if it works or doesn't work on your device.

Note: JackIt may not work if you have applied the [Logitech firmware update](http://forums.logitech.com/t5/Mice-and-Pointing-Devices/Logitech-Response-to-Unifying-Receiver-Research-Findings/td-p/1493878) or [KB3152550](https://support.microsoft.com/en-us/kb/3152550).

## Why

We work in the security industry and often it is necessary to demonstrate risk in order to create action. Unfortunately, these kinds of issues don't show up on Nessus scans, so we wrote an exploit. Please use this code responsibly.

## How

To use these scripts, you will need a [CrazyRadio PA adapter from Seeed Studio](https://www.seeedstudio.com/item_detail.html?p_id=2104). You will also need to flash the firmware of the adapter using [Bastille's MouseJack research tools](https://github.com/RFStorm/mousejack). Please follow their instructions for updating the firmware before continuing.

After installing the firmware, you can install JackIt via:

```
git clone https://github.com/insecurityofthings/jackit.git
cd jackit
pip install -e .
```

Once your CrazyRadio PA is ready, you can launch JackIt via:

```
sudo jackit
```

Let the script run and detect the nearby devices, then press Ctrl-C to start your attack. The workflow is similar to [Wifite](https://github.com/derv82/wifite). By default, it will only monitor for devices. If you would like to inject, specify a Duckyscript payload file using --script. The payload should be in plain text, not compiled using the Duckyscript encoder.

If you have no idea what Duckyscript is, see the [Hak5 USB Rubber Ducky Wiki](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Duckyscript).

For practical usage instructions and gotchas, check on [the Wiki page](https://github.com/phikshun/jackit/wiki).

## Who

This implementation was written by phikshun and infamy. Our code is all BSD license. All the files in the lib directory were written by Bastille's research team and are GPLv3 license.
