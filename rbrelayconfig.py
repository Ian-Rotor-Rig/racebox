ch340 = {
        'name': 'CH340 serial relay',
        'channel':
            [
                {'on': b'\xA0\x01\x01\xA2', 'off': b'\xA0\x01\x00\xA1'},
                {'on': b'\xA0\x02\x01\xA3', 'off': b'\xA0\x02\x00\xA2'},
                {'on': b'\xA0\x03\x01\xA4', 'off': b'\xA0\x03\x00\xA3'},
                {'on': b'\xA0\x04\x01\xA5', 'off': b'\xA0\x04\x00\xA4'}
            ]
    }

hid16c0 = {
        'name': 'Vendor 16c0 (www.dcttech.com)',
        'channel':
            [
                {'on': b'\xff\x01\x00\x00', 'off': b'\xfd\x01\x00\x00'},
                {'on': b'\xff\x02\x00\x00', 'off': b'\xfd\x02\x00\x00'},
            ],
        'vid': 0x16c0,
        'pid': 0x05df
    }
# https://slomkowski.eu/tutorials/eavesdropping-usb-and-writing-driver-in-python/

defaultDelay = 0.75 #seconds
