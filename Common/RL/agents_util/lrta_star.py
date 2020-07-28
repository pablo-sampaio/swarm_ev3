
from RL.agents_util.q_table import TabularQ


# Attention: this a a LRTA* adapted to use rewards (instead of costs/distances) 
# and to use "zero-range" data
# TODO: implement default 1-range version, using the model
class LRTAStarAgent:

    def __init__(self, **kwargs):
        self.values = {}
        self.default_q = 0.0
        self.h = None
    
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

    # it is optional to call this method
    # useful only if you want to know each start state
    def reset_env(self):
        assert self.h is not None, "Must call start_train() first"
        assert self.state == None, "Episode not finished"
        self.state = self.env.reset()
        # on first episode, initialize the "h-table" for the initial state (assuming it is always the same)
        if self.epi_finished == 0:
            self.h.initialize_values(self.state, self.env.valid_actions(), self.default_q) 
        return self.state

    def step_train(self):
        if self.state is None:
            self.reset_env()

        actions_in_state = self.env.valid_actions()
        action, _ = self.h.argmax(self.state, actions_in_state)

        new_state, reward, terminal = self.env.apply_action(action)
        self.train_step += 1
        self.epi_step += 1

        # updates the heuristic
        if terminal:
            new_h = reward 
        else:
            actions_in_new_state = self.env.valid_actions()
            # initializes the q-table for 'new_state'
            self.h.initialize_values(new_state, actions_in_new_state, self.default_q) 
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

