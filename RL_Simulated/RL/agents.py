
import math
import random as rand

from enum import Enum, unique
from itertools import product

from RL.environments import Action, Direction


class TabularQ(object):
    def __init__(self, actionset):
        self.q = {}  # dictionary for pairs (s,a)
        self.all_actions = actionset

    def set(self, s, a, value):
        self.q[(s,a)] = value

    def value(self, s, a):
        return self.q.get((s,a), 0.0)
    
    def argmax(self, s, actions_in_s=None, default_q=0.0):
        if actions_in_s is None:
            actions_in_s = self.all_actions        
        ties = []
        max_q = float("-inf")
        for a in actions_in_s:
            curr_q = self.q.get((s,a), default_q)
            if curr_q > max_q:
                max_q = curr_q
                ties = [a]
            elif curr_q == max_q:
                ties.append(a)
        return rand.choice(ties), max_q
    
    def max(self, s, actions_in_s=None, default_q=0.0):
        if actions_in_s is None:
            actions_in_s = self.all_actions        
        top = float("-inf")
        for a in actions_in_s:
            curr_q = self.q.get((s,a), default_q)
            if curr_q > top:
                top = curr_q
        return top


class DynaQPlusAgent(object):

    def __init__(self, epsilon=0.1, gamma=0.98, alpha=0.1, planning_steps=5, kappa=0.00001, model_option='state+actions'):
        self.epsilon = epsilon
        self.gamma = gamma
        self.alpha = alpha
        self.planning_steps = planning_steps
        self.kappa = kappa
        self.q = None
        self.model = None
        assert model_option in ['state', 'state+actions', 'state+next_state+actions', 'all']
        self.model_option = model_option
        self.train_step = 0

    def choose_action(self, s):
        return self.q.argmax(s)

    def full_train(self, env, max_steps=None, max_episodes=None):
        assert not (max_steps is None and max_episodes is None), "Must set al least one of max_steps and max_episodes (cannot both be None)"
        if max_episodes is None:
            max_episodes = float("inf")
        if max_steps is None:
            max_steps = float("inf")

        self.start_train(env)
        while self.epi_finished < max_episodes and self.train_step < max_steps:
            self.step_train()

    def start_train(self, env):
        self.env = env
        self.all_actions = env.all_actions()
        self.q = TabularQ(self.all_actions)
        self.model = dict({})  # keys are pairs (s,a)

        if self.model_option == 'all':
            for s_a in product(env.states(), list(Action)):
                self.model[s_a] = (0.0, s_a[0], False, 0)

        self.state = None
        self.train_step = 0
        self.epi_step = 0
        self.epi_finished = 0  # number of episodes finished
        return self.state

    # it is optional to call this method
    # useful only if you want to know each start state
    def reset_env(self):
        assert self.state == None, "Episode not finished"
        self.state = self.env.reset()
        return self.state

    def step_train(self):
        if self.state == None:
            self.state = self.env.reset()

        # select and apply action
        if rand.random() < self.epsilon:
            action = rand.choice(self.all_actions)
        else:
            action, _ = self.q.argmax(self.state)

        new_state, reward, terminal = self.env.apply_action(action)
        self.train_step += 1
        self.epi_step += 1

        # update Q, by direct RL
        if terminal:
            target_q = reward
        else:
            target_q = reward + self.gamma * self.q.max(new_state)
        q_state_action = self.q.value(self.state, action)
        q_state_action += self.alpha * (target_q - q_state_action)
        self.q.set(self.state, action, q_state_action)
        
        # update model
        self.update_model(self.state, action, reward, new_state, terminal)

        # update Q by planning (indirect RL)
        self.planning(self.train_step)
        
        result = (action, reward, new_state, terminal)
        self.state = new_state

        if terminal:
            self.state = None
            self.epi_step = 0
            self.epi_finished += 1
        
        return result

    def update_model(self, state, action, reward, new_state, terminal):
        if self.model_option == 'state' or self.model_option == 'all':
            self.model[(state,action)] = (reward, new_state, terminal, self.train_step)
        
        elif self.model_option == 'state+actions':
            if (state, action) not in self.model: # se nao tiver uma acao, nao tem nenhuma
                for a in self.all_actions:
                    if a != action:
                        self.model[(state,a)] = (0, state, False, self.train_step)
            self.model[(state,action)] = (reward, new_state, terminal, self.train_step)
        
        elif self.model_option == 'state+next_state+actions':
            if (state, action) not in self.model: # se nao tiver uma acao, nao tem nenhuma
                for a in self.all_actions:
                    if a != action:
                        self.model[(state,a)] = (0, state, False, self.train_step)
            self.model[(state,action)] = (reward, new_state, terminal, self.train_step)
            if not terminal:
                for a in self.all_actions:
                    if (new_state, a) in self.model: # se tiver uma acao, tem todas
                        break
                    self.model[(new_state,a)] = (0, new_state, False, self.train_step)
        
        else:
            raise Exception("Invalid option for model update: " + self.model_option)

    def planning(self, curr_timestep):
        # different implementations for random steps:
        # 1 - using samples() with the minimum of model entries and planning steps: 50 steps worse than 5 or 10
        # 2 - using only choices(): 10 steps worse than 5
        # 3 - using choices() when entries < planning steps, and samples() otherwise: good
        set_s_a = self.model.keys()
        if len(set_s_a) < self.planning_steps:
            samples = rand.choices(list(set_s_a), k=self.planning_steps)
        else:
            samples = rand.sample(set_s_a, k=self.planning_steps)
        for s, a in samples:
            r, next_s, arrived, t = self.model[(s,a)]
            r += self.kappa * math.sqrt(curr_timestep - t)
            if arrived:
                target_q = r
            else:
                target_q = r + self.gamma * self.q.max(next_s) 
            q_s_a = self.q.value(s, a)
            q_s_a += self.alpha * (target_q - q_s_a)
            self.q.set(s, a, q_s_a)


class LRTAStarAgent:

    def __init__(self, **kwargs):
        self.values = {}
    
    def choose_action(self, s):
        return self.h.argmax(s)

    def start_train(self, env):
        self.env = env
        self.all_actions = env.all_actions()
        self.h = TabularQ(self.all_actions)

        self.state = None
        self.train_step = 0
        self.epi_step = 0
        self.epi_finished = 0
        return self.state

    # it is optional to call this method
    # useful only if you want to know each start state
    def reset_env(self):
        assert self.state == None, "Episode not finished"
        self.state = self.env.reset()
        return self.state

    def step_train(self):
        if self.state is None:
            self.state = self.env.reset()

        action, _ = self.h.argmax(self.state)

        new_state, reward, terminal = self.env.apply_action(action)
        self.train_step += 1
        self.epi_step += 1

        # updates the heuristic
        if terminal:
            new_h = reward 
        else:
            new_h = reward + self.h.max(new_state) 
        self.h.set(self.state, action, new_h)

        result = (action, reward, new_state, terminal)
        self.state = new_state

        if terminal:
            new_state = self.env.reset()
            self.epi_step = 0
            self.epi_finished += 1
            self.state = None
        
        return result

    def full_train(self, env, max_steps=None, max_episodes=None):
        assert not (max_steps is None and max_episodes is None), "Must set al least one of max_steps and max_episodes (cannot both be None)"
        if max_episodes is None:
            max_episodes = float("inf")
        if max_steps is None:
            max_steps = float("inf")

        self.start_train(env)
        while self.epi_finished < max_episodes and self.train_step < max_steps:
            self.step_train()

