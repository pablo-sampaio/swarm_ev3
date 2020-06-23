
from time import sleep
from ev3dev.ev3 import *
from PID import PID


class AbstractBotHardware:
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


class EducatorBot(AbstractBotHardware):
    ''' Class to control the Educator Robot o(ficial model in LEGO EV3 Education), with some
        customization (main brick inverted, gyro in upside down position, using non-standard ports).
    '''
    def __init__(self):
        AbstractBotHardware.__init__(self, 'outD', 'outA', 'in2', 'in3', (7.0 * 360 / 122.5))

        self.gyro = GyroSensor()
        assert self.gyro.connected, "Connect a gyro sensor to any sensor port"
        self.gyro.mode='GYRO-ANG'

        #self.distSensor = UltrasonicSensor()
        #assert self.distSensor.connected, "Connect an ultrasonic distance sensor to any sensor port"
        #self.distSensor.mode='US-DIST-CM'  #attention: it measures milimeters indeed

        # if (self.lightLeft.connected):
        #     print("LineFollower - 2 sensors")
        #     self.pid_controller = PID(0.5, 0, 0.7)
        #     self.pid_controller.setPoint(0)
        # else:
        #     print("LineFollower - 1 sensor")
        #     self.pid_controller = PID(1.5, 0, 1.0)
        #     self.pid_controller.setPoint(20)

    def getDistanceAhead(self):
        return self.distSensor.value() / 10.0  #in cm

    def getOrientation(self):
        return -self.gyro.angle

    def resetOrientation(self):
        # changing mode resets the angle (cannot set to 0 directly)
        self.gyro.mode = 'GYRO-RATE'
        sleep(0.5)
        self.gyro.mode = 'GYRO-ANG'

    def turnForEver(self, velocity=150):
        self.runMotors(+velocity, -velocity)

    def turn(self, rel_degrees, velocity=150): # relative degrees in clockwise, use negative to counter-CW
        assert velocity > 0, "Use negative degrees to turn counter-clockwise"
        if (rel_degrees >= 0):
            self._turnToOrientRight(self.getOrientation() + rel_degrees, velocity)
        else:
            self._turnToOrientLeft(self.getOrientation() + rel_degrees, velocity)

    def turnToOrientation(self, abs_degrees, velocity=150):
        assert velocity > 0, "Use degree value below current orientation to turn counter-clockwise"
        if (abs_degrees >= self.getOrientation()):
            self._turnToOrientRight(abs_degrees, velocity)
        else:
            self._turnToOrientLeft(abs_degrees, velocity)

    def _turnToOrientRight(self, targetDegree, velocity=150):
        self.runMotors(+velocity, -velocity)
        while (self.getOrientation() < targetDegree):
            pass
        self.stopMotors(stop_action="hold")
        sleep(0.1)
        if (self.getOrientation() > (targetDegree + 1)):  # this improves precision of right (and makes its error symetrical to left's)
            self.runMotors(-50, +50)
            while (self.getOrientation() > (targetDegree + 1)):
                pass
            self.stopMotors(stop_action="hold")

    def _turnToOrientLeft(self, targetDegree, velocity=150):
        self.runMotors(-velocity, +velocity)
        while (self.getOrientation() > targetDegree):
            pass
        self.stopMotors(stop_action="hold")
        sleep(0.1)
        if (self.getOrientation() < targetDegree):
            self.runMotors(+40, -40)
            while (self.getOrientation() < targetDegree):
                pass
            self.stopMotors(stop_action="hold")


class EnterpriseBot(AbstractBotHardware):
    ''' Class to control the Entreprise Robot, model by Seshan brothers made with LEGO EV3 Home Edition.
    '''
    def __init__(self):
        AbstractBotHardware.__init__(self, 'outD', 'outA', 'in1', 'in4', (8.0 * 360 / 106.8))  # from experiment: in 8 turns, almost 107 cm
        self.pid_controller = PID(3.0, 0.2, 1.0)  # usa valores mais adequados ao Enterprise
                                                  # opcoes passadas: (6,0,1), point: 20
        self.pid_controller.setPoint(15)
        self.WHEEL_FACTOR = 2.290  # entre 2.275 e 2.290

        self.leftMotorZero = self.leftMotor.position
        self.rightMotorZero = self.rightMotor.position

        #self.irSensor = InfraredSensor()
        #assert self.irSensor.connected, "Connect an infrared distance sensor to any sensor port"
        #self.irSensor.mode = 'IR-PROX'
        #self.distSensor = UltrasonicSensor()
        #self.distSensor.mode = 'US-DIST-CM'  # attention: it measures milimeters indeed

    def getDistanceAhead(self):
        #if self.irSensor.connected:
        #    return self.irSensor.value() # TODO: convert to cm
        #else:
        #    return None
        #return self.distSensor.value() / 10
        return None

    def getOrientation(self):
        deltaLeft = self.leftMotor.position - self.leftMotorZero
        deltaRight = self.rightMotor.position - self.rightMotorZero
        assert (deltaLeft + deltaRight) < 30, "Motors are not in symmetrical positions: " + str(deltaLeft) + "/" + str(deltaRight)  # did you do a non-turn movement after last reset?
        return (deltaLeft - deltaRight) / 2.0 / self.WHEEL_FACTOR

    def resetOrientation(self):
        sleep(0.5)  # to wait for full stop, in case the robot is in an inertial movement
        self.leftMotorZero = self.leftMotor.position
        self.rightMotorZero = self.rightMotor.position
        # obs.: zeroing the "position" attribute of the motors causes bugs, probably due to concurrency

    def turnForEver(self, velocity=130):
        self.runMotors(+velocity, -velocity)

    def turn(self, rel_degrees, velocity=130):  # relative degrees in clockwise, use negative to counter-CW
        assert velocity > 0, "Use negative degrees to turn counter-clockwise"
        wheelDeltaAngle = self.WHEEL_FACTOR * rel_degrees
        if -1 <= wheelDeltaAngle <= +1:
            return
        nextLeftPos = self.leftMotor.position + wheelDeltaAngle
        nextRightPos = self.rightMotor.position - wheelDeltaAngle
        self.leftMotor.run_to_abs_pos(position_sp=nextLeftPos, speed_sp=velocity, stop_action="brake")
        self.rightMotor.run_to_abs_pos(position_sp=nextRightPos, speed_sp=velocity, stop_action="brake")
        self.leftMotor.wait_while('running')
        self.rightMotor.wait_while('running')

    def turnToOrientation(self, abs_degrees, velocity=130):
        assert velocity > 0, "Use degree value below current orientation to turn counter-clockwise"
        rel_degrees = abs_degrees - self.getOrientation()
        self.turn(rel_degrees, velocity)
