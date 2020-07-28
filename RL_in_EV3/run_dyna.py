#!/usr/bin/env python3

from RL.environments import Ev3GridEnv, _DummyBot
from RL.agents import DynaQPlusAgent

from BotHardware import EducatorBase

import time
import random as rand
import sys

# works when running from Ctrl+F5 in VS Code, or running from
# command line, but doesn't work when run from the brick interface
OUTPUT_TO_FILE = True
if OUTPUT_TO_FILE:
    sys.stdout = open("output.txt", "w")

#robot = _DummyBot()
robot = EducatorBase()

env = Ev3GridEnv(robot=robot, count_visits=True, wait_every_step=True)
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
