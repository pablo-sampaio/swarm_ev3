
from experiment_util import *
import experiment_util

import sys

#sys.path.append("../Common")
from RL.agents import DynaQPlusAgent
from RL.environments import SimulatedEnv

def change_environment(env):
    env.map[2][-1] = 0  # opens another corridor on the other end of row 2

env = SimulatedEnv()
shape_env = (len(env.map), len(env.map[0]))
#change_environment(env)
#print(env.map)

set_results_dir("results-stepcost") # from experiment_util


# Experiment parameters
experiment_parameters = {
    "num_runs" : 50,         # Number of times we run the experiment
    "num_episodes" : 40,     # Number of episodes per experiment
}

# Environment parameters 
env_parameters = {
    "count_visits" : False,
    "reward_option" : 'step_cost', 
    "allow_all_actions" : False
}

# Agent parameters
agent_parameters = {  
    "gamma": 0.95,
    "epsilon": 0.1, 
    "alpha" : 0.85,                   # Best value return by Optuna: 0.85
    "planning_steps" : [0, 5, 50],    # The list of planning_steps we want to try
    "kappa" : 0.0,                    # To behave as Dyna-Q
    "model_option" : 'transition',
    "default_q" : 0.0,
}

results_filename = os.path.basename(__file__) + ".npy"

run_episodes(SimulatedEnv, DynaQPlusAgent, 
    env_parameters, agent_parameters, experiment_parameters,
    'planning_steps', 
    results_filename)

print(results_filename, "saved.")

plot_steps_per_episode(results_filename)
