import time

from BotHardware import Kraz3Base
from RL.environments import Action

DEFAULT_MAP_OBSTACLES = [ (+1,0), (+1,-1), (+1,-2), (0,-3), (-1,-3), (0,+1), (-1,+1), (-2,0), (-2,-1), (-2,-2) ]
DEFAULT_MAP_GOAL = (-1,-2)

class Kraz3GridEnv:
    '''
    An environment that interfaces to a real EV3 robot that physically executes the actions.
    This class is an improved version of the RileyRoverBase, although only tested on Kraz3Base. It doesn't use the distance
    sensor (to find obstacles) or the color sensor (to detect the terminal state), and makes the agent more inclined to
    doing FRONT actions.
    The limits of the map and the obstacles is represented by a list of `forbidden_positions`. The current default forbidden 
    positions delimit a 3x2 map, extending to the front an to the left of the initial position of the robot.
    The goal position is also a parameter. 
    The initial state may be provided as a tuple of 3 integers (row, column, orientation).
    '''
    def __init__(self, robot, count_visits=False, reward_option='goal', wait_every_step=0.0,
                 initial_state=(0,0,0), forbidden_positions=DEFAULT_MAP_OBSTACLES, goal_position=DEFAULT_MAP_GOAL):
        self.robot = robot
        
        # Here, the 'transition' is the relative view of the agent
        # Column and row are always assumed to be 0 in the start of an episode
        # and may become negative
        assert initial_state[2] in [0, 90, 180, 270]
        self.initial_state = tuple(initial_state)
        self.state = None
        
        assert reward_option in ['goal', 'step_cost']
        self.reward_option = reward_option
        if reward_option == 'goal':
            self.STEP_REWARD = 0.0
            self.GOAL_REWARD = 1.0
            self.HOLE_REWARD = -1.0     # not used yet
        else:
            self.STEP_REWARD = -1.0
            self.GOAL_REWARD = 0.0
            self.HOLE_REWARD = -1000.0  # not used yet

        if count_visits:
            self.visits = {}
        else:
            self.visits = None
        self.count_visits = count_visits
        
        self.forbidden_positions = list(forbidden_positions)
        self.goal_position = tuple(goal_position)  # must be tuple, to compare with the state tuple

        self.actions_no_front = list(Action)
        self.actions_no_front.remove(Action.FRONT)
        
        # a list with the multiple copies of Action.FRONT
        # this is basically a HACK, to increase the odds of the agent choosing this action
        self.actions = list(Action)
        self.actions.append(Action.FRONT)
        self.actions.append(Action.FRONT)

        self.wait_every_step = wait_every_step

        self.step = self.apply_action # another name for the function (similar to the name used in gym)

    def all_actions(self):
        return list(Action)

    def curr_actions(self):
        assert self.state is not None, "Environment must be reset"
        if self._front_allowed():
            return self.actions
        else:
            return self.actions_no_front
    
    def states(self):
        raise Exception("In this environment, the state space is unknown.")

    def reset(self):
        print("Place the robot in the start position (use always the same!).")
        print("Press ANY button when ready.")
        while not self.robot.brickButton.any():
            pass
        self.robot.speaker.beep()
        if self.wait_every_step:
            time.sleep(self.wait_every_step)
        
        self.state = self.initial_state 
        if self.visits is not None:
            count = self.visits.get(self.state[0:2], 0)
            self.visits[self.state[0:2]] = count + 1
        self.epi_steps = 0
        return self.state

    def _internal_apply_action(self, obs, action, apply=True):
        row, col, orientation = obs

        if action == Action.FRONT:
            if orientation == 0: # Direction.UP:
                row -= 1
            elif orientation == 180: #Direction.DOWN:
                row += 1
            elif orientation == 90: # Direction.RIGHT:
                col += 1
            elif orientation == 270: # Direction.LEFT:
                col -= 1
            else:
                raise Exception("Invalid direction")
            
            if apply:
                self.robot.runMotorsDistance(25.0, 150) # anda 25.0 cm

        elif action == Action.TURN_CW:
            orientation = (orientation+90) % 360
            if apply:
                self.robot.turn(90)
        elif action == Action.TURN_COUNTER_CW:
            orientation = (orientation-90) % 360
            if apply:
                self.robot.turn(-90)
        else:
            raise Exception("Invalid action")
        
        if apply:
            self.epi_steps += 1

        return (row, col, orientation)

    def reset_visits(self):
        old_visits = self.visits
        if self.count_visits:
            self.visits = {}
        return old_visits

    def _front_allowed(self):
        next_state = self._internal_apply_action(self.state, Action.FRONT, apply=False)
        next_pos = next_state[0:2]
        return next_pos not in self.forbidden_positions

    def _check_goal(self):
        arrived = (self.state[0:2] == self.goal_position)
        if arrived and isinstance(self.robot, Kraz3Base):
            self.robot.celebrate()
        return arrived

    def apply_action(self, action):
        assert self.state is not None, "Environment must be reset"

        new_state = None
        if action != Action.FRONT or self._front_allowed():
            new_state = self._internal_apply_action(self.state, action)
            self.state = new_state
            if self.visits is not None and action == Action.FRONT:
                count = self.visits.get(self.state[0:2], 0)
                self.visits[ self.state[0:2] ] = count + 1
        else:
            # prohibited moves: 
            # don't change self.state but store it in new_state to return it
            print("Prohibited action")
            new_state = self.state
       
        if self.wait_every_step:
            time.sleep(self.wait_every_step)
       
        arrived = self._check_goal()

        if arrived:
            self.robot.speaker.beep()
            reward = self.GOAL_REWARD
            self.state = None 
        else:
            reward = self.STEP_REWARD

        return new_state, reward, arrived
    
    def get_visits_with_nonnegative_pos(self):
        if self.visits is not None:
            rows, cols = zip(*self.visits.keys())
            rmin = min(rows)
            rmax = max(rows)
            cmin = min(cols)
            cmax = max(cols)
            new_visits = [[0 for x in range(cmax-cmin+1)] for x in range(rmax-rmin+1)] 
            for r, c in self.visits.keys():
                new_visits[r-rmin][c-cmin] = self.visits[(r,c)]
            return new_visits
        else:
            return None
