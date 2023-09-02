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
#kmtronic FTDI serial relay
ft232r = {
        'name': 'Kmtronic FT232R FTDI serial relay',
        'channel':
            [
                {'on': b'\xFF\x01\x01', 'off': b'\xFF\x01\x00'},
                {'on': b'\xFF\x02\x01', 'off': b'\xFF\x02\x00'},
                {'on': b'\xFF\x03\x01', 'off': b'\xFF\x03\x00'},
                {'on': b'\xFF\x04\x01', 'off': b'\xFF\x04\x00'}
            ]
    }

# http://www.icstation.com/icstation-micro-channel-relay-module-control-relay-module-icse012a-p-4012.html
# https://stackoverflow.com/questions/26913755/need-help-understading-sending-bytes-to-serial-port
# to turn on both channels at the same time: b'\xff' (binary 11111111)
# x03 turns on both as in binary it is 0011
# and x05 (0101) turns on ch1 and ch2 off with x06 (0110) turning on ch2 and ch1 off
# so it is just the rightmost bits in the binary number that matters
# as xf0 turns both off --> 11110000 in binary
pl2303 = {
        'name': 'PL2303 serial relay',
        'handshake': b'\x50',
        'activate': b'\x51',
        'reset': b'\x00',
        'channel':
            [
                {'on': b'\x01', 'off': b'\x00'},
                {'on': b'\x02', 'off': b'\x00'}
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

