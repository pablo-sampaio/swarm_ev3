
import random as rand

from RL.agents import DynaQPlusAgent, DynaQPlusAgentExperimental, LRTAStarAgent
from RL.environments import SimulatedEnv, Ev3GridEnv

def print_visits(visits):
    for row in visits:
        print(row)

NUM_EPISODES = 10

rand.seed(17)

env = SimulatedEnv(count_visits=True, reward_option='step_cost')
#print(list(env.states()))
print(len(list(env.states())), "states")

# 1. This code shows the simplest way to train an agent, using an
#    experimental version of Dyna-Q+ (but can be used in the others)
print("Experimental Dyn-Q+:")
agent1 = DynaQPlusAgentExperimental(planning_steps=10, kappa=0.0)
agent1.full_train(env, max_episodes=NUM_EPISODES)
print_visits(env.visits)
print(agent1.train_step)

rand.seed(17)
env.reset_visits()
print()

# 2. This code shows an alternative way to train an agent, where
#    one can access information from each step
print("Standard Dyna-Q+:")
agent2 = DynaQPlusAgent(planning_steps=10, kappa=0.0)
agent2.start_train(env)
for epi in range(NUM_EPISODES):
    terminal = False
    print("- episode #", epi)
    while not terminal:
        _, _, _, terminal = agent2.step_train()
print_visits(env.visits)
print(agent2.train_step)

rand.seed(17)
env.reset_visits()
print()

# 3. This code shows a variation of the second way to train an agent, 
#    that allows you to get information from each initial step 
print("LRTA*:")
agent3 = LRTAStarAgent()
agent3.start_train(env)
for epi in range(NUM_EPISODES):
    initial_state = agent3.reset_env()  # attention: don't reset the environment directly, or the agent will miss the information of the current state
    terminal = False
    print("- episode #", epi, "starting at", initial_state)
    while not terminal:
        _, _, _, terminal = agent3.step_train()
print_visits(env.visits)
print(agent3.train_step)

