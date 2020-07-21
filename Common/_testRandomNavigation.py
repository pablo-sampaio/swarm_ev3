#!/usr/bin/env python3

from ev3dev.ev3 import Button, Sound
from BotHardware import EnterpriseBot
from RfidReader import RfidSerialThread
import random
from ECEP import *

robot = EnterpriseBot()

# This distance varies according to how the RFID antenna is assembled, so we left it
# here (and not inside the class definition) to remember to ajust accordingly.
# Distance measured considering the RFID antenna as position 0, being positive if the
# antenna comes "before" the axis (i.e. when the axis is over an RFID tag, the robot 
# must move forward to let the antenna exactly above the tag).
robot.RFID_TO_AXIS_DISTANCE = 4.0  


#######################
### ENTRY POINT

try:
    navData = navigateInitialize(robot)

    nextNode = navData.getNode(random.randrange(0, navData.getNumNodes())) # chooses a random neighbor
    navData = navigateToNeighbor(robot, navData, nextNode)

    #navData = navigateFollowPath(robot, navData, [])

except:
    print("Error. More info:")
    import traceback
    traceback.print_exc()
    robot.stopMotors("coast")
    RfidSerialThread.getInstance().stop()

