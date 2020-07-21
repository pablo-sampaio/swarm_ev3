
#import numpy as np  # TODO: change, to make it independent of np
import random as rand
import time

from enum import Enum, unique
from itertools import product

@unique
class Direction(Enum):
    # Important: numbered in clocwise order !
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

@unique
class Action(Enum):
    FRONT = 0
    TURN_CW = 1
    TURN_COUNTER_CW = 2


class SimulatedEnv:
    def __init__(self, count_visits=False, use_real_state=False, reward_option='goal'):
        # 0 is corridor; 1 is wall; 2 is goal (r=1, if reward is goal); 
        # 3 is start position; 
        # 4 is a hole that terminates the episode (r=-1, if reward is goal); 
        self.map = [ 
            [ 0, 0, 0, 0, 0, 0, 2],
            [ 0, 0, 0, 0, 0, 0, 0],
            [ 0, 1, 1, 1, 1, 1, 1],
            [ 0, 0, 0, 0, 0, 0, 0],
            [ 0, 0, 0, 3, 0, 0, 0],
        ]
        # "state" reflects the absolute view of the map
        # while "observation" is the view of the agent
        self.initial_state = (4, 3, Direction.UP)  # row, column, orientation
        assert self.map[self.initial_state[0]][self.initial_state[1]] == 3, "Initial position in the map should have 3"
        self.state = None
        self.observation = None
        self.use_real_state = use_real_state
        assert reward_option in ['goal', 'step_cost']
        self.reward_option = reward_option
        if reward_option == 'goal':
            self.STEP_REWARD = 0.0
            self.GOAL_REWARD = 1.0
            self.HOLE_REWARD = -1.0
        else:
            self.STEP_REWARD = -1.0
            self.GOAL_REWARD = 0.0
            self.HOLE_REWARD = -1000.0

        if count_visits:
            self.visits = np.zeros((len(self.map), len(self.map[0])), dtype=int)
        else:
            self.visits = None
        self.count_visits = count_visits
        
        self.actionset = list(Action)
        self.actionset_no_front = list(Action)
        self.actionset_no_front.remove(Action.FRONT)

        self.step = self.apply_action # another name for the function (similar to the name used in gym)

    def all_actions(self):
        return self.actionset
    
    def curr_actions(self):
        assert self.state is not None, "Environment must be reset"
        state = self.state
        if 0 <= state[0] < len(self.map) \
                and 0 <= state[1] < len(self.map[0]) \
                and self.map[state[0]][state[1]] != 1:
            return self.actionset
        else:
            return self.actionset_no_front

    def states(self):
        positions = product(range(len(self.map)), range(len(self.map[0])))
        return product(positions, list(Direction))

    def reset(self):
        self.state = self.initial_state 
        if self.use_real_state:
            self.observation = self.state
        else:
            self.observation = (0, 0, Direction.UP) # can be randomized, at least the direction
        if self.visits is not None:
            self.visits[self.state[0], self.state[1]] += 1
        return self.observation

    def _internal_apply_action(self, obs, action):
        row, col, direction = obs
        if action == Action.FRONT:
            if direction == Direction.UP:
                row -= 1
            elif direction == Direction.DOWN:
                row += 1
            elif direction == Direction.RIGHT:
                col += 1
            elif direction == Direction.LEFT:
                col -= 1
            else:
                raise Exception("Invalid direction")
        elif action == Action.TURN_CW:
            direction = Direction( (direction.value + 1) % 4 )
        elif action == Action.TURN_COUNTER_CW:
            direction = Direction( (direction.value - 1) % 4)
        else:
            raise Exception("Invalid action")
        return (row, col, direction)

    def reset_visits(self):
        old_visits = self.visits
        if self.count_visits:
            self.visits = np.zeros((len(self.map), len(self.map[0])), dtype=int)
        return old_visits

    def apply_action(self, action):
        assert self.state is not None, "Environment must be reset"

        new_state = self._internal_apply_action(self.state, action)
        
        if 0 <= new_state[0] < len(self.map) \
                and 0 <= new_state[1] < len(self.map[0]) \
                and self.map[new_state[0]][new_state[1]] != 1:
            self.state = new_state
            self.observation = self._internal_apply_action(self.observation, action)
            if self.visits is not None and action == Action.FRONT:
                self.visits[new_state[0], new_state[1]] += 1
        else:
            # prohibited moves: don't change self.state and self.observation
            new_state = self.state
        
        arrived = False
        if self.map[new_state[0]][new_state[1]] == 2: # goal
            arrived = True
            reward = self.GOAL_REWARD
        elif self.map[new_state[0]][new_state[1]] == 4:  # hole
            arrived = True
            reward = self.HOLE_REWARD
        else:
            reward = self.STEP_REWARD
        
        if arrived:
            self.state = None  # but don't change the observation (that will be returned)

        return self.observation, reward, arrived



_ORIENT_ERROR_MARGIN = 15.0  # in degrees

class Ev3GridEnv:
    '''
    An environment that interfaces to a real EV3 robot that physically executes the actions.
    The 'robot' parameter should be one of the classes from BotHarware module.
    '''
    def __init__(self, robot, count_visits=False, reward_option='goal'):
        self.robot = robot
        # Here, the "state" is the relative view of the agent
        # Column and row are always assumed to be 0 in the start of an episode
        # and may become negative
        self.initial_state = (0, 0, 0)  # row, column, orientation angle
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
        
        self.actions = list(Action)
        self.actions_no_front = list(Action)
        self.actions_no_front.remove(Action.FRONT)
        self.step = self.apply_action # another name for the function (similar to the name used in gym)

    def all_actions(self):
        return self.actions

    def curr_actions(self):
        assert self.state is not None, "Environment must be reset"
        if self._front_allowed():
            return self.actions
        else:
            return self.actions_no_front
    
    def states(self):
        raise Excetion("In this environment, the state space is unknown.")

    def reset(self):
        print("Place the robot in the start position (use always the same!).")
        print("The robot starts when you press a button or when sensing green.")
        while not (self.robot.brickButton.any() or self.robot.readColor() == 3):
            pass
        self.robot.speaker.beep()
        time.sleep(3)
        self.robot.resetOrientation()

        self.state = self.initial_state 
        if self.visits is not None:
            count = self.visits.get(self.state[0:2]), 0)
            self.visits[self.state[0:2]] = count + 1
        return self.state

    def _internal_apply_action(self, obs, action):
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
            self.robot.runMotorsDistance(21.5, 150) # anda 21.5 cm
        elif action == Action.TURN_CW:
            orientation = (orientation+90) % 360
            self.robot.turnToOrientation(self.robot.getOrientation() + 90)
            #rounded_orientation = 90.0 * ((self.robot.getOrientation() + _ORIENT_ERROR_MARGIN) // 90)  # resultados + / -
            #self.robot.turnToOrientation(rounded_orientation + 90)
        elif action == Action.TURN_COUNTER_CW:
            orientation = (orientation-90) % 360
            self.robot.turnToOrientation(self.robot.getOrientation() - 90)
            #rounded_orientation = 90.0 * ((self.robot.getOrientation() + _ORIENT_ERROR_MARGIN) // 90)
            #self.robot.turnToOrientation(rounded_orientation - 90)
        else:
            raise Exception("Invalid action")
        return (row, col, orientation)

    def reset_visits(self):
        old_visits = self.visits
        if self.count_visits:
            self.visits = {}
        return old_visits

    def _front_allowed(self):
        return self.robot.getDistanceAhead() >= 22.0

    def _check_goal(self):
        return (self.robot.readColor() == 5)  # RED

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
        
        arrived = self._check_goal()
        reward = self.STEP_REWARD
        if arrived:
            self.robot.speaker.beep()
            reward = self.GOAL_REWARD
            self.state = None 

        return new_state, reward, arrived
    
    def get_visits_with_nonnegative_pos(self):
        if self.visits is not None:
            rows, cols = zip(*self.visits.keys())
            rmin = min(rows)
            rmax = max(rows)
            cmin = min(cols)
            cmax = max(cols)
            new_visits = np.zeros((rmax-rmin+1, cmax-cmin+1), dtype=int)
            for r, c in self.visits.keys():
                new_visits[r-rmin, c-cmin] = self.visits[(r,c)]
            return new_visits
        else:
            return None

class _DummyBot:
    ''' Class created only to test the Ev3GridEnv
    '''
    def __init__(self):
        class _Button:
            def __init__(self, parent):
                self.parent = parent
            def any(self):
                self.parent.count = 0
                return True
        class _Sound:
            def beep(self):
                print("Beeep!")
                pass
        self.brickButton = _Button(self)
        self.speaker = _Sound()
        self.count = 0
        self.orientation = 0.0

    def readColor(self):
        return 5 if self.count >= 20 else 3 

    def runMotorsDistance(self, distance, velocity=200, wait=True):
        self.count += 1

    def getOrientation(self):
        return self.orientation

    def resetOrientation(self):
        self.orientation = 0.0

    def turnToOrientation(self, abs_degrees, velocity=50):
        self.orientation = abs_degrees

    def getDistanceAhead(self):
        return 25.0
