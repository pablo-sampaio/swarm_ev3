
import math
import random as rand

from enum import Enum, unique
from itertools import product

from RL.environments import Action, Direction

try: 
    rand.choices
except AttributeError:
    def _choices(options, k):
        l = []
        for _ in range(k):
            l.append(rand.choice(options))
        return l
    rand.choices = _choices


'''
A tabular Q that stores values for pairs (s,a) and that can be progressively filled.
Although may seem awkward, this class was designed carefully to behave as expected 
with the DynaQ+, specially because of its use with varying sets of actions in planning. 
Be carefaul if you want to change.
'''
class TabularQ(object):
    def __init__(self):
        self.q = {}  # dictionary for pairs (s,a)
        self.get = self.value  # alternative name

    def set(self, s, a, value):
        assert (s,a) in self.q
        self.q[s,a] = value
    
    def set_all(self, s, actions_in_s, default_value):
        for a in actions_in_s:
            if (s,a) in self.q:  # if it has value for one action from s, it has for all actions
                break
            self.q[s,a] = default_value

    def value(self, s, a):
        return self.q[s,a]
    
    def argmax(self, s, actions_in_s, ignore_missing=False):
        ties = []
        max_q = float("-inf")
        for a in actions_in_s:
            # the ignore missing flag works like an assertion, i.e. to make sure
            # that just in some situations entries can be ignored
            if ignore_missing and (s,a) not in self.q:
                continue  # i.e., don't execute the rest of the loop
            curr_q = self.q[s,a]
            if curr_q > max_q:
                max_q = curr_q
                ties = [a]
            elif curr_q == max_q:
                ties.append(a)
        #assert max_q != float("-inf")  # ok in the tests
        return rand.choice(ties), max_q
    
    def max(self, s, actions_in_s, ignore_missing=False):
        top = float("-inf")
        for a in actions_in_s:
            if ignore_missing and (s,a) not in self.q:
                continue  # i.e., don't execute the rest of the loop
            curr_q = self.q[s,a]
            if curr_q > top:
                top = curr_q
        #assert top != float("-inf")  # ok in the tests
        return top


class DynaQPlusAgent(object):

    def __init__(self, epsilon=0.1, gamma=0.98, alpha=0.1, planning_steps=5, kappa=0.00001, model_option='transition+', default_q=0.0):
        self.epsilon = epsilon
        self.gamma = gamma
        self.alpha = alpha
        self.planning_steps = planning_steps
        self.kappa = kappa
        self.qtable = None
        self.model = None
        assert model_option in ['transition', 'transition+', 'optimistic_transition+', 'all']
        self.model_option = model_option
        self.train_step = 0
        self.default_q = default_q

    def choose_action(self, s):
        return self.qtable.argmax(s)

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
        self.qtable = TabularQ()
        self.model = dict({})  # keys are pairs (state, action)
        
        self.state = self.env.reset()
        self.qtable.set_all(self.state, self.env.valid_actions(), self.default_q)
        self.train_step = 0

        if self.model_option == 'all':
            for s_a in product(env.states(), list(Action)):
                self.model[s_a] = (0.0, s_a[0], False, self.train_step)

        self.epi_step = 0
        self.epi_finished = 0  # number of episodes finished
        return self.state

    # Calling this method to reset the environment is optional.
    # It is useful only if you want to know each start state.
    def reset_env(self):
        assert self.state == None, "Episode not finished"  # it is ok to disable this
        self.state = self.env.reset()
        return self.state

    def step_train(self):
        if self.state == None:
            self.state = self.env.reset()

        # select ction
        actions_in_state = self.env.valid_actions()
        if rand.random() < self.epsilon:
            action = rand.choice(actions_in_state)
        else:
            action, _ = self.qtable.argmax(self.state, actions_in_state)

        # apply action
        new_state, reward, is_terminal = self.env.apply_action(action)
        self.train_step += 1
        self.epi_step += 1

        # update Q, by direct RL
        if is_terminal:
            target_q = reward
        else:
            actions_in_new_state = self.env.valid_actions()
            self.qtable.set_all(new_state, actions_in_new_state, self.default_q) # initializes the q-table for 'new_state'
            target_q = reward + self.gamma * self.qtable.max(new_state, actions_in_new_state)
        
        q_state_action = self.qtable.value(self.state, action)
        q_state_action += self.alpha * (target_q - q_state_action)
        self.qtable.set(self.state, action, q_state_action)
        
        # update model
        self.update_model(self.state, action, reward, new_state, is_terminal, actions_in_state)

        # update Q by planning (indirect RL)
        self.planning(self.train_step)
        
        result = (action, reward, new_state, is_terminal)
        self.state = new_state

        if is_terminal:
            self.state = None
            self.epi_step = 0
            self.epi_finished += 1
        
        return result

    # Observacao: Ideia abandonada - 'transition++' - acrescenta todas as acoes para o new_state na primeira visita (e inicializa com todas do 
    # estado inicial). Acrescenta pouco em relacao ao 'transition+' e o acrescimo nao parece util. Em testes, de fato, o desempenho foi similar.
    def update_model(self, state, action, reward, new_state, is_terminal, actions_in_state=None):
        if actions_in_state is None:
            actions_in_state = self.all_actions

        if self.model_option == 'transition' or self.model_option == 'all':
            # the update is done below this if-elif-else
            pass
        elif self.model_option == 'transition+' or self.model_option == 'optimistic_transition+':
            assumed_r = 0.0 if self.model_option == 'transition+' else 1.0  # optimism: assumes reward 1!
            for a in actions_in_state:
                if (state,a) in self.model: # if it has entry for one action (in state), it has for all
                    break
                if a != action:
                    self.model[state,a] = (assumed_r, state, False, self.train_step)
        else:
            raise Exception("Invalid option for model update: " + self.model_option)
        
        # for all models
        self.model[state,action] = (reward, new_state, is_terminal, self.train_step)
        reverse_action = Action.reverse(action)
        # reverse actions: not very useful in tests
        #if not is_terminal \
        #        and reverse_action is not None \
        #        and (new_state,reverse_action) not in self.model:
        #    self.model[new_state,reverse_action] = (reward, state, False, self.train_step)

    def planning(self, curr_timestep):
        # different implementations for random steps:
        # 1 - using samples() with the minimum of model entries and planning steps: 50 steps worse than 5 or 10
        # 2 - using only choices(): 10 steps was worse than 5 steps
        # 3 - using choices() when entries < planning steps, and samples() otherwise: good
        set_s_a = self.model.keys()
        if len(set_s_a) < self.planning_steps:
            samples = rand.choices(list(set_s_a), k=self.planning_steps)
        else:
            samples = rand.sample(set_s_a, k=self.planning_steps)
        for s, a in samples:
            r, next_s, is_terminal, t = self.model[(s,a)]
            r += self.kappa * math.sqrt(curr_timestep - t)
            if is_terminal:
                target_q = r
            else:
                target_q = r + self.gamma * self.qtable.max(next_s, self.all_actions, ignore_missing=True) 
            q_s_a = self.qtable.value(s, a)
            q_s_a += self.alpha * (target_q - q_s_a)
            self.qtable.set(s, a, q_s_a)


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

