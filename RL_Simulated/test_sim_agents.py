
import random as rand

from RL.agents import DynaQPlusAgent, LRTAStarAgent
from RL.environments import SimulatedEnv, Ev3GridEnv


rand.seed(17)

env = SimulatedEnv(count_visits=True, reward_option='step_cost')
#print(list(env.states()))
print(len(list(env.states())), "states")

agent1 = DynaQPlusAgent(planning_steps=10, kappa=0.0)
agent1.full_train(env, max_episodes=20)
print(env.visits)
print(agent1.train_step)

env.reset_visits()
agent2 = LRTAStarAgent()
agent2.full_train(env, max_episodes=20)
print(env.visits)
print(agent2.train_step)

# alternative trainning loop:
'''agent.start_train(env)
for epi in range(20):
    terminal = False
    print("Episode #", epi)
    while not terminal:
        _, _, _, terminal = agent.step_train()
print(env.visits)'''
