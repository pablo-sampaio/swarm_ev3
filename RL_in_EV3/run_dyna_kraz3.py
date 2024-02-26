#!/usr/bin/env python3
import random as rand
import sys
import time

from ev3dev.ev3 import PowerSupply

# para rodar em PC, descomente aqui
#import sys
#from os import path
#sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) + "/Common" )
#sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) + "/Common_RL" )

from RL.agents import DynaQPlusAgent, DynaQPlusAgentExperimental
from BotHardware import Kraz3Base
from ev3_environments import Kraz3GridEnv, _SimulatedBot

SIMULATED = False
OUTPUT_TO_FILE = False

# epsilon decay function -- not used
#MIN_EPSILON  =  0.0
#DECAY_PERIOD = 20.0
#def epsilon_decay(train_step):
#    return max((DECAY_PERIOD - train_step) / DECAY_PERIOD, MIN_EPSILON)


if __name__ == "__main__":
    if not SIMULATED:
        power = PowerSupply()

    # works when running from Ctrl+F5 in VS Code, or running from
    # command line, but doesn't work when it is run from the brick interface
    if OUTPUT_TO_FILE:
        sys.stdout = open("output.txt", "w")

    if SIMULATED:
        robot = _SimulatedBot()
    else:
        robot = Kraz3Base()

    env = Kraz3GridEnv(robot=robot, count_visits=True, wait_every_step=True, reward_option='goal', initial_state=(0,0,0))
    
    #agent1 = DynaQPlusAgent(alpha=0.2, epsilon=1.0, planning_steps=15, kappa=0.0)
    agent1 = DynaQPlusAgentExperimental(epsilon=0.05, planning_steps=15, kappa=0.0, 
                                        model_option='transition+', reverse_actions=True, 
                                        initial_policy='state-action-count', epsilon_decay_fn=None)

    rand.seed(28)
    NUM_EPISODES = 6

    robot.speaker.beep()
    robot.celebrate()

    agent1.start_train(env)
    robot.speaker.speak("Starting!")

    for epi in range(NUM_EPISODES):
        terminal = False
        epi_steps = 0
        print("Episode #", epi)

        if SIMULATED:
            voltage = 10.0
        else:
            voltage = power.measured_voltage / 10e5  # voltage in V
        
        if voltage < 7.4:
            robot.speaker.beep()
            print("Low battery! Please recharge the battery!")
            robot.speaker.speak("Low battery! Please recharge the battery!")
            time.sleep(3)
            #robot.speaker.speak("Shutting down! Bye, bye...")
            #time.sleep(3)
            #robot.speaker.beep()
            #os.system("shutdown -h now") # doesn't work -- requires sudo
        
        while not terminal:
            a, r, s, terminal = agent1.step_train()
            print(" - STEP", epi_steps,": action =", a, "/ state =", s)
            epi_steps += 1
        
        print(" - TOTAL DE PASSOS:", epi_steps)

    print(env.visits)
    print(env.get_visits_with_nonnegative_pos())
    print(agent1.train_step)

    if OUTPUT_TO_FILE:
        sys.stdout.close()
