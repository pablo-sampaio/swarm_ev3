
from .abstract_base import AbstractHardwareBase
from time import sleep
from ev3dev.ev3 import *


class _EducatorBase(AbstractHardwareBase):
    ''' Class to control the Educator Robot o(ficial model in LEGO EV3 Education), with some
        customization (main brick inverted, gyro in upside down position, using non-standard ports).
    '''
    def __init__(self):
        AbstractHardwareBase.__init__(self, 'outC', 'outA', 'in2', 'in3', (7.0 * 360 / 122.5))

        self.gyro = GyroSensor()
        assert self.gyro.connected, "Connect a gyro sensor to any sensor port"
        self.gyro.mode='GYRO-ANG'

        self.distSensor = UltrasonicSensor()
        if self.distSensor.connected:
            self.distSensor.mode='US-DIST-CM'  #attention: it measures milimeters indeed
        else:
            #self.distSensor = None
            print("No ultrasonic distance sensor connected to any sensor port. Going on.")

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
        #return -self.gyro.angle  #attention: use this if sensor is placed upside down 
        return self.gyro.angle

    def resetOrientation(self):
        # changing mode resets the angle (cannot set to 0 directly)
        self.gyro.mode = 'GYRO-RATE'
        sleep(0.5)
        self.gyro.mode = 'GYRO-ANG'

    def turnForEver(self, velocity=150):
        self.runMotors(+velocity, -velocity)

    def turn(self, rel_degrees, velocity=150): # relative degrees in clockwise, use negative to counter-CW
        assert velocity > 0, "Negative velocity prohibited. Use negative degrees to turn counter-clockwise"
        if (rel_degrees >= 0):
            self._turnToOrientRight(self.getOrientation() + rel_degrees, velocity)
        else:
            self._turnToOrientLeft(self.getOrientation() + rel_degrees, velocity)

    def turnToOrientation(self, abs_degrees, velocity=150):
        assert velocity > 0, "Negative velocity prohibited. Use degree value below current orientation if you want to turn counter-clockwise"
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
            self.runMotors(-40, +40)
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
