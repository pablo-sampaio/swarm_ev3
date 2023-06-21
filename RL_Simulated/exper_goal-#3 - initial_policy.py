'''
This file runs experimentos with different "initial policies" for the agent using the "goal" reward option. 
The initial policy is a policy used only in the first episode.

The options we tested were:
- epsilon-greedy: use the default policy of the agent
- cell-count: the agents counts the number of visits to each cell of the map and chooses the cell with minimun number of visits
- state-count: similar to the above, but it counts the state
- state-action-count: similar to the above, but it counts the pairs (state,action)
'''

from experiment_util import *

from RL.agents import DynaQPlusAgentExperimental
from RL.environments import SimulatedEnv

set_results_dir("results-goal") # from experiment_util


# Experiment parameters
experiment_parameters = {
    "num_runs" : 30,            # Number of times we run the experiment
    "num_episodes" : 20,        # Number of episodes per experiment (for run_episodes())
    "num_max_steps" : 5000      # Number of steps (for run_num_steps())
}

# Environment parameters 
env_parameters = {
    "count_visits" : False,
    "reward_option" : 'goal', 
    "allow_all_actions" : False,
    "use_real_state" : True,
}

# Agent parameters
agent_parameters = {  
    "gamma": 0.95,
    "epsilon": 0.1, 
    "alpha" : 0.2,
    "planning_steps" : 70,
    "kappa" : 0.0,
    "model_option" : 'transition+',
    "default_q" : 0.0,  # better than 1.0 here !
    "initial_policy" : ['e-greedy', 'cell-count', 'state-count', 'state-action-count']
}

results_filename1 = os.path.basename(__file__) + "-epi.npy"
results_filename2 = os.path.basename(__file__) + "-steps.npy"

#'''
run_episodes(SimulatedEnv, DynaQPlusAgentExperimental, 
    env_parameters, agent_parameters, experiment_parameters,
    'initial_policy', 
    results_filename1)

print(results_filename1, "saved.")


run_num_steps(SimulatedEnv, DynaQPlusAgentExperimental,
    env_parameters, agent_parameters, experiment_parameters,
    'initial_policy', 
    results_filename2)

print(results_filename2, 'saved.')
#'''

plot_steps_per_episode(results_filename1)
plot_results_per_step(results_filename2, 'Results for initial policies', 'cum_reward_all')
