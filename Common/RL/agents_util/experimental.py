
import math
import random as rand

#from enum import Enum, unique
from itertools import product

from RL.environments import Action, Direction
#from RL.agents_util.q_table import TabularQExperimental

try: 
    rand.choices
except AttributeError:
    def _choices(options, k):
        l = []
        for _ in range(k):
            l.append(rand.choice(options))
        return l
    rand.choices = _choices


# obs.: imperfect because of obstacles and additional turns that may  
# be required to get to the goal, but it works as an optimistic value
def distance_to_goal(state, goal):
    dist = abs(state[0] - goal[0]) + abs(state[1] - goal[1])
    return dist


class DynaQPlusAgentExperimental(object):
    def __init__(self, epsilon=0.1, gamma=0.98, alpha=0.1, planning_steps=5, kappa=0.00001, 
            model_option='transition', reverse_actions=False, initial_policy='e-greedy', default_q=0.0):
        self.epsilon = epsilon
        self.gamma = gamma
        self.alpha = alpha
        self.planning_steps = planning_steps
        self.kappa = kappa
        self.qtable = None
        self.model = None
        assert model_option in ['transition', 'transition+', 'optimistic_transition+', 'all']
        self.model_option = model_option
        self.reverse_action = reverse_actions
        assert initial_policy in ['e-greedy', 'state-action-count', 'state-count', 'cell-count']
        self.initial_policy = initial_policy
        assert isinstance(default_q, (float, int, str))
        if isinstance(default_q, str):
            assert default_q in ['goal_dist', 'tentative_goal_dist']
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
        self.qtable = TabularQExperimental(env.all_actions())
        self.model = {}  # a dict where keys are pairs (state, action), values are tuples (reward, next state, terminal, train step)

        # a dict where keys are states, values are the collection of valid actions
        # it is also used as a list on values for which the q-table is initialized
        self.model_valid_actions = {}  
        
        self.state = None
        self.train_step = 0
        self.epi_step = 0
        self.epi_finished = 0  # number of finished episodes

        if isinstance(self.default_q, str):
            assert self.env.use_real_state, "To use advanced \'default_q\', the environment must use the real state (not an observation derived from it)"
            assert self.env.reward_option == 'step_cost'
            if self.default_q == 'tentative_goal_dist':
                self.tentative_goal = ( rand.randint(0, len(env.map)), 
                                        rand.randint(0, len(env.map[0])) )

        if self.model_option == 'all':
            for s in env.states():
                q_s = self.get_heuristic_q(s, False)
                self.model_valid_actions[s] = self.all_actions
                self.qtable.initialize_values(s, self.all_actions, q_s)
                for a in self.all_actions:
                    self.model[s,a] = (0.0, s, False, self.train_step)

    # Calling this method to reset the environment is optional.
    # It is useful only if you want to know each start state.
    def reset_env(self):
        assert self.qtable is not None, "Must call start_train() first"
        assert self.state == None, "Episode not finished"  # probably, it is ok to disable this
        self.state = self.env.reset()

        # before training one episode
        if self.epi_finished == 0: 
            self.model_valid_actions[self.state] = self.env.curr_actions()
            q_state = self.get_heuristic_q(self.state, True)
            self.qtable.initialize_values(self.state, self.all_actions, q_state) # assign for all actions
       
            if self.initial_policy == 'e-greedy':
                self.policy = self.e_greedy_policy
            elif self.initial_policy == 'state-action-count':
                self.count = {}
                self.policy = self.state_action_count_policy
            elif self.initial_policy == 'state-count':
                self.count = {}
                self.count[self.state] = 1
                self.policy = self.state_count_policy
            elif self.initial_policy == 'cell-count':
                self.count = {}
                self.count[self.state[0:2]] = 1
                self.policy = self.cell_count_policy
            else:
                raise Exception()
        
        # after training one episode
        elif self.epi_finished == 1: 
            self.policy = self.e_greedy_policy
        
        return self.state

    def e_greedy_policy(self, state, actions_in_state):
        if rand.random() < self.epsilon:
            action = rand.choice(actions_in_state)
        else:
            action, _ = self.qtable.argmax(state, actions_in_state)
        return action

    def step_train(self):
        if self.state == None:
            self.reset_env()

        # select action
        actions_in_state = self.env.curr_actions()
        action = self.policy(self.state, actions_in_state)

        # apply action
        new_state, reward, is_terminal = self.env.apply_action(action)
        self.train_step += 1
        self.epi_step += 1
        
        if self.policy == self.state_count_policy:
            self.count[new_state] = self.count.get(new_state,0) + 1
        elif self.policy == self.cell_count_policy:
            self.count[new_state[0:2]] = self.count.get(new_state[0:2],0) + 1

        # update Q, by direct RL
        if is_terminal:
            actions_in_new_state = []
            target_q = reward
        else:
            actions_in_new_state = self.env.curr_actions()
            # if it is the first time in 'new_state', initializes its value in the q-table
            if new_state not in self.model_valid_actions:
                q_new_state = self.get_heuristic_q(new_state, True)
                self.qtable.initialize_values(new_state, self.all_actions, q_new_state) # initialize for all actions
            target_q = reward + self.gamma * self.qtable.max(new_state, actions_in_new_state)
        
        q_state_action = self.qtable.value(self.state, action)
        q_state_action += self.alpha * (target_q - q_state_action)
        self.qtable.set(self.state, action, q_state_action)
        
        # update model
        self.update_model(self.state, action, reward, new_state, is_terminal, 
                            actions_in_state, actions_in_new_state)

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
    def update_model(self, state, curr_action, reward, new_state, is_terminal, actions_in_state, actions_in_new_state):
        # attention! this code assumes that the environment may be dynamical (i.e., an action 
        # may suddently become available/unavailable, because the cell was un/blocked)

        if self.model_option in ['transition+', 'optimistic_transition+']:
            assumed_r = 0.0 if self.model_option == 'transition+' else 1.0  # optimism: assumes reward 1!
            # add fake transitions
            for a in self.all_actions:
                if a != curr_action and (state,a) not in self.model: 
                    self.model[state,a] = (assumed_r, state, False, self.train_step)
        elif self.model_option not in ['transition', 'all']:
            raise Exception()
        
        # remove invalid actions for state and new_state
        for a in self.all_actions:
            if a not in actions_in_state:
                self.model.pop((state,a), None)
            if a not in actions_in_new_state: 
                self.model.pop((new_state,a), None)
        
        # for all models
        self.model_valid_actions[state] = actions_in_state # always reassign the valid actions, because the environment may change
        self.model_valid_actions[new_state] = actions_in_new_state
        
        self.model[state,curr_action] = (reward, new_state, is_terminal, self.train_step)
        
        if self.reverse_action:
            inv_action = Action.reverse(curr_action)
            if not is_terminal \
                    and inv_action is not None \
                    and (new_state, inv_action) not in self.model:
                self.model[new_state,inv_action] = (reward, state, False, self.train_step)

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
                # the model_valid_actions was created mostly because of its use here, after many buggy trials
                # simpler alternatives: (1) make 'model' with key 's', pointing do another dict with key 'action;
                # (2) simply allow all actions, making inefective the actions not available
                target_q = r + self.gamma * self.qtable.max(next_s, self.model_valid_actions[next_s]) 
            
            q_s_a = self.qtable.value(s, a) # don't need a default value, because the q-table has the values for all actions
            q_s_a += self.alpha * (target_q - q_s_a)
            assert not math.isnan(q_s_a)
            self.qtable.set(s, a, q_s_a)

    def get_heuristic_q(self, state, may_change_tentative):
        if isinstance(self.default_q, (int,float)):
            return self.default_q
        elif isinstance(self.default_q, str) and self.default_q == 'goal_dist':
            dist = distance_to_goal(state, self.env.goal_position)
            dist = (-1)*(1.0 - self.gamma**dist) / (1.0 - self.gamma) # formula for geometric series, assuming each step gives -1 reward
            return dist
        elif isinstance(self.default_q, str) and self.default_q == 'tentative_goal_dist':
            # the tentative_goal is a fake goal chosen randomly to calculate initial q-values (for new states)
            # it is changed when the agent arrives in that assumed goal
            if may_change_tentative and state[0:2] == self.tentative_goal:
                # ideia: escolher preferencialmente entre locais nao visitados ou menos visitados
                self.tentative_goal = ( rand.randint(0, len(self.env.map)), 
                                        rand.randint(0, len(self.env.map[0])) )
            dist = distance_to_goal(state, self.tentative_goal)
            dist = (-1)*(1.0 - self.gamma**dist) / (1.0 - self.gamma) # formula for geometric series, assuming each step gives -1 reward
            return dist
        else:
            raise Exception()

    def state_action_count_policy(self, state, actions_in_state):
        min_count = 1000000
        min_actions = []
        for a in actions_in_state:
            cnt = self.count.get((state,a), 0)
            if cnt < min_count:
                min_count = cnt
                min_actions = [ a ]
            elif cnt == min_count:
                min_actions.append(a)
        action = rand.choice(min_actions)
        self.count[state,action] = min_count + 1
        return action

    def state_count_policy(self, state, actions_in_state):
        min_count = 1000000
        min_actions = []
        for a in actions_in_state:
            # the model has this state-action pair and it is not a loop
            if (state,a) not in self.model or self.model[state,a][1] == state:
                cnt = 0
            else:
                new_state = self.model[state,a][1]
                cnt = self.count.get(new_state, 0)
            
            if cnt < min_count:
                min_count = cnt
                min_actions = [ a ]
            elif cnt == min_count:
                min_actions.append(a)
        
        action = rand.choice(min_actions)
        return action

    def cell_count_policy(self, state, actions_in_state):
        min_count = 1000000
        min_actions = []
        for a in actions_in_state:
            # the model has this state-action pair and it is not a loop
            if (state,a) not in self.model or self.model[state,a][1] == state:
                cnt = 0
            else:
                new_state = self.model[state,a][1]
                cnt = self.count.get(new_state[0:2],0)  # keys are only the first two components of state (row and column, without direction)
            
            if cnt < min_count:
                min_count = cnt
                min_actions = [ a ]
            elif cnt == min_count:
                min_actions.append(a)
        
        action = rand.choice(min_actions)
        return action



'''
A tabular Q that stores values for pairs (s,a) and that can be progressively filled.
Although may seem awkward, this class was designed carefully to behave as expected 
with the DynaQ+, specially because of its use with varying sets of actions in planning. 
Be carefaul if you want to change.
'''
class TabularQExperimental(object):
    def __init__(self, all_actions):
        self.q = {}  # dictionary for pairs (s,a)
        self.get = self.value  # alternative name
        #self.initialized_states = set()
        self.all_actions = all_actions

    def set(self, s, a, value):
        self.q[s,a] = value

    def value(self, s, a, default_q=None):
        if default_q is None:
            return self.q[s,a]
        else:
            return self.q.get((s,a), default_q)  
    
    def initialize_values(self, s, actions_in_s, default_value):
        # disabled the verification for initialized states because of environments that change dynamically
        for a in self.all_actions:
            if a in actions_in_s:
                if (s,a) not in self.q:
                    self.q[s,a] = default_value
            else:
                # remove entries for invalid actions, possibly added during planning or from the 'all' model
                # Q: why not set to -inf? R: to prevent it to be drawn during planning 
                self.q.pop((s,a), None)

    def argmax(self, s, actions_in_s):
        ties = []
        max_q = float("-inf")
        for a in actions_in_s:
            curr_q = self.q[s,a]  # all entries must exist
            if curr_q > max_q:
                max_q = curr_q
                ties = [a]
            elif curr_q == max_q:
                ties.append(a)
        #assert max_q != float("-inf")  # ok in the tests
        return rand.choice(ties), max_q
    
    def max(self, s, actions_in_s=None):
        top = float("-inf")
        ignore_missing = (actions_in_s is None)
        if ignore_missing:
            actions_in_s = self.all_actions
        for a in actions_in_s:
            # this 'ignore_missing' verification works as an "assert" to ensure
            # that only in certain situations some entries may be missing
            # this happens only in "planning" with certain model options (e.g. 'all')
            if ignore_missing and (s,a) not in self.q:
                continue  # i.e., don't execute the rest of the loop
            curr_q = self.q[s,a]
            if curr_q > top:
                top = curr_q
        #assert top != float("-inf")  # ok in the tests
        return top