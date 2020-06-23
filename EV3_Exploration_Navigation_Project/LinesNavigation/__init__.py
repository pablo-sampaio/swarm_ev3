

LIGHT_LIMIT = 35  # values equal or below this threshold indicates a black line
                  # a "not black" line is 10% above this value; intermediate values are not used to decide lines' limits


def detectAllLinesAround(robot):
    print("Detecting black lines")
    robot.resetOrientation()

    angles = []
    inblack = False
    maxTurnDegree = 360 # the robots will do a complete turn around itself

    if (robot.lightRight.value() <= LIGHT_LIMIT):  # it is in a line
        inblack = True
        maxTurnDegree = 330  #lines after this are probably the first line
        print("- starts in a line")
        angles.append(0)

    robot.turnForEver(150)

    while (robot.getOrientation() < maxTurnDegree):
        if (not inblack and robot.lightRight.value() <= LIGHT_LIMIT):
            inblack = True
            angles.append(robot.getOrientation()) #initial orientation where the black line was identified

        if (inblack and robot.lightRight.value() > 1.1 * LIGHT_LIMIT):
            #testar e descartar se a linha é muito pequena?
            print("- line width:", robot.getOrientation()-angles[-1])
            inblack = False
            if angles[-1] != 0: #if it is not the line in orientation 0 deg
                angles[-1] = (angles[-1] + robot.getOrientation()) / 2  #average between initial and final orientation of the black line

    robot.stopMotors("brake")
    robot.turnToOrientation(0, 150)

    return angles


def centralizeInLine(robot, direction=None):
    ''' Assuming that the agent is over a black line, this function centralizes the
    robot in the center of the line.
        Direction can be +1 or -1 to indicate the next direction that the robot must turn
    to find the other limit of the line (current orientation is considered a limit).
    If it is None, than both limits of the line must be found.'''
    assert (robot.lightRight.value() <= 1.1*LIGHT_LIMIT), "Robot must be on a line!"

    leftLim, rightLim = None, None
    startOrientation = robot.getOrientation()

    if direction == +1:
        leftLim = startOrientation
    elif direction == -1:
        rightLim = startOrientation

    if direction == +1 or direction is None:
        robot.turnForEver(150)
        while (robot.getOrientation() < startOrientation+90 and robot.lightRight.value() <= 1.1*LIGHT_LIMIT):
            pass
        robot.stopMotors("brake")
        rightLim = robot.getOrientation()

    if direction is None:
        # put the robot back to the black line
        robot.turnForEver(-150)
        while (robot.getOrientation() < startOrientation + 90 and robot.lightRight.value() > LIGHT_LIMIT):
            pass

    if direction == -1 or direction is None:
        robot.turnForEver(-150)
        while (robot.getOrientation() > startOrientation-90 and robot.lightRight.value() <= 1.1*LIGHT_LIMIT):
            pass
        robot.stopMotors("brake")
        leftLim = robot.getOrientation()

    robot.turnToOrientation((leftLim+rightLim)/2, 150)


def goToNthLine(robot, n):
    '''Drives the robot to the n-th black line from its current position,
       in clockwise direction.
       Counting starts at 0 and includes the line where the robot is (if any).'''
    robot.resetOrientation()

    inblack = False
    count = 0
    maxTurnDegree = 360

    if (robot.lightRight.value() <= LIGHT_LIMIT):  # it is in a line
        inblack = True
        maxTurnDegree = 330  # lines detected after this limit are probably the first line again
        if (n == 0):
            centralizeInLine(robot)
            return robot.getOrientation()

    robot.turnForEver(150)

    while (robot.getOrientation() < maxTurnDegree):
        if (not inblack and robot.lightRight.value() <= LIGHT_LIMIT):
            inblack = True
            if (count == n):
                #print("- line", count)
                robot.stopMotors("brake")
                centralizeInLine(robot, +1)
                return robot.getOrientation()
        if (inblack and robot.lightRight.value() > 1.1 * LIGHT_LIMIT):
            inblack = False
            count = count + 1

    robot.stopMotors("brake")
    return None


def findLineNearby(robot, centralize=True):
    robot.resetOrientation()

    if (robot.lightRight.value() <= LIGHT_LIMIT):
        if centralize:
            centralizeInLine(robot)
        return robot.getOrientation()

    for angle in [10,20,30]:
        for sign in [+1,-1]:
            print("- at", sign * angle)
            desiredOrientation = sign * angle
            robot.turnForEver(sign * 150)

            while (sign == +1 and robot.getOrientation() < desiredOrientation) \
                    or (sign == -1 and robot.getOrientation() > desiredOrientation):
                if (robot.lightRight.value() <= LIGHT_LIMIT):
                    robot.stopMotors("brake")
                    if centralize:
                        centralizeInLine(robot, sign)
                    return robot.getOrientation()

            robot.stopMotors("brake")

    return None
