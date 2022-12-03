# Same as normal fuzzer, but program does not exit on device disconnect


import usb, time, random, sys
import dfu
from RepeatFromLog import ParseCrashLog, ControlTransfer

HOST2DEVICE = 0x21

DFU_DETACH = 0
DFU_DNLOAD = 1
DFU_UPLOAD = 2
DFU_GETSTATUS = 3
DFU_CLRSTATUS = 4
DFU_GETSTATE = 5
DFU_ABORT = 6

USB_TIMEOUT = 5

IOErrorCount = 0
DeviceHasDisconnected = False

CURRENT = time.strftime("%m-%d-%Y-%H:%M:%S")

iterations = 10
allComponents = {1: "bmRequestType", 2: "bRequest", 3: "wValue", 4: "wIndex", 5: "data", 6: "wLength"}

successes = []

def log(message):
    global CURRENT
    # Open filename with now as the name
    with open(f'Logs/{CURRENT}-log.txt', 'a') as f:
        f.write(f'\n{message}')
        f.close()

def repeatLog(message):
    with open('repeatLog.txt', 'a') as f:
        f.write(f'\n{message}')
        f.close()

def controlTransferNoLog(device, bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout):
    try:
        device.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout)
        return 0
    except usb.core.USBError as e:
        if "No such device" in str(e):
            print("Device disconnected, stopping fuzzing")
            exit(1)
        if 'Input/Output' in str(e):
            global IOErrorCount
            IOErrorCount += 1
        return 1

def controlTransfer(device, bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout):
    if type(data_or_wLength) != int:
        log(f'controlTransfer(bmRequestType: {bmRequestType}, bRequest: {bRequest}, wValue: {wValue}, wIndex: {wIndex}, data_or_wLength: {data_or_wLength}, lengthOfData: {len(data_or_wLength)}, timeout: {timeout})')
    else:
        log(f'controlTransfer(bmRequestType: {bmRequestType}, bRequest: {bRequest}, wValue: {wValue}, wIndex: {wIndex}, data_or_wLength: {data_or_wLength}, timeout: {timeout})')
    try:
        device.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout)
        global successes
        if type(data_or_wLength) != int:
            successes.append(f"bmRequestType: {bmRequestType}, bRequest: {bRequest}, wValue: {wValue}, wIndex: {wIndex}, data: {data_or_wLength}")
        else:
            successes.append(f"bmRequestType: {bmRequestType}, bRequest: {bRequest}, wValue: {wValue}, wIndex: {wIndex}, wLength: {data_or_wLength}")
        log('Control transfer success')
        return 0
    except usb.core.USBError as e:
        log("Control transfer ERROR: %d, %d, %r" % (bmRequestType, bRequest, e))
        if "No such device" in str(e):
            log("Device disconnected")
            global DeviceHasDisconnected
            DeviceHasDisconnected = True
        if 'Input/Output' in str(e):
            global IOErrorCount
            IOErrorCount += 1
        return 1

def repeatControlTransfer(device, bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout):
    if type(data_or_wLength) != int:
        repeatLog(f'controlTransfer(bmRequestType: {bmRequestType}, bRequest: {bRequest}, wValue: {wValue}, wIndex: {wIndex}, data_or_wLength: {data_or_wLength}, lengthOfData: {len(data_or_wLength)}, timeout: {timeout})')
    else:
        repeatLog(f'controlTransfer(bmRequestType: {bmRequestType}, bRequest: {bRequest}, wValue: {wValue}, wIndex: {wIndex}, data_or_wLength: {data_or_wLength}, timeout: {timeout})')
    try:
        device.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout)
        global successes
        if type(data_or_wLength) != int:
            successes.append(f"bmRequestType: {bmRequestType}, bRequest: {bRequest}, wValue: {wValue}, wIndex: {wIndex}, data: {data_or_wLength}")
        else:
            successes.append(f"bmRequestType: {bmRequestType}, bRequest: {bRequest}, wValue: {wValue}, wIndex: {wIndex}, wLength: {data_or_wLength}")
        repeatLog('Control transfer success')
        return 0
    except usb.core.USBError as e:
        repeatLog("Control transfer ERROR: %d, %d, %r" % (bmRequestType, bRequest, e))
        if "No such device" in str(e):
            repeatLog("Device disconnected, possible a reboot?")
            global DeviceHasDisconnected
            DeviceHasDisconnected = True
        if 'Input/Output' in str(e):
            global IOErrorCount
            IOErrorCount += 1
        return 1


def generateRequestType():
    return random.randint(0, 255)

def generateRequest():
    return random.randint(0, 6)

def generateIndex():
    return random.randint(0,5)

def generateValue():
    return random.randint(1, 4)

def generateWLength():
    return random.randint(1, 1000)

def generateData():
    num = random.randint(1, 1000)
    return random.randbytes(num)

def main(components, wLength=None, data_or_wLength=None):

    start = time.time()

    assert type(components) == list, "Components must be a list"
    assert len(components) > 0, "No components specified"

    device = dfu.acquire_device()
    print("\nGot device: %s" % device.serial_number)
    log(f"Device: {device.serial_number}\n")

    time.sleep(0.5)

    controlTransferNoLog(device, HOST2DEVICE, DFU_DNLOAD, 0, 0, 0x40, 5)
    
    
    time.sleep(2)

    count = 1
    errorCount = 0
    global IOErrorCount
    global DeviceHasDisconnected

    for _ in range(iterations):
        requestType = generateRequestType() if 1 in components else 0x21
        request = generateRequest() if 2 in components else DFU_DNLOAD
        value = generateValue() if 3 in components else 0
        index = generateIndex() if 4 in components else 0
        dataOrwLength = 0

        # get random bool to determine if wLength or data is used
        if wLength == True or data_or_wLength == True:
            dataOrwLength = generateWLength() if 6 in components else generateData()
        else:
            usingData = random.choice([True, False])
            dataOrwLength = generateData() if usingData == True else generateWLength()

        if DeviceHasDisconnected == True:
            log("Device has disconnected, trying to reconnect")
            time.sleep(0.5)
            device = dfu.acquire_device()
            log("\nDevice: %s\n" % device.serial_number)
            DeviceHasDisconnected = False

        if IOErrorCount >= 5:
            log('Too many IOErrors, reconnecting')
            try:
                device.reset()
                time.sleep(0.5)
            except:
                print("Could not reset device, may have disconnected")
            dfu.release_device(device)
            device = dfu.acquire_device()
            log("\nDevice: %s\n" % device.serial_number)
            IOErrorCount = 0

        log(f"\nRequest {count}")
        ret = controlTransfer(device, requestType, request, value, index, dataOrwLength, USB_TIMEOUT)
        if ret == 1:
            errorCount += 1
        count += 1
        requestType += 1

    
    log("\n\nSuccessful transfers:\n")
    for success in successes:
        log(success)

    print(f"\nDone fuzzing with {errorCount} errors and {len(successes)} successes")
    print('Finished in %0.2f seconds' % (time.time() - start))

    dfu.usb_reset(device)
    dfu.release_device(device)


if __name__ == '__main__':
    
    # Title screen and component picker
    print("\n\n")
    print(" =====================================")
    print("(                                     )")
    print("(       DFU Fuzzer by alfiecg24       )")
    print("(                                     )")
    print(" =====================================")
    print("\n\n")
    # check if requests are from log
    usingLog = input("Use requests from log? (y/n): ")
    if usingLog == 'y':
        # Begin log
        with open('Logs/{CURRENT}-RepeatLog.txt', 'w+') as f:
            f.write(f"LOG START - {CURRENT}")
            f.close()
        repeatLog("Using requests from crash log")
        fileName = input("Enter full crash log file name (include Logs/ if needed): ")
        transfers = ParseCrashLog(fileName)
        repeatLog(f"Found {len(transfers)} requests in crash log")
        device = dfu.acquire_device()
        print("\nGot device: %s" % device.serial_number)
        repeatLog(f"Device: {device.serial_number}\n\n")
        time.sleep(0.5)
        repeatControlTransfer(device, HOST2DEVICE, DFU_DNLOAD, 0, 0, 0x40, 5)
        time.sleep(2)

        count = 1

        for transfer in transfers:
            assert type(transfer) == ControlTransfer, "Transfer must be a ControlTransfer object"
            if IOErrorCount >= 5:
                repeatLog('Too many IOErrors, reconnecting')
                device.reset()
                time.sleep(0.5)
                device = dfu.acquire_device()
                repeatLog("\nDevice: %s\n" % device.serial_number)
                IOErrorCount = 0
            repeatLog(f"\nRequest {count}")
            ret = repeatControlTransfer(device, transfer.bmRequestType, transfer.bRequest, transfer.wValue, transfer.wIndex, transfer.data_or_wLength, transfer.timeout)
            count += 1
    else:
        # Begin log
        with open(f'Logs/{CURRENT}-log.txt', 'w+') as f:
            f.write(f"LOG START - {CURRENT}")
            f.close()
        iterations = int(input("Enter the number of requests to be sent: "))
        log(f"\nNumber of requests to be made: {iterations}")
        print("\n")
        print("Fuzzing options:")
        print("1. bmRequestType")
        print("2. bRequest")
        print("3. wValue")
        print("4. wIndex")
        print("5. data")
        print("6. wLength")
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
        if "5" in opts and "6" in opts:
            print("Cannot fuzz both data and wLength")
            exit()
        if "5" in opts:
            componentsToFuzz.append(5)
        if "6" in opts:
            componentsToFuzz.append(6)

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
        try:
            main(componentsToFuzz)
        except KeyboardInterrupt:
            log("\n\nSuccessful transfers:\n")
            for success in successes:
                log(success)
        
