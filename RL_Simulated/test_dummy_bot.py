
import random as rand

from RL.agents import DynaQPlusAgent
from RL.environments import Ev3GridEnv, _DummyBot


########### MAIN ############

env = Ev3GridEnv(robot=_DummyBot(), count_visits=True)
agent1 = DynaQPlusAgent(planning_steps=2, kappa=0.0)

agent1.full_train(env, max_episodes=20)
print(env.visits)
print(env.get_visits_with_nonnegative_pos())
print(agent1.train_step)
