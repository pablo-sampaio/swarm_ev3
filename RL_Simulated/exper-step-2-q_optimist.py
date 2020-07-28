
from experiment_util import *
import experiment_util

import sys

#sys.path.append("../Common")
from RL.agents import DynaQPlusAgentExperimental
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
    "num_runs" : 30,             # The number of times we run the experiment
    "num_episodes" : 40,         # The number of episodes per experiment
    "num_max_steps" : 5000
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
    "alpha" : 0.85,
    "planning_steps" : 50,
    "kappa" : 0.0,                      # To behave as Dyna-Q
    "model_option" : 'transition',
    "default_q" : [-1.0, 0.0, 1.0]      # List of values to test -- ALL are optimistic values
}

results_filename1 = os.path.basename(__file__) + "-epi.npy"
results_filename2 = os.path.basename(__file__) + "-steps.npy"

'''
run_episodes(SimulatedEnv, DynaQPlusAgentExperimental, 
    env_parameters, agent_parameters, experiment_parameters,
    'default_q', 
    results_filename1)

print(results_filename1, "saved.")
#'''

'''
run_num_steps(SimulatedEnv, DynaQPlusAgentExperimental,
    env_parameters, agent_parameters, experiment_parameters,
    'default_q', 
    results_filename2)

print(results_filename2, 'saved.')
#'''

plot_steps_per_episode(results_filename1)
plot_results_per_step(results_filename2, 'Varied initial Q-values', 'finished_episodes')
