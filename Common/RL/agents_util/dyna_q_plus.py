
import math
import random as rand

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


class DynaQPlusAgent(object):
    def __init__(self, epsilon=0.1, gamma=0.98, alpha=0.1, planning_steps=5, kappa=0.00001, 
            default_q=0.0):
        self.epsilon = epsilon
        self.gamma = gamma
        self.alpha = alpha
        self.planning_steps = planning_steps
        self.kappa = kappa
        self.qtable = None
        self.model = None
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
        self.qtable = TabularQ(env.all_actions())
        self.model = dict({})  # keys are pairs (state, action)
        
        self.state = None
        self.train_step = 0
        self.epi_step = 0
        self.epi_finished = 0  # number of episodes finished

    # Calling this method to reset the environment is optional.
    # It is useful only if you want to know each start state.
    def reset_env(self):
        assert self.qtable is not None, "Must call start_train() first"
        assert self.state == None, "Episode not finished"  # probably, it is ok to disable this
        self.state = self.env.reset()

        if self.epi_finished == 0: # before training one episode
            self.qtable.initialize_values(self.state, self.env.curr_actions(), self.default_q)

        return self.state

    def step_train(self):
        if self.state == None:
            self.reset_env()

        # select action
        actions_in_state = self.env.curr_actions()
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
            actions_in_new_state = self.env.curr_actions()
            # initializes the q-table for 'new_state'
            self.qtable.initialize_values(new_state, actions_in_new_state, self.default_q) 
            target_q = reward + self.gamma * self.qtable.max(new_state, actions_in_new_state)
        
        q_state_action = self.qtable.value(self.state, action, self.default_q)
        q_state_action += self.alpha * (target_q - q_state_action)
        self.qtable.set(self.state, action, q_state_action)
        
        # update model
        self.update_model(self.state, action, reward, new_state, is_terminal)

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
    def update_model(self, state, action, reward, new_state, is_terminal):
        self.model[state,action] = (reward, new_state, is_terminal, self.train_step)

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
            q_s_a = self.qtable.value(s, a, self.default_q)
            q_s_a += self.alpha * (target_q - q_s_a)
            self.qtable.set(s, a, q_s_a)

