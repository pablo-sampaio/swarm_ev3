#!/usr/bin/env python3

from RL.agents import DynaQPlusAgent
from BotHardware import Kraz3Base
from ev3_environments import Kraz3GridEnv

import random as rand
import sys

# works when running from Ctrl+F5 in VS Code, or running from
# command line, but doesn't work when it is run from the brick interface
OUTPUT_TO_FILE = False
if OUTPUT_TO_FILE:
    sys.stdout = open("output.txt", "w")

#robot = _DummyBot()
robot = Kraz3Base()

env = Kraz3GridEnv(robot=robot, count_visits=True, wait_every_step=True, reward_option='goal', initial_state=(0,0,0))
agent1 = DynaQPlusAgent(planning_steps=50, kappa=0.0)

rand.seed(28)
NUM_EPISODES = 5

robot.speaker.beep()
robot.celebrate()

agent1.start_train(env)

for epi in range(NUM_EPISODES):
    terminal = False
    epi_steps = 0
    print("Episode #", epi)
    
    while not terminal:
        a, r, s, terminal = agent1.step_train()
        print("STEP: action =", a, "/ state =", s)
        epi_steps += 1
        #time.sleep(1.5)
    
    print(" - TOTAL DE PASSOS:", epi_steps)

print(env.visits)
print(env.get_visits_with_nonnegative_pos())
print(agent1.train_step)

if OUTPUT_TO_FILE:
    sys.stdout.close()
