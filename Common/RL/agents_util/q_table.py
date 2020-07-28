
import random as rand

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
        # disabled the code below because of environments that change dynamically
        #if s in self.initialized_states:
        #    return
        #self.initialized_states.add(s)
        for a in self.all_actions:
            if a in actions_in_s:
                if (s,a) not in self.q:
                    self.q[s,a] = default_value
            else:
                # remove entries for invalid actions, added during planning 
                # Q: why not set to -inf? R: to avoid it to be drawn during planning 
                self.q.pop(s,a)

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

