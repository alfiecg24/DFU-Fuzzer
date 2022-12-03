# Create ControlTransfer class
class ControlTransfer:
    def __init__(self, bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout):
        self.bmRequestType = bmRequestType
        self.bRequest = bRequest
        self.wValue = wValue
        self.wIndex = wIndex
        self.data_or_wLength = data_or_wLength
        self.timeout = timeout

def ParseCrashLog(fileName):
    # Open Crash.txt
    with open(fileName, 'r') as f:
        # Create a list to store all the control transfers
        controlTransfers = []
        # Read each line
        for line in f:
            # Create ControlRequest values in advance
            bmRequestType = 0
            bRequest = 0
            wValue = 0
            wIndex = 0
            data_or_wLength = 0
            timeout = 0
            # Check if line is a control transfer
            if line.startswith("controlTransfer"):
                # Split line into parts
                parts = line.split()
                # Get bmRequestType
                bmRequestType = parts[1].removesuffix(',')
                # Safely cast to int
                try:
                    bmRequestType = int(bmRequestType)
                except ValueError:
                    print("Invalid bmRequestType: " + bmRequestType)
                # Get bRequest
                bRequest = parts[3].removesuffix(',')
                # Safely cast to int
                try:
                    bRequest = int(bRequest)
                except ValueError:
                    print("Invalid bRequest: " + bRequest)
                # Get wValue
                wValue = parts[5].removesuffix(',')
                # Safely cast to int
                try:
                    wValue = int(wValue)
                except ValueError:
                    print("Invalid wValue: " + wValue)
                # Get wIndex
                wIndex = parts[7].removesuffix(',')
                # Safely cast to int
                try:
                    wIndex = int(wIndex)
                except ValueError:
                    print("Invalid wIndex: " + wIndex)
                # Get data_or_wLength - there may be spaces in the data
                next = parts[10]
                # Make sure parts[10] contains "timeout" or "lengthOfData"
                while "timeout" not in parts[10] and "lengthOfData" not in parts[10]:
                    # Append parts[10] to parts[9]
                    parts[9] += parts[10]
                    # Remove parts[10]
                    parts.pop(10)

                data_or_wLength = parts[9].removesuffix(',')
                # Check if parts[10] is "timeout"
                if parts[10] == "timeout:":
                    # Get timeout
                    timeout = parts[11].removesuffix(')')
                    # Safely cast to int
                    try:
                        timeout = int(timeout)
                    except ValueError:
                        print("Invalid timeout: " + timeout)
                else:
                    # timeout is parts[13]
                    timeout = parts[13].removesuffix(')')
                    # Safely cast to int
                    try:
                        timeout = int(timeout)
                    except ValueError:
                        print("Invalid timeout: " + timeout)
                # Create ControlTransfer object
                ct = ControlTransfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout)
                # Add ControlTransfer object to list
                controlTransfers.append(ct)
            
        return controlTransfers