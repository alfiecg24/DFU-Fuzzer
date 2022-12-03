# DFU Fuzzer

This is a simple Python program I wrote to fuzz the DFU mode in the SecureROM of iOS devices.
Yes, it's a mess, but it does what it needs to do. It sends random control requests to DFU.

## Usage

Simply run `python3 Fuzzer.py` to start the program. When the program starts, you can choose which components of the control requests to fuzz, along with choosing the number of iterations - and having the option to change the USB timeout. If you don't fuzz wLength OR data, it will select either one randomly each time.

All results are written to a log file in the Logs/ directory.

If you get any interesting results, you can "replay" a log file, and the program will parse the log and send exactly the same set of control requests.

Enjoy!


## Credits

* axi0mX for ipwndfu - I got `dfu.py` from there
* Me - follow my Twitter at @alfiehacks, I sometimes tweet about my projects ;)
