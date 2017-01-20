import serial

COMMAND_STATE_NOT_IN_QUEUE = 0
COMMAND_STATE_IN_QUEUE = 1
COMMAND_STATE_SENT = 2
COMMAND_STATE_REPLIED = 3

LASER_STATE_IDLE = 0
LASER_STATE_ERR = -1
LASER_STATE_WAITING_FOR_REPLY = 1

class LaserCommand():
    def __init__(self, command_str, callback):
        self._command = command_str
        self._callback = callback
        self._state = COMMAND_STATE_NOT_IN_QUEUE

    def getCommand(self):
        return self._command

    def setState(self, state):
        self._state = state

    def getState(self):
        return self._state

    def handleReply(self, reply):
        self._callback(reply)

class Laser():
    """A python abstraction to control a laser"""
    def __init__(self, serial_port, com_function=defaultComFunc, simulated=False):
        if type(serial_port) == str:
            print ("Adding from string is a feature for later.")
        else:
            self._serial = serial_port
        self._simulated = simulated #If true, this isn't like an actual laser.

        self._pilot_on = False
        self._power_on = False
        self._laser_on = False
        self._laser_power = 0

        self._state = LASER_STATE_IDLE       
        self._commandQueue = []
        self._com_function = com_function
        self._buffer = ""

    def __str__(self):
        return "Laser: (" + self._serial.name + ")"

    def _sendNextCommand(self):
        next_comm = self._commandQueue[0]
        self._serial.write(next_comm.getCommand()+"\r")
        next_com.setState(COMMAND_STATE_SENT)
        self._state = LASER_STATE_WAITING_FOR_REPLY

    def _readInput(self):
        while ser.inWaiting():
            self._buffer += (ser.readline())
        if (self._buffer[-2:] == '\r\n'):
            

    def update(self):

    def close(self):
        

def defaultComFunc(string):
    print (string)
