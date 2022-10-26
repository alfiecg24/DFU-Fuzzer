#!/opt/homebrew/bin/python3

import usb, time, random, sys
import dfu

HOST2DEVICE = 0x21

DFU_DETACH = 0
DFU_DNLOAD = 1
DFU_UPLOAD = 2
DFU_GETSTATUS = 3
DFU_CLRSTATUS = 4
DFU_GETSTATE = 5
DFU_ABORT = 6

USB_TIMEOUT = 5

iterations = 10
allComponents = {1: "bmRequestType", 2: "bRequest", 3: "wValue", 4: "wIndex", 5: "data"}

def log(message):
    with open('log.txt', 'a') as f:
        f.write(f'\n{message}')
        f.close()

def controlTransfer(device, bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout):
    log(f'controlTransfer(bmRequestType: {bmRequestType}, bRequest: {bRequest}, wValue: {wValue}, wIndex: {wIndex}, data_or_wLength: {data_or_wLength}, timeout: {timeout})')
    try:
        device.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout)
        log('Success')
        return 0
    except usb.core.USBError as e:
        log("Control transfer ERROR: %d, %d, %r" % (bmRequestType, bRequest, e))
        return 1


def generateRequestType():
    return random.randint(0, 255)

def generateRequest():
    return random.randint(0, 6)

def generateIndex():
    return random.randint(0,5)

def generateValue():
    return random.randint(1, 4)

def generateData():
    num = random.randint(1, 1000)
    return random.randbytes(num)


def main(components, wLength=None):

    assert type(components) == list, "Components must be a list"
    assert len(components) > 0, "No components specified"

    device = dfu.acquire_device()
    print("\nGot device: %s" % device.serial_number)
    log(f"Device: {device.serial_number}\n\n")

    time.sleep(0.5)

    controlTransfer(device, HOST2DEVICE, DFU_DNLOAD, 0, 0, 0x40, 5)
    
    time.sleep(2)

    count = 1
    errorCount = 0

    for _ in range(iterations):
        requestType = generateRequestType() if 1 in components else 0x21
        request = generateRequest() if 2 in components else DFU_DNLOAD
        value = generateValue() if 3 in components else 0
        index = generateIndex() if 4 in components else 0
        dataOrwLength = generateData() if wLength == None else wLength

        log(f"\nRequest {count}")
        ret = controlTransfer(device, requestType, request, value, index, dataOrwLength, USB_TIMEOUT)
        if ret == 1:
            errorCount += 1
        time.sleep(0.5)
        count += 1
        requestType += 1

    print(f"\nDone fuzzing with {errorCount} errors")

    dfu.usb_reset(device)
    dfu.release_device(device)


if __name__ == '__main__':
    # Begin log
    with open('log.txt', 'w') as f:
        f.write(time.strftime("LOG START: %Y-%m-%d %H:%M:%S", time.localtime()))
        f.close()
    
    # Title screen and component picker
    print("\n\n")
    print(" =====================================")
    print("(                                     )")
    print("(       DFU Fuzzer by alfiecg24       )")
    print("(                                     )")
    print(" =====================================")
    print("\n\n")
    iterations = int(input("Enter the number of requests to be sent: "))
    log(f"\nNumber of requests to be made: {iterations}")
    print("\n")
    print("Fuzzing options:")
    print("1. bmRequestType")
    print("2. bRequest")
    print("3. wValue")
    print("4. wIndex")
    print("5. data")
    opts = input("\nEnter the components to fuzz (e.g. 145): ")
    componentsToFuzz = []
    wLength = None
    if "1" in opts:
        componentsToFuzz.append(1)
    if "2" in opts:
        componentsToFuzz.append(2)
    if "3" in opts:
        componentsToFuzz.append(3)
    if "4" in opts:
        componentsToFuzz.append(4)
    if "5" in opts:
        componentsToFuzz.append(5)
    if "5" not in opts:
        wLength = int(input("Please specify the wLength in decimal: "))

    # Make sure we have components to fuzz
    assert len(componentsToFuzz) > 0, "No components specified"
    print("\nFuzzing:")
    log("\nComponents being fuzzed:")
    for i in componentsToFuzz:
        print(f"{allComponents[i]}")
        log(f"{allComponents[i]}")
    log("\n")

    timeout = input("\n\nIf you would like to specify USB timeout, do it here. Otherwise, press enter to leave at 5: ")
    if timeout != "":
        try:
            USB_TIMEOUT = int(timeout)
            log(f"User specified USB timeout: {USB_TIMEOUT}")
        except ValueError:
            print("Invalid timeout entered, using default of 5")

    input("\nPress enter to start...")
    if wLength == None:
        main(componentsToFuzz)
    else:
        main(componentsToFuzz, wLength)
    