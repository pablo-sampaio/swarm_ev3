#!/usr/bin/env python3

from ev3dev.ev3 import Button, Sound
from BotHardware import EnterpriseBot
from RfidReader import RfidSerialThread
import random
from ECEP import *

robot = EnterpriseBot()

# TODO: definir direto na classe
robot.RFID_TO_AXIS_DISTANCE = 4.0  #old: 5.7  # measure considering the axis as 0, and considering positive if should move forward to reach RFID reader


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

