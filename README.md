# DFU Fuzzer

This is a simple Python program I found to fuzz the DFU mode in the SecureROM of iOS devices. In it's current state, it will choose a random bmRequestType between 0 and 100,000 - but the script can easily be edited to change different parts of the USB request.

All results are written to log.txt, and I have put some of my findings inside Findings.md

Enjoy!