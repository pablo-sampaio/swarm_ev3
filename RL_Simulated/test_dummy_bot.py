
import random as rand

from RL.agents import DynaQPlusAgent
from RL.environments import Ev3GridEnv


class _DummyBot:
    ''' Class created only to test the Ev3GridEnv
    '''
    def __init__(self):
        class _Button:
            def __init__(self, parent):
                self.parent = parent
            def any(self):
                self.parent.count = 0
                return True
        class _Sound:
            def beep(self):
                print("Beeep!")
                pass
        self.brickButton = _Button(self)
        self.speaker = _Sound()
        self.count = 0
        self.orientation = 0.0

    def readColor(self):
        return 5 if self.count >= 20 else 3 

    def runMotorsDistance(self, distance, velocity=200, wait=True):
        self.count += 1

    def getOrientation(self):
        return self.orientation

    def resetOrientation(self):
        self.orientation = 0.0

    def turnToOrientation(self, abs_degrees, velocity=50):
        self.orientation = abs_degrees

    def getDistanceAhead(self):
        return 25.0


########### MAIN ############

env = Ev3GridEnv(robot=_DummyBot(), count_visits=True)
agent1 = DynaQPlusAgent(planning_steps=2, kappa=0.0)

agent1.full_train(env, max_episodes=20)
print(env.visits)
print(env.get_visits_with_nonnegative_pos())
print(agent1.train_step)
