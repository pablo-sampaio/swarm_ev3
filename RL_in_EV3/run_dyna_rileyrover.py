#!/usr/bin/env python3

from RL.agents import DynaQPlusAgent
from BotHardware import RileyRoverBase
from ev3_environments import RileyRoverGridEnv
#from ev3_environments import Kraz3GridEnv  # this is an IMPROVED version of RileyRover env, TODO: test with the RileyRover base

import random as rand
import sys

# works when running from Ctrl+F5 in VS Code, or running from
# command line, but doesn't work when it is run from the brick interface
OUTPUT_TO_FILE = True
if OUTPUT_TO_FILE:
    sys.stdout = open("output.txt", "w")

#robot = _DummyBot()
robot = RileyRoverBase()

env = RileyRoverGridEnv(robot=robot, count_visits=True, wait_every_step=True)
#env = Kraz3GridEnv(robot=robot, count_visits=True, wait_every_step=True, reward_option='goal', initial_state=(0,0,0))
agent1 = DynaQPlusAgent(planning_steps=10, kappa=0.0)

rand.seed(23)
NUM_EPISODES = 4

robot.speaker.beep()
agent1.start_train(env)

for epi in range(NUM_EPISODES):
    terminal = False
    print("Episode #", epi)
    
    while not terminal:
        a, r, s, terminal = agent1.step_train()
        print("STEP: action =", a, "/ state =", s)
        #time.sleep(1.5)

print(env.visits)
print(env.get_visits_with_nonnegative_pos())
print(agent1.train_step)

if OUTPUT_TO_FILE:
    sys.stdout.close()
