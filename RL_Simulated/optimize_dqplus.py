
import numpy as np
import time
import optuna

import random as rand
from RL.environments import SimulatedEnv
from RL.agents import DynaQPlusAgent

from util import play_episodes

# any of these 2 are used only in static experiments
ENV = SimulatedEnv()
#ENV = SimulatedEnv(reward_option='step_cost')

def train_static_env(trial):
    plan_steps = trial.suggest_int('planning_steps', 5, 100)
    alpha = trial.suggest_uniform('alpha', 0.1, 0.9)
    kappa = trial.suggest_uniform('kappa', 1e-10, 0.01) 
    model_update = trial.suggest_categorical('model_update', ['state', 'state+actions', 'state+next_state+actions', 'all'])

    agent = DynaQPlusAgent(alpha=alpha, planning_steps=plan_steps, kappa=kappa, model_option=model_update)

    print()
    print(f"TRIAL: plan_steps={plan_steps}, alpha={alpha}, kappa={kappa}, model_option={model_update}")

    # Train model
    time_sum = 0.0
    for i in range(3):
        rand.seed(10+i)
        agent.full_train(ENV, max_episodes=20, max_steps=7000)
        time_sum += agent.train_step 

    # metric to be minimized: number of timesteps to train 
    return time_sum


def change_environment(env):
    env.map[2][0] = 1   # closes a corridor in the start of a row
    env.map[2][-1] = 0  # opens another one on the other end of the row


def train_dynamic_env(trial):
    plan_steps = trial.suggest_int('planning_steps', 5, 100)
    alpha = trial.suggest_uniform('alpha', 0.1, 0.9)
    kappa = trial.suggest_uniform('kappa', 1e-10, 0.01) 
    model_update = trial.suggest_categorical('model_update', ['state', 'state+actions', 'state+next_state+actions', 'all'])

    agent = DynaQPlusAgent(alpha=alpha, planning_steps=plan_steps, kappa=kappa, model_option=model_update)

    print()
    print(f"TRIAL: plan_steps={plan_steps}, alpha={alpha}, kappa={kappa}, model_option={model_update}")

    MAX_STEPS = 6000
    CHANGE_AT = 3500  # time to change environment

    # Train model
    cum_reward = 0.0
    for run in range(1):
        rand.seed(run + 10)

        env = SimulatedEnv()
        agent.start_train(env)
        num_steps = 0

        while num_steps < MAX_STEPS-1 :
            is_terminal = False
            while not is_terminal and num_steps < MAX_STEPS-1 :
                a, r, state, is_terminal = agent.step_train()                
                num_steps += 1
                cum_reward += r
                # change the environment
                if num_steps == CHANGE_AT:
                    change_environment(agent.env)

    # metric to be maximized: cumulative reward
    return cum_reward


if __name__ == '__main__':
    study = optuna.create_study(storage='sqlite:///sim_env.db', study_name='sim_env', load_if_exists=True)
    study.optimize(train_static_env, n_trials=100)
    
    #study = optuna.create_study(storage='sqlite:///sim_env.db', direction='maximize', study_name='sim_dyn_env_2', load_if_exists=True)
    #study.optimize(train_dynamic_env, n_trials=200)

    #study = optuna.create_study(storage='sqlite:///sim_env.db', study_name='sim_env_stepcost_dynaq_k0', load_if_exists=True)
    #study.optimize(train_static_env, n_trials=100)

    '''
    EXCELENTE RESULTADO ESTATICO (200 trials), mas tambem bom em ambiente dinamico:
    Current best value is 2051.0 with parameters: 
    {'alpha': 0.8715057749268625, 'kappa': 0.0005103567175066837, 'model_update': 'state+next_state+actions', 'planning_steps': 68}.

    RESULTADO DINAMICO (200 trials), mas foi ruim no experimento final:
    Current best value is 331.0 with parameters: 
    {'alpha': 0.6912174835109899, 'kappa': 0.00025776587656380903, 'model_update': 'state+actions', 'planning_steps': 48}.

    ESTÁTICO USANDO step_cost:
    Current best value is 2539.0 with parameters: 
    {'alpha': 0.8990851646314703, 'kappa': 0.008284247329579839, 'model_update': 'state', 'planning_steps': 89}.

    ESTATICO, com step_cost e k=0 (100 trials):
    Current best value is 1891.0 with parameters: 
    {'alpha': 0.6482801021137697, 'model_update': 'state+actions', 'planning_steps': 51}

    '''

    print("FINISHED!")
