
import platform
import serial
import binascii
from time import sleep, time
from threading import *


DEBUG_MSG = False

#prints debug messages (easily disabled)
def prntDbg(*argv):
    if DEBUG_MSG:
        print("[rfidthrad] ", end="")
        for arg in argv:
            print(arg, end=" ")
        print()

#auxiliary "constants"
START, DETECT, READ, WRITE, TAG = range(0, 5)

######################################################################
## Thread para comunicacao serial com o Arduino (via porta serial USB)
## para enviar informacoes de leitor RFID conectado ao Arduino
## O Arduino deve estar rodando o driver adequado implementado no VS Code

class RfidSerialThread(Thread):
    __INSTACE = None
    
    def getInstance(port_name = None, auto_ping_tag = True):
        if (RfidSerialThread.__INSTANCE is None):
            if port_name is None:
                port_name = "COM5" if (platform.system() == "Windows") else "/dev/ttyUSB0"
            RfidSerialThread.__INSTANCE = RfidSerialThread(port_name, auto_ping_tag)
            print("Starting RFID reader...")
            RfidSerialThread.__INSTANCE.start()
            sleep(4)  # time for the RFID reader to start up

        return RfidSerialThread.__INSTANCE
        

    def __init__(self, portName, auto_ping_tag = True):
        Thread.__init__(self, name="RFID_Thread")
        self.running = False
        self.serialComm = serial.Serial(portName, 38400, timeout=0.002)

        self._lock = Lock()
        self._ping_tag = auto_ping_tag

        #for the 5 types of message treated
        self.responses = [(0,None) for i in range(0,5)]   # pairs (timestamp in sec, message)
        self.responses[START] = (time(), None)

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        print("[rfidthrd] Starting up...")

        prntDbg("Starting...")
        self.serialComm.flushInput()  # newer versions: reset_input_buffer()
        sleep(2.0)

        with self._lock:
            self.serialComm.write(b"(t)")  # test
            sleep(1.0)
            self.serialComm.write(b"(s)")  # start

        sleep(2.0)
        print("[rfidthrd] Running.")

        partialMsg = b""

        while self.running:
            with self._lock:
                if self._ping_tag:
                    if (time() - self.responses[TAG][0]) > 15:  # more than 15 secs
                        prntDbg("Pinging tag...")
                        self.serialComm.write(b"(d)")
                        self.responses[TAG] = (time(), None)

                msg = self.serialComm.readline()
                if (msg is None or len(msg) == 0):
                    continue

                endMsgIndex = msg.rfind(b")")  # end-of-message delimiter is ")"
                if endMsgIndex == -1:
                    partialMsg += msg
                    continue

                prntDbg("Received full:", partialMsg + msg)
                msg = partialMsg + msg[0:endMsgIndex] # terminator ) discarded
                partialMsg = b""

                responseType, responseInfo = msg.split(b" ", 1)

                if responseType == b"(tag":
                    if responseInfo == b"not detected":
                        prntDbg("No tag!")
                        self.responses[TAG] = (time(), None)
                    else:
                        self.responses[TAG] = (time(), responseInfo)
                elif responseType == b"(r":
                    self.responses[READ] = (time(), responseInfo)
                elif responseType == b"(w":
                    self.responses[WRITE] = (time(), responseInfo)
                elif responseType == b"(s":
                    self.responses[START] = (time(), responseInfo)
                elif responseType == b"(t":
                    print("[rfidthrd]", responseInfo[responseInfo.find(b",")+2:].decode("ascii"))
                else:
                    print("[rfidthrd] Invalid response:", msg[1:])
        #end while

        with self._lock:
            self.serialComm.write("(x)".encode("ascii"))
            sleep(2)
            self.serialComm.close()

        print("[rfidthrd] Stopped")
    #end run()

    def getCurrentTagId(self):
        with self._lock:
            return self.responses[TAG][1]

    def sendReadRequest(self, block_addr, magic_num_str):
        msg = "(r " + str(block_addr) + " " + magic_num_str + ")"
        msg = msg.encode("ascii")
        prntDbg("Sending:", msg)

        with self._lock:
            self.serialComm.write(msg)
            self.responses[READ] = (0, None)

    def sendWriteRequest(self, block_addr, magic_num_str, content):
        msg = "(w " + str(block_addr)
        msg += " " + magic_num_str
        if isinstance(content, str):
            content = content.encode("ascii")
        #content_hex = content.hex()  # python 3.6 or higher
        content_hex = binascii.hexlify(content).decode("ascii")
        msg += " " + str(len(content_hex) // 2)
        msg += " " + content_hex + ")"
        msg = msg.encode("ascii")
        prntDbg("Sending:", msg)

        with self._lock:
            self.serialComm.write(msg)
            self.responses[WRITE] = (0, None)

    def getReadResponse(self):
        """Returns None (no answer) or a pair: (Success?, Error message / Data)
        """
        with self._lock:
            if (self.responses[READ][0] == 0): #no answer
                return None
            response = self.responses[READ][1]

        if response.startswith(b"Error"):
            self.responses[READ] = (0, None)
            return (False, response)
        else:
            datasize, data = response.split(b" ", 1)
            datasize = int(datasize)
            data = bytes.fromhex(data.decode("ascii"))
            prntDbg("Data sizes:", datasize, len(data))
            self.responses[READ] = (0, None)
            return (True, data)

    def getWriteResponse(self):
        """Returns None (no answer) or a pair: (Success?, Error message)
        """
        with self._lock:
            if (self.responses[WRITE][0] == 0): #no answer
                return None
            response = self.responses[WRITE][1]

        if response.startswith(b"OK") or response.startswith(b"Ok"):
            self.responses[WRITE] = (0, None)
            return (True, None)
        else:
            self.responses[WRITE] = (0, None)
            return (False, response)

