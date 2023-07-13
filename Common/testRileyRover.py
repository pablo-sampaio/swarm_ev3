#!/usr/bin/env python3

from ev3dev.ev3 import Button, Sound
from time import *
import platform

from BotHardware import RileyRoverBase
from RfidReader import RfidSerialThread
from LinesNavigation import *


robot = RileyRoverBase()


###########################
## MAIN FUNCTIONS

def TEST0():
    robot.runMotorsTimed(1.5, 300, 300)
    robot.resetOrientation()
    print("Motors", robot.leftMotor.position, robot.rightMotor.position)
    print("Orientation", robot.getOrientation())
    sleep(2)

    robot.turnToOrientation(90)
    sleep(0.5)
    robot.turnToOrientation(180)
    sleep(0.5)
    robot.turnToOrientation(3* 360)


def TEST1():
    robot.runMotorsTimed(1.5, 300, 300)
    robot.resetOrientation()
    print("Motors", robot.leftMotor.position, robot.rightMotor.position)
    print("Orientation", robot.getOrientation())
    sleep(2)

    robot.turnToOrientation(90)
    sleep(0.5)
    robot.turnToOrientation(-90)
    sleep(0.5)
    robot.turn(180)
    robot.runMotorsTimed(1.0, 400, 400)
    robot.turn(-90)


def TEST2():
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


def TEST3():
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


def TEST4():
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


def TEST5_BUG():
    # this a bug in an older version of reset orientation
    robot.runMotorsTimed(3, 150, 150)
    robot.turn(190)
    sleep(1)

    #antigo robot.resetOrientation()
    robot.leftMotor.position = 0
    robot.rightMotor.position = 0


def TEST6():
    robot.runMotorsDistance(125, 300)
    robot.stopMotors("hold")
    sleep(5)
    #robot.runMotorsDistance(-25, 100)
    #robot.stopMotors("hold")
    #robot.runMotorsDistance(125, 100)
    #robot.stopMotors("coast")


def TEST7():
    robot.resetOrientation()
    centralizeInLine(robot)


def TEST8():
    ANGLE_TO_SCAN = 15
    VELOCITY = 40

    sleep(2)

    # 1. Scan from -ANGLE_TO_SCAN to +ANGLE_TO_SCAN to find the min distance
    min_distance = max(robot.getDistanceAhead(), robot.getDistanceAhead())
    print("Finding minimum distance...")
    print(" - initial distance:", min_distance)
    
    robot.resetOrientation()

    robot.turnToOrientation(-ANGLE_TO_SCAN, VELOCITY)
    robot.turnForEver(VELOCITY)

    while robot.getOrientation() < ANGLE_TO_SCAN:
        distance = max(robot.getDistanceAhead(), robot.getDistanceAhead())
        if distance < min_distance:
            min_distance = distance
    robot.stopMotors()

    print(" - min distance:", min_distance)

    # 2. Scan multiple times from +ANGLE_TO_SCAN to -ANGLE_TO_SCAN to stop at "min distance + error"
    #    where the admissable error is increased in each scan.
    print("Scanning to stop at minimum distance...")
    error = 0.05
    scan_min_dist = robot.getDistanceAhead()
    found = scan_min_dist <= (min_distance + error)

    while not found:
        robot.turnForEver(-VELOCITY)
        while not found and robot.getOrientation() > -ANGLE_TO_SCAN:
            distance = robot.getDistanceAhead()
            scan_min_dist = min(distance, scan_min_dist)
            found = distance <= (min_distance + error)

        if found:
            break

        error *= 2.0
        robot.turnForEver(+VELOCITY)
        while not found and robot.getOrientation() < +ANGLE_TO_SCAN:
            distance = robot.getDistanceAhead()
            scan_min_dist = min(distance, scan_min_dist)
            found = distance <= (min_distance + error)

        error *= 2.0
        print(" - after 2 scans, admissable error is", error, "min distance found was", scan_min_dist)
        print(" - last distance was", distance)

    robot.stopMotors()
    
    print("Final distance:", robot.getDistanceAhead())
    print("Final orientation:", robot.getOrientation())


#######################
### ENTRY POINT

try:
    #TEST7()
    #TEST6()
    #TEST0()
    #TEST8()
    for i in range(10):
        print("Color:", robot.readColor())
        sleep(1)

except:
    print("Error. More info:")
    robot.stopMotors("coast")
    import traceback
    traceback.print_exc()
