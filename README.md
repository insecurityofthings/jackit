# JackIt

## What

This is an implementation of Bastille's MouseJack exploit. See [mousejack.com](https://www.mousejack.com) for more details. Full credit goes to Bastille for discovering this issue and writing the libraries to work with the CrazyRadio PA dongle.

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

Let the script run and detect the nearby devices, then press Ctrl-C to start your attack. The workflow is similar to Wifite. By default, it will only monitor for devices. If you would like to inject, specify a Duckyscript payload file using --attack. The payload should be in plain text, not compiled using the Duckyscript encoder.

If you have no idea what Duckyscript is, see the [Hak5 USB Rubber Ducky Wiki](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Duckyscript).

## Who

This implementation was written by phishun and infamy. Our attack script and keylogger fall under the BSD license. All the files in the lib directory were written by Bastille and are GPLv3 license.
