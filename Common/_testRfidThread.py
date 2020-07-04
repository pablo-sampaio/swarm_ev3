#!/usr/bin/env python3

from RfidReader import *
from time import *
import platform

BLOCK_ADDR = 16
SERIAL_PORT = "COM5" if (platform.system() == "Windows") else "/dev/ttyUSB0"

threadRfid = RfidSerialThread(SERIAL_PORT)
threadRfid.start()
sleep(6)

print("WAITING FOR A TAG:")
print(" - tag:", threadRfid.getCurrentTagId())

while (threadRfid.getCurrentTagId() is None):
    sleep(1)
    print(" - tag:", threadRfid.getCurrentTagId())

print("SENDING READ CMD")
threadRfid.sendReadRequest(BLOCK_ADDR, "12345678")

resp = threadRfid.getReadResponse()
while (resp is None):
    print(" - nothing received")
    resp = threadRfid.getReadResponse()
    sleep(0.001)

if (resp[0]):
    print("RECEIVED DATA:", resp[1])

else:
    print("PROBLEM READING:", resp[1])
    sleep(2)

    print("SENDING WRITE CMD")
    threadRfid.sendWriteRequest(BLOCK_ADDR, "12345678", "Testando!")

    resp = threadRfid.getWriteResponse()
    while (resp is None):
        print(" - nothing received")
        resp = threadRfid.getWriteResponse()
        sleep(0.001)

    if (resp[0]):
        print("WRITE OK")
    else:
        print("PROBLEM WRITING:", resp[1])

print("ASKING TO STOP")
threadRfid.stop()
