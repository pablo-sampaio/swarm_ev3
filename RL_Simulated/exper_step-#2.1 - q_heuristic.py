
from experiment_util import *
import experiment_util

import sys

#sys.path.append("../Common")
from RL.agents import DynaQPlusAgentExperimental
from RL.environments import SimulatedEnv

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
    "allow_all_actions" : False,
    "use_real_state" : True,  # required to use heuristics for default_q
}

# Agent parameters
agent_parameters = {  
    "gamma": 0.95,
    "epsilon": 0.1, 
    "alpha" : 0.85,
    "planning_steps" : 50,
    "kappa" : 0.0,                      # To behave as Dyna-Q
    "model_option" : 'transition',
    "reverse_actions" : False,
    "default_q" : [0.0, 'goal_dist', 'tentative_goal_dist'],
}

results_filename1 = os.path.basename(__file__) + "-epi.npy"
results_filename2 = os.path.basename(__file__) + "-steps.npy"

#'''
run_episodes(SimulatedEnv, DynaQPlusAgentExperimental, 
    env_parameters, agent_parameters, experiment_parameters,
    'default_q', 
    results_filename1)

print(results_filename1, "saved.")
#'''

#'''
run_num_steps(SimulatedEnv, DynaQPlusAgentExperimental,
    env_parameters, agent_parameters, experiment_parameters,
    'default_q', 
    results_filename2)

print(results_filename2, 'saved.')
#'''

plot_steps_per_episode(results_filename1)
plot_results_per_step(results_filename2, 'Varied initial Q-values', 'finished_episodes')
