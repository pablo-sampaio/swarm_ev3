
class PID:
    """	Discrete PID control
    """

    def __init__(self, kp=2.0, ki=0.0, kd=1.0, Integrator_max=500, Integrator_min=-500):
        self.Kp=kp
        self.Ki=ki
        self.Kd=kd

        self.Integrator=0.0
        self.Integrator_max=Integrator_max
        self.Integrator_min=Integrator_min

        self.last_error=0.0
        self.set_point=0.0

        self.P_value = self.I_value = self.D_value = 0.0
        self.Integrator = 0.0

    def setPoint(self, set_point):
        """	Initilize the setpoint of PID
        """
        self.set_point = set_point
        self.Integrator = 0
        self.last_error = 0

    def set_ideal_form(self, kp, ki, kd, Integrator_max=500, Integrator_min=-500):
        self.Kp = kp
        self.Ki = ki
        self.Kd = kd

        self.Integrator = 0.0
        self.Integrator_max = Integrator_max
        self.Integrator_min = Integrator_min

        self.last_error=0.0
        #self.set_point=0.0

        self.P_value = self.I_value = self.D_value = 0.0
        self.Integrator = 0.0

    def set_standard_form(self, Kp, Ti, Td, Integrator_max=500, Integrator_min=-500):
        self.Kp = Kp
        self.Ki = Kp / Ti
        self.Kd = Kp * Td

        self.Integrator = 0.0
        self.Integrator_max = Integrator_max
        self.Integrator_min = Integrator_min

        self.last_error = 0.0
        #self.set_point = 0.0

        self.P_value = self.I_value = self.D_value = 0.0
        self.Integrator = 0.0

    def update(self,current_value):
        """	Calculate PID output value for given reference input and feedback
        """
        error = self.set_point - current_value

        self.P_value = self.Kp * error
        self.D_value = self.Kd * (error - self.last_error)
        self.last_error = error

        self.Integrator = self.Integrator + error

        if self.Integrator > self.Integrator_max:
            self.Integrator = self.Integrator_max
        elif self.Integrator < self.Integrator_min:
            self.Integrator = self.Integrator_min

        self.I_value = self.Integrator * self.Ki

        #print("PID =", self.P_value, self.I_value, self.D_value)
        PID = self.P_value + self.I_value + self.D_value

        return PID
