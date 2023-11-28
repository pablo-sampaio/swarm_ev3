#!/usr/bin/env python3
import random as rand
import sys
import os
import time

from ev3dev.ev3 import PowerSupply

# para rodar em PC, descomente
#import sys
#from os import path
#sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) + "/Common" )

from RL.agents import DynaQPlusAgentExtended, DynaQPlusAgentExperimental
from BotHardware import Kraz3Base
from ev3_environments import Kraz3GridEnv, _SimulatedBot

power = PowerSupply()

def epsilon_decay(train_step):
    return max((50 - train_step) / 50.0, 0.1)


if __name__ == "__main__":
    # works when running from Ctrl+F5 in VS Code, or running from
    # command line, but doesn't work when it is run from the brick interface
    OUTPUT_TO_FILE = False
    if OUTPUT_TO_FILE:
        sys.stdout = open("output.txt", "w")

    #robot = _SimulatedBot()
    robot = Kraz3Base()

    env = Kraz3GridEnv(robot=robot, count_visits=True, wait_every_step=True, reward_option='goal', initial_state=(0,0,0))
    #agent1 = DynaQPlusAgentExtended(alpha=0.2, epsilon=1.0, planning_steps=15, kappa=0.0, epsilon_decay_fn=epsilon_decay)
    agent1 = DynaQPlusAgentExperimental(planning_steps=15, kappa=0.0, model_option='all', reverse_actions=True, initial_policy='state-action-count')

    rand.seed(28)
    NUM_EPISODES = 5

    robot.speaker.beep()
    robot.celebrate()

    agent1.start_train(env)
    robot.speaker.speak("Starting!")

    for epi in range(NUM_EPISODES):
        terminal = False
        epi_steps = 0
        print("Episode #", epi)

        voltage = power.measured_voltage / 10e5  # voltage in V
        if voltage < 7.5:
            robot.speaker.beep()
            print("Low battery! Please recharge the battery!")
            robot.speaker.speak("Low battery! Please recharge the battery!")
            time.sleep(3)
            #robot.speaker.speak("Shutting down! Bye, bye...")
            #time.sleep(3)
            robot.speaker.beep()
            #os.system("shutdown -h now")
        
        while not terminal:
            a, r, s, terminal = agent1.step_train()
            print(" - STEP", epi_steps,": action =", a, "/ state =", s)
            epi_steps += 1
            #time.sleep(1.5)
        
        print(" - TOTAL DE PASSOS:", epi_steps)

    print(env.visits)
    print(env.get_visits_with_nonnegative_pos())
    print(agent1.train_step)

    if OUTPUT_TO_FILE:
        sys.stdout.close()
