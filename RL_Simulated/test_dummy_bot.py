
import random as rand

from RL.agents import DynaQPlusAgentExperimental
from RL.environments import Ev3GridEnv, _DummyBot

def print_visits(visits):
    for row in visits:
        print(row)


########### MAIN ############

rand.seed(21)

robot=_DummyBot()
env = Ev3GridEnv(robot, count_visits=True, reward_option='step_cost', wait_every_step=0)
agent1 = DynaQPlusAgentExperimental(planning_steps=5, kappa=0.0, model_option='transition+', default_q=1.0)
#agent1 = DynaQPlusAgentExperimental(planning_steps=5, kappa=0.0, model_option='optimistic_transition+')

agent1.full_train(env, max_episodes=5)

print(env.visits)
print_visits(env.get_visits_with_nonnegative_pos())
print(agent1.train_step)

# SEM REVERSAO / 5 plan_steps

## 20 episodios
 # AMBIENTE:                                GOAL        STEP_COST
 # SEM OTIMISMO (transition+):              1514        1179
 # MODELO OTIMISTA (optimistic_transition+):   2737        1261
 # Q OTIMISTA:                              1110 (q=1)  1179 (q=0) / 1163 (q=1)
 
## 5 episodios
 #               Goal    Step
 # SEM OTIM      312     276
 # MOD OTIM      540     264
 # Q OTIM        273     276 (q=0) / 299 (q=1)

