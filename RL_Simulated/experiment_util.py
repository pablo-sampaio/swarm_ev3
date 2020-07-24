
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
import random as rand

import numpy as np
from time import sleep


RESULTS_DIR = ''

def set_results_dir(relative_path):
    if relative_path[-1] != '/':
        relative_path = relative_path + '/'
    global RESULTS_DIR
    RESULTS_DIR = relative_path
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print(RESULTS_DIR)

plt.rcParams.update({'font.size': 15})
plt.rcParams.update({'figure.figsize': [8,5]})


# antigo run_experiment
def run_episodes(EnvClass, AgentClass, env_parameters, agent_parameters, exp_parameters,
                    agent_param_to_variate, result_file_name):
    # Experiment settings
    num_runs = exp_parameters['num_runs']
    num_episodes = exp_parameters['num_episodes']
    list_of_param_values = agent_parameters[agent_param_to_variate]
              
    agent_info = dict(agent_parameters) # creates a copy

    # for collecting metrics that shall be plotted later
    all_averages = np.zeros((len(list_of_param_values), num_runs, num_episodes))  
    log_data = {'agent_param' : agent_param_to_variate, 'agent_param_values' : list_of_param_values}

    for param_i, param_value in enumerate(list_of_param_values):
        print("WITH", agent_param_to_variate, '=', param_value)
        sleep(0.3)  # to prevent tqdm printing out-of-order before the above print()
        
        agent_info[agent_param_to_variate] = param_value

        for run_i in tqdm(range(num_runs)):
            rand.seed(run_i)

            env = EnvClass(**env_parameters)
            agent = AgentClass(**agent_info)

            agent.start_train(env)
            for ep_i in range(num_episodes):
                is_terminal = False
                num_steps = 0
                while not is_terminal:
                    _, _, _, is_terminal = agent.step_train()
                    num_steps += 1
                all_averages[param_i][run_i][ep_i] = num_steps

    log_data['all_averages'] = all_averages
    np.save(RESULTS_DIR + result_file_name, log_data)
    

def plot_steps_per_episode(file_path):
    data = np.load(RESULTS_DIR + file_path, allow_pickle=True).item()
    all_averages = data['all_averages']
    param_name = data['agent_param']
    param_values = data['agent_param_values']

    all_averages = np.mean(all_averages, axis=1)
    for i, value in enumerate(param_values):
        plt.plot(all_averages[i], label=param_name+' = '+str(value))

    plt.legend(loc='upper right')
    plt.xlabel('Episodes')
    plt.ylabel('Steps\nper\nepisode', rotation=0, labelpad=40)
    plt.axhline(y=16, linestyle='--', color='grey', alpha=0.4)
    plt.show()


# represents as an int, using only the position (discards the direction)
def state_to_int(env, state):
    row, col, d = state
    assert row >= 0 and col >= 0
    return row * len(env.map[0]) + col


# env_changer allows to change the environment at step
def run_num_steps(EnvClass, AgentClass, 
        env_parameters, agent_parameters, exp_parameters, 
        agent_param_to_variate, result_file_name):
    # read experiment settings
    num_runs = exp_parameters['num_runs']
    num_max_steps = exp_parameters['num_max_steps']
    count_visits = exp_parameters.get('count_visits', False)
    step_to_change_env = exp_parameters.get('change_at_n', -1)
    env_changer_proc =  exp_parameters.get('env_changer_procedure', None)

    list_of_param_values = agent_parameters[agent_param_to_variate]

    agent_info = dict(agent_parameters)

    env = EnvClass()
    num_positions = len(env.map) * len(env.map[0])

    if count_visits:
        # To keep the number of visitations per state
        state_visits_before_change = np.zeros((len(list_of_param_values), num_runs, num_positions))  
        state_visits_after_change = np.zeros((len(list_of_param_values), num_runs, num_positions)) 
    
    # Metrics to evaluate the agents
    cum_reward_all = np.zeros((len(list_of_param_values), num_runs, num_max_steps))
    finished_episodes = np.zeros((len(list_of_param_values), num_runs, num_max_steps))

    log_data = {
        'agent_param' : agent_param_to_variate, 
        'agent_param_values' : list_of_param_values,
        'change_at_n' : step_to_change_env }

    for idx, param_value in enumerate(list_of_param_values):
        print("WITH", agent_param_to_variate, '=', param_value)
        sleep(0.3)
        
        agent_info[agent_param_to_variate] = param_value

        for run in tqdm(range(num_runs)):
            rand.seed(run)

            # instantiate environment and agent
            env = EnvClass(**env_parameters)
            agent = AgentClass(**agent_info)

            agent.start_train(env)
            num_steps = 0
            cum_reward = 0
            finished_eps = 0

            # the condition on "num_steps" here must be the same as in the inner loop
            # removing "-1" only here causes infinite loop
            while num_steps < num_max_steps-1 :
                # this is the initial state of an episode (not returned by train_step)
                state = state_to_int(env, agent.state)

                if count_visits:
                    if num_steps < step_to_change_env: 
                        state_visits_before_change[idx][run][state] += 1
                    else:
                        state_visits_after_change[idx][run][state] += 1

                is_terminal = False
                while not is_terminal and num_steps < num_max_steps-1 :
                    a, r, state, is_terminal = agent.step_train()
                    
                    state = state_to_int(env, state)
                    num_steps += 1
                    # change the environment
                    if num_steps == step_to_change_env:
                        env_changer_proc(agent.env)
                    
                    cum_reward += r
                    cum_reward_all[idx][run][num_steps] = cum_reward
                    finished_eps += 1 if is_terminal else 0
                    finished_episodes[idx][run][num_steps] = finished_eps

                    if count_visits:
                        if num_steps < step_to_change_env:
                            state_visits_before_change[idx][run][state] += 1
                        else:
                            state_visits_after_change[idx][run][state] += 1
                    
                    if is_terminal:
                        # reset is done automatically in "step()", but we did it explicitly here to be able 
                        # to read "agent.state" at the start of the outer loop
                        agent.reset_env()

    if count_visits:
        log_data['state_visits_before'] = state_visits_before_change
        log_data['state_visits_after'] = state_visits_after_change
    log_data['cum_reward_all'] = cum_reward_all
    log_data['finished_episodes'] = finished_episodes
    
    global RESULTS_DIR
    np.save(RESULTS_DIR + result_file_name, log_data)


def plot_results_per_step(file_path, title, performance_metric, y_label):
    data_all = np.load(RESULTS_DIR + file_path, allow_pickle=True).item()
    data_y_all = data_all[performance_metric]
    agent_param = data_all['agent_param']
    ag_param_values = data_all['agent_param_values']
    vert_line_pos = data_all['change_at_n']

    for i, value in enumerate(ag_param_values):
        plt.plot(np.mean(data_y_all[i], axis=0), label=f"{agent_param} = {value}")

    if vert_line_pos != -1:
        plt.axvline(x=vert_line_pos, linestyle='--', color='grey', alpha=0.4)
    plt.xlabel('Timesteps')
    plt.ylabel(y_label, rotation=0, labelpad=60)
    plt.legend(loc='upper left')
    plt.title(title)
    plt.show()


def plot_state_visitations(file_path, plot_titles, idx, shape_env):
    data = np.load(RESULTS_DIR + file_path, allow_pickle=True).item()
    data_keys = ["state_visits_before", "state_visits_after"]
    positions = [211,212]
    titles = plot_titles
    wall_ends = [None,-1]

    for i, key in enumerate(data_keys):
        state_visits = data[key][idx]
        average_state_visits = np.mean(state_visits, axis=0)
        grid_state_visits = np.rot90(average_state_visits.reshape(shape_env).T)
        #grid_state_visits[2,1:wall_ends[i]] = np.nan # walls
        #print(average_state_visits.reshape((6,9)))
        plt.subplot(positions[i])
        plt.pcolormesh(grid_state_visits, edgecolors='gray', linewidth=1, cmap='viridis')
        plt.text(3+0.5, 0+0.5, 'S', horizontalalignment='center', verticalalignment='center')
        plt.text(6+0.5, 4+0.5, 'G', horizontalalignment='center', verticalalignment='center')
        plt.title(titles[i])
        plt.axis('off')
        cm = plt.get_cmap()
        cm.set_bad('gray')

    plt.subplots_adjust(bottom=0.0, right=0.7, top=1.0)
    cax = plt.axes([1., 0.0, 0.075, 1.])
    cbar = plt.colorbar(cax=cax)
    plt.show()


def plot_results_comparison(file_name_dynaq, file_name_dynaqplus, dq_plus_plan_steps,
        performance_metric='cum_reward_all', ylabel='Cumulative\nreward'):
    # gets and plots the results of DynaQ with 50 steps
    dynaq = np.load(RESULTS_DIR + file_name_dynaq, allow_pickle=True).item()
    assert dynaq['agent_param'] == 'planning_steps', "Wrong results file given for Dyna-Q?"
    dynaq_steps = dynaq['agent_param_values'][-1] # last number of planning steps used
    dynaq_performance = dynaq[performance_metric][-1]  # last one Dyna-Q tested
    
    plt.plot(np.mean(dynaq_performance, axis=0), label=f'Dyna-Q ({dynaq_steps} steps)')
    
    # gets and plots the results of DynaQ+ with the given steps
    dynaq_plus = np.load(RESULTS_DIR + file_name_dynaqplus, allow_pickle=True).item()

    vertical_line_pos = dynaq['change_at_n']
    assert dynaq['change_at_n'] == dynaq_plus['change_at_n'], "Unexpected -- environments changed at different times"

    for i, k in enumerate(dq_plus_plan_steps):
        dynaq_plus_perf = dynaq_plus[performance_metric][i]
        plt.plot(np.mean(dynaq_plus_perf, axis=0), label=f'Dyna-Q+ ({k} steps)')

    plt.axvline(x=vertical_line_pos, linestyle='--', color='grey', alpha=0.4)
    plt.xlabel('Timesteps')
    plt.ylabel(ylabel, rotation=0, labelpad=60)
    plt.legend(loc='upper left')
    plt.title('Average performance of Dyna-Q and Dyna-Q+ agents in the Dynamic Env\n')
    plt.show()
