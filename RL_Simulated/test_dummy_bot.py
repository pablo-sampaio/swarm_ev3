
import random as rand

from RL.agents import DynaQPlusAgent
from RL.environments import Ev3GridEnv, _DummyBot


########### MAIN ############

rand.seed(21)

robot=_DummyBot()
env = Ev3GridEnv(robot, count_visits=True, reward_option='step_cost')
agent1 = DynaQPlusAgent(planning_steps=5, kappa=0.0)
#agent1 = DynaQPlusAgent(planning_steps=5, kappa=0.0, model_option='state+next_state+actions')

agent1.full_train(env, max_episodes=20)

print(env.visits)
#print(env.get_visits_with_nonnegative_pos())
print(agent1.train_step)

# 20 episodios
# AMBIENTE:                             GOAL    STEP-COST
# SEM OTIMISMO (state+actions):         1514    1179
# OTIMISTA (state+next-state+actions):  2737    1261

# 5 episodios
#               Goal    Step
# SEM OTIM      312     276
# OTIM          540     264
