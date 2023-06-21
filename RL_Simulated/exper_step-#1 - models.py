
from experiment_util import *

from RL.agents import DynaQPlusAgentExperimental
from RL.environments import SimulatedEnv


def change_environment(env):
    env.map[2][-1] = 0  # opens another corridor on the other end of row 2

#env = SimulatedEnv()
#shape_env = (len(env.map), len(env.map[0]))
#change_environment(env)
#print(env.map)

set_results_dir("results-stepcost") # from experiment_util


# Experiment parameters
experiment_parameters = {
    "num_runs" : 30,             # The number of times we run the experiment
    "num_episodes" : 40,         # The number of episodes per experiment
    "num_max_steps" : 10000,
    "change_at_n" : 4000,                         # Time step where the environment will change
    "env_changer_procedure" : change_environment  # Procedure to change the environment 
}

# Environment parameters 
env_parameters = {
    "count_visits" : False,
    "use_real_state" : True,
    "reward_option" : 'step_cost', 
    "allow_all_actions" : False
}

# Agent parameters
agent_parameters = { 
    "gamma": 0.95,
    "epsilon": 0.1, 
    "alpha" : 0.85,
    "planning_steps" : 50,
    "kappa" : 0.007,   # Dyna-Q+
    "model_option" : ['transition', 'transition+', 'optimistic_transition+', 'all'],
    "default_q" : 0.0,
}

results_filename1 = os.path.basename(__file__) + "-epi.npy"
results_filename2 = os.path.basename(__file__) + "-steps.npy"

#'''
run_episodes(SimulatedEnv, DynaQPlusAgentExperimental, 
    env_parameters, agent_parameters, experiment_parameters,
    'model_option', 
    results_filename1)

print(results_filename1, "saved.")


run_num_steps(SimulatedEnv, DynaQPlusAgentExperimental,
    env_parameters, agent_parameters, experiment_parameters,
    'model_option', 
    results_filename2)

print(results_filename2, 'saved.')
#'''

plot_steps_per_episode(results_filename1)
plot_results_per_step(results_filename2, 'Different model options', 'finished_episodes')
