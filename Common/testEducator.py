#!/usr/bin/env python3

from ev3dev.ev3 import Button, Sound
from time import *
import platform

from BotHardware import EducatorBase

from RfidReader import RfidSerialThread
from LinesNavigation import *


robot = EducatorBase()


def rotate(list, index): #not used yet
    return list[index:] + list[:index]


###########################
## MAIN FUNCTIONS

def TEST1(): #ok
    robot.runMotorsTimed(1.5, 300, 200)

    print("Orientation before reset:", robot.getOrientation())
    robot.resetOrientation()
    print("Orientation after reset:", robot.getOrientation())
    print("Motors", robot.leftMotor.position, robot.rightMotor.position)
    sleep(3)

    robot.turnToOrientation(90)
    robot.turnToOrientation(-90)
    robot.runMotorsTimed(2.0, 200, 200)
    robot.turn(180)
    robot.runMotorsTimed(1.0, 400, 400)
    robot.turn(-90)
    print("Final orientation:", robot.getOrientation())


def TEST2(): #not tested!!!
    brickButton = Button()
    rfidReader = RfidSerialThread("COM5" if (platform.system() == "Windows") else "/dev/ttyUSB0")

    print("FOLLOWING LINES, DETECTING TAGS:")
    rfidReader.start()
    sleep(4)
    robot.resetOrientation()

    while not brickButton.any():
        robot.followLine(200)

        if rfidReader.getCurrentTagId() is not None:
            robot.stopMotors()
            print("TAG FOUND - id", rfidReader.getCurrentTagId())
            Sound.beep()
            sleep(1)
            robot.runMotorsDistance(-5.7, 150)
            sleep(4)
            robot.runMotorsDistance(12.0, 150) #to go past the tag

        if (robot.getDistanceAhead() is not None and robot.getDistanceAhead() < 20):
            print("Obstacle! Dist =", robot.getDistanceAhead(), "Exiting...")
            break

    robot.stopMotors()
    rfidReader.stop()


def TEST3():  #not tested!!!
    print("DETECTING ALL BLACK LINES AROUND:")
    angles = detectAllLinesAround(robot)
    print(angles)

    print("Verifying angles")
    sleep(10)

    robot.resetOrientation()
    for a in angles:
        robot.turnToOrientation(a)
        if robot.lightRight.value() <= 50:
            print("- ok, angle", a, "light", robot.lightRight.value())
        else:
            print("- fail, angle", a, "light", robot.lightRight.value())
        sleep(1)

    robot.turnToOrientation(0)


def TEST4():  #not tested!!!
    print("TESTING BASIC LINE DETECTION:")

    ang = findLineNearby(robot)
    print("Nearest line was at (from start position):", ang)
    sleep(3)

    for n in [0,1,2]:
        orient = goToNthLine(robot, n)
        sleep(3)
        if (orient is not None):
            print("Line", n, "found at", orient, "degrees")
            robot.turn(-orient, 150)
        else:
            print("Line", n, "not found")


def TEST5_BUG():  #not tested!!!
    # this was a bug in enterprise
    robot.runMotorsTimed(3, 150, 150)
    robot.turn(190)
    sleep(1)

    #antigo robot.resetOrientation()
    robot.leftMotor.position = 0
    robot.rightMotor.position = 0


def TEST6(): #ok
    '''# to calibrate the distance
    robot.leftMotor.run_to_abs_pos(position_sp=robot.leftMotor.position+7*360, speed_sp=100, stop_action="hold")
    robot.rightMotor.run_to_abs_pos(position_sp=robot.rightMotor.position+7*360, speed_sp=100, stop_action="hold")
    robot.leftMotor.wait_while('running')
    robot.rightMotor.wait_while('running')
    sleep(20)
    '''
    robot.runMotorsDistance(40, 100)
    robot.stopMotors("hold")
    sleep(10)
    robot.runMotorsDistance(-40, 100)
    robot.stopMotors("coast")
    #'''

def TEST7():  #not tested!!!
    robot.resetOrientation()
    centralizeInLine(robot)


#######################
### ENTRY POINT

try:
    TEST6()
    robot.stopMotors("coast")

except:
    print("Error. More info:")
    robot.stopMotors("coast")
    import traceback
    traceback.print_exc()
