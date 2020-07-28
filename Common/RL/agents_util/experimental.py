
import math
import random as rand

#from enum import Enum, unique
from itertools import product

from RL.environments import Action, Direction
from RL.agents_util.q_table import TabularQ

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
        self.train_step = 0

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
        self.qtable = TabularQ(env.all_actions())
        self.model = dict({})  # keys are pairs (state, action)
        
        self.state = None
        self.train_step = 0
        self.epi_step = 0
        self.epi_finished = 0  # number of finished episodes

        if self.model_option == 'all':
            for s_a in product(env.states(), list(Action)):
                self.model[s_a] = (0.0, s_a[0], False, self.train_step)

        if isinstance(self.default_q, str) and self.default_q == 'tentative_goal_dist':
            self.tentative_goal = ( rand.randint(0, len(env.map)), 
                                    rand.randint(0, len(env.map[0])) )

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

    '''def init_q_for_state(self, state, actions_in_state):
        if isinstance(self.default_q, (int,float)):
            self.qtable.initialize_values(state, actions_in_state, self.default_q)
        elif isinstance(self.default_q, str) and self.default_q == 'goal_dist':
            dist = distance_to_goal(state, self.env.goal_position)
            dist = (-1)*(1.0 - self.gamma**dist) / (1.0 - self.gamma) # formula for geometric series, assuming each step gives -1 reward
            self.qtable.initialize_values(state, actions_in_state, dist)
        elif isinstance(self.default_q, str) and self.default_q == 'tentative_goal_dist':
            if state[0:2] == self.tentative_goal:
                # TODO: escolher apenas entre locais nao visitados
                self.tentative_goal = ( rand.randint(0, len(self.env.map)), 
                                        rand.randint(0, len(self.env.map[0])) )
            dist = distance_to_goal(state, self.tentative_goal)
            dist = (-1)*(1.0 - self.gamma**dist) / (1.0 - self.gamma) # formula for geometric series, assuming each step gives -1 reward
            self.qtable.initialize_values(state, actions_in_state, dist)
        else:
            raise Exception()'''

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

    # Calling this method to reset the environment is optional.
    # It is useful only if you want to know each start state.
    def reset_env(self):
        assert self.qtable is not None, "Must call start_train() first"
        assert self.state == None, "Episode not finished"  # probably, it is ok to disable this
        self.state = self.env.reset()
       
        if self.epi_finished == 0: # before training one episode
            q_state = self.get_heuristic_q(self.state, True)
            if math.isnan(q_state):
                print()
            self.qtable.initialize_values(self.state, self.env.curr_actions(), q_state)
        elif self.epi_finished == 1: # after training one episode
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
            target_q = reward
        else:
            actions_in_new_state = self.env.curr_actions()
            # initializes the q-table for 'new_state'
            q_new_state = self.get_heuristic_q(new_state, True)
            if math.isnan(q_new_state):
                print()
            self.qtable.initialize_values(new_state, actions_in_new_state, q_new_state)
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
            # TODO: attention! what happens if the environment changes (adding or blocking an action)?
            for a in actions_in_state:
                if (state,a) in self.model: # if it has entry for one action (in state), it has for all
                    break
                if a != action:
                    self.model[state,a] = (assumed_r, state, False, self.train_step)
        else:
            raise Exception()
        
        # for all models
        self.model[state,action] = (reward, new_state, is_terminal, self.train_step)
        if self.reverse_action:
            inv_action = Action.reverse(action)
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
                target_q = r + self.gamma * self.qtable.max(next_s, None) 
            q_s_a = self.qtable.value(s, a, self.get_heuristic_q(s, False))
            q_s_a += self.alpha * (target_q - q_s_a)
            if math.isnan(q_s_a):
                print()
            self.qtable.set(s, a, q_s_a)

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

    #def dfs(self, state, actions_in_state):
        #if self.state in self.visited_places: