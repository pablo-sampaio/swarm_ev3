from time import sleep
from ev3dev.ev3 import *
from PID import PID


class AbstractHardwareBase:
    ''' Abstract class. Each subclass implements functionality that is dependent
        on the model (how it is built and what are its components).
    '''
    def __init__(self, port_motor_l, port_motor_r, port_light_l, port_light_r, degreesPerCm):
        self.rightMotor = LargeMotor(port_motor_r)
        self.leftMotor = LargeMotor(port_motor_l)

        self.DIST_TO_DEGREE_FACTOR = degreesPerCm   # how many degrees a wheel turns to walk 1 cm
        self.pid_controller = PID(4.0, 0, 1.0)  # each subclass should instantiate a PID controller properly calibrated for the model

        self.lightRight = ColorSensor(port_light_r)
        assert self.lightRight.connected, "Connect a color sensor to port " + port_light_r
        self.lightRight.mode = 'COL-REFLECT'

        self.lightLeft = ColorSensor(port_light_l)
        if (self.lightLeft.connected):
            self.lightLeft.mode = 'COL-REFLECT'
            self.followLine = self._followline_2sensors
        else:
            self.followLine = self._followline_1sensor
        
        # attributes created to be acessed directly (public)
        self.brickButton = Button()
        self.speaker = Sound

    def readColor(self):
        self.lightRight.mode = 'COL-COLOR'
        sleep(0.1)
        color = self.lightRight.color
        self.lightRight.mode = 'COL-REFLECT'

    def runMotors(self, leftVelocity, rightVelocity):
        self.leftMotor.run_forever(speed_sp=leftVelocity)
        self.rightMotor.run_forever(speed_sp=rightVelocity)

    def runMotorsAngle(self, wheelAngle, velocity=200, wait=True):
        nextLeftPos = self.leftMotor.position + wheelAngle
        nextRightPos = self.rightMotor.position + wheelAngle
        self.leftMotor.run_to_abs_pos(position_sp=nextLeftPos, speed_sp=velocity, stop_action="hold")
        self.rightMotor.run_to_abs_pos(position_sp=nextRightPos, speed_sp=velocity, stop_action="hold")
        if wait:
            self.leftMotor.wait_while('running')
            self.rightMotor.wait_while('running')

    def runMotorsDistance(self, distance, velocity=200, wait=True):
        assert velocity > 0
        deltaWheelDegree = distance * self.DIST_TO_DEGREE_FACTOR
        nextLeftPos = self.leftMotor.position + deltaWheelDegree
        nextRightPos = self.rightMotor.position + deltaWheelDegree
        self.leftMotor.run_to_abs_pos(position_sp=nextLeftPos, speed_sp=velocity, stop_action="brake")
        self.rightMotor.run_to_abs_pos(position_sp=nextRightPos, speed_sp=velocity, stop_action="brake")
        if wait:
            self.leftMotor.wait_while('running')
            self.rightMotor.wait_while('running')

    def runMotorsTimed(self, time, leftVelocity=200, rightVelocity=200, stop_action="brake"):
        self.leftMotor.run_forever(speed_sp=leftVelocity)
        self.rightMotor.run_forever(speed_sp=rightVelocity)
        sleep(time)
        self.leftMotor.stop(stop_action=stop_action)
        self.rightMotor.stop(stop_action=stop_action)

    def isRunning(self):
        return self.leftMotor.is_running or self.rightMotor.is_running

    def stopMotors(self, stop_action="brake"):
        self.leftMotor.stop(stop_action=stop_action)
        self.rightMotor.stop(stop_action=stop_action)

    def _followline_2sensors(self, velocity=200):
        print("FRONT_2sensors")

        output = (- self.lightLeft.value()) + self.lightRight.value()
        correction = self.pid_controller.update(output)

        if (correction > 100):
            #over = over + 1
            correction = 100.0
        elif (correction < -100):
            #over = over + 1
            correction = -100.0

        goLeft = (correction < 0)
        speedProportion = 1 - (abs(correction) / 100.0)

        if (goLeft):
            leftVel = velocity * speedProportion
            rightVel = velocity
        else:
            leftVel = velocity
            rightVel = velocity * speedProportion

        #print('- lvel:', "%.2f" % leftVel, 'rvel', "%.2f" % rightVel)
        self.runMotors(leftVel, rightVel)

    def _followline_1sensor(self, velocity=200): # uses only the right sensor
        ''' Goes front following a line using only one light sensor. Uses a PD controller, where the
            target luminosity is 20. If it is below (darker), goes right; if above (lighter), goes left.
        '''
        #print("FRONT_1sensor")
        output = self.lightRight.value()
        correction = self.pid_controller.update(output)

        if (correction > 100):
            #over = over + 1
            correction = 100.0
        elif (correction < -100):
            #over = over + 1
            correction = -100.0

        goLeft = (correction < 0)
        speedProportion = 1 - (abs(correction) / 100.0)

        if (goLeft):
            leftVel = velocity * speedProportion
            rightVel = velocity
        else:
            leftVel = velocity
            rightVel = velocity * speedProportion

        #print('- lvel:', "%.2f" % leftVel, 'rvel', "%.2f" % rightVel)
        self.runMotors(leftVel, rightVel)

    def getDistanceAhead(self):  # in cm
        return None

    def getOrientation(self):
        '''Returns the angle in degrees to where the agent is headed, considering only
        (all kinds of) turn actions after the last resetOrientation(). If a non-turn is done
        after resetting, the orientation is not guaranteed to have a correct value. '''
        pass

    def resetOrientation(self):
        '''Defines the current orientation of the robot as zero degree. After you do a
        non-turn movement, it is recommended to call this method before calling "turnToOrientation()".'''
        pass

    def turnForEver(self, velocity):
        pass

    def turn(self, rel_degrees, velocity): # relative degrees in clockwise, use negative to counter-CW
        pass

    def turnToOrientation(self, abs_degrees, velocity):
        '''Orientation of the robot, considering only "turn" actions.'''
        pass
