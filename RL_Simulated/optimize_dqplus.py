
import numpy as np
import time
import optuna

import random as rand
from RL.environments import SimulatedEnv
from RL.agents import DynaQPlusAgent

from util import play_episodes

# FIXED PARAMETERS OF THE ENVIRONMENT/AGENT 
REWARD_OPTION = 'step_cost'
DYNAMIC_ENV = False
USE_KAPPA = False   # if True, it is Dyna-Q+; else, it is Dyna-Q

# used only in static experiments
ENV = SimulatedEnv(reward_option=REWARD_OPTION, allow_all_actions=False)

def train_static_env(trial):
    plan_steps = trial.suggest_int('planning_steps', 5, 80)
    alpha = trial.suggest_uniform('alpha', 0.1, 0.9)
    if USE_KAPPA:
        kappa = trial.suggest_uniform('kappa', 1e-10, 0.01) 
    else:
        kappa = 0.0
    model_update = trial.suggest_categorical('model_update', ['transition', 'transition+', 'optimistic_transition+']) # 'all' was not considered -- requires too much previous knowledge

    agent = DynaQPlusAgent(alpha=alpha, planning_steps=plan_steps, kappa=kappa, model_option=model_update)

    print()
    print(f"TRIAL (sta): plan_steps={plan_steps}, alpha={alpha}, kappa={kappa}, model_option={model_update}")

    # Train model
    time_sum = 0.0
    for i in range(3):
        rand.seed(10+i)
        agent.full_train(ENV, max_episodes=20, max_steps=7000)
        time_sum += agent.train_step 

    # metric to be minimized: number of timesteps to train 20 episodes
    return time_sum


def change_environment(env):
    env.map[2][-1] = 0  # opens another corridor on the other end of the row

def train_dynamic_env(trial):
    plan_steps = trial.suggest_int('planning_steps', 5, 80)
    alpha = trial.suggest_uniform('alpha', 0.1, 0.9)
    if USE_KAPPA:
        kappa = trial.suggest_uniform('kappa', 1e-10, 0.01) 
    else:
        kappa = 0.0
    model_update = trial.suggest_categorical('model_option', ['transition', 'transition+', 'optimistic_transition+'])  # 'all' not considered (see comment above)

    agent = DynaQPlusAgent(alpha=alpha, planning_steps=plan_steps, kappa=kappa, model_option=model_update)

    print()
    print(f"TRIAL (dyn): plan_steps={plan_steps}, alpha={alpha}, kappa={kappa}, model_option={model_update}")

    MAX_STEPS = 6000
    CHANGE_AT = 3500  # time to change environment

    # Train model
    cum_reward = 0.0
    episodes = 0
    for run in range(1):
        rand.seed(run + 10)

        env = SimulatedEnv(reward_option=REWARD_OPTION, allow_all_actions=False)
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
                if is_terminal:
                    episodes += 1

    #return -cum_reward   # maximize cumulative reward
    return -episodes     # maximize number of finished episodes


if __name__ == '__main__':
    if DYNAMIC_ENV:
        study = optuna.create_study(storage='sqlite:///optimize_dqplus.db', study_name='dynamic_'+REWARD_OPTION+'_k_'+str(USE_KAPPA), load_if_exists=True)
        study.optimize(train_dynamic_env, n_trials=100)
    else:    
        study = optuna.create_study(storage='sqlite:///optimize_dqplus.db', study_name='static_'+REWARD_OPTION+'_'+str(USE_KAPPA), load_if_exists=True)
        study.optimize(train_static_env, n_trials=100)

    print("FINISHED results for", 
        "DynaQ-PLUS" if USE_KAPPA else "Dyna-Q",
        "dynamic" if DYNAMIC_ENV else "static", "environment", 
        "with reward option", REWARD_OPTION)

    '''
    DYNA-Q STEP_COST / ESTATICO:
    Current best value is 2420.0 with parameters: 
    {'alpha': 0.8596454428029752, 'model_update': 'transition', 'planning_steps': 70}.
    FINISHED results for Dyna-Q static environment with reward option step_cost

    DYNA-Q-PLUS STEP_COST / ESTATICO:
    Current best value is 2397.0 with parameters: 
    {'alpha': 0.837684237749518, 'kappa': 0.004700042668218965, 'model_update': 'transition', 'planning_steps': 68}.
    FINISHED results for static environment with reward option step_cost

    DYNA-Q-PLUS STEP_COST / DINAMICO:
    Current best value is -388.0 with parameters: 
    {'alpha': 0.899265696824145, 'kappa': 0.007269805815171486, 'model_option': 'transition', 'planning_steps': 77}.
    FINISHED results for dynamic environment with reward option step_cost
    '''
