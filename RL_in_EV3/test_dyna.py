#!/usr/bin/env python3

from RL.environments import Ev3GridEnv
from RL.agents import DynaQPlusAgent

from BotHardware import EducatorBot


robot = EducatorBot()

env = Ev3GridEnv(robot=robot, count_visits=True)
agent1 = DynaQPlusAgent(planning_steps=2, kappa=0.0)

agent1.full_train(env, max_episodes=1)
print(env.visits)
print(env.non_negative_positions_visits())
print(agent1.train_step)

