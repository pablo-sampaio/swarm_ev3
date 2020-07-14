
from .abstract_base import AbstractHardwareBase
from time import sleep
from ev3dev.ev3 import *


class _EnterpriseBase(AbstractHardwareBase):
    ''' Class to control the Entreprise Robot, model by Seshan brothers made with LEGO EV3 Home Edition.
    '''
    def __init__(self):
        AbstractHardwareBase.__init__(self, 'outD', 'outA', 'in1', 'in4', (8.0 * 360 / 106.8))  # from experiment: in 8 turns, almost 107 cm
        self.pid_controller = PID(3.0, 0.2, 1.0)  # usa valores mais adequados ao Enterprise
                                                  # opcoes passadas: (6,0,1), point: 20
        self.pid_controller.setPoint(15)
        self.WHEEL_FACTOR = 2.290  # bom entre 2.275 e 2.290

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
