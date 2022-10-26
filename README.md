# DFU Fuzzer

This is a simple Python program I wrote to fuzz the DFU mode in the SecureROM of iOS devices.

## Usage

Simply run `python3 Fuzzer.py` to start the program. When the program starts, you can choose which components of the control requests to fuzz, along with choosing the number of iterations - and having the option to change the USB timeout.

All results are written to `log.txt` in the same directory.

Enjoy!


## Credits

axi0mX for ipwndfu - I got `dfu.py` from there
Me - follow my Twitter at @alfiehacks, I sometimes tweet about my projects
