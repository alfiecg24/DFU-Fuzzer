A bmRequestType of 0x41 succeeds in a control transfer

wIndex MUST be 0 for transfers to succeed by the looks of it


Known bmRequestTypes to work with bRequest 1, wValue 0 and wIndex 0:
* 0xBE41
* 0xDE21
* 0x21
* 0x41
* 0x8821
* 0x12441
* 0x16E41
* 0x5C21
* 0xC241
* 0x141
* 0xE441
* 0x12921
* 0xD821
* 0xA241
* 0x11A21
* 0x16421
* 0x6521
* 0x6141
* 0x2C41
* 0x2921
* 0x18141
* 0x4541
* 0xE441

Remember that the bmRequestTypes in log.txt are in decimal, but the above have been converted to hexadecimal