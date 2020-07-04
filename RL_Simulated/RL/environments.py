
import numpy as np
import random as rand

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
        # 0 is corridor; 1 is wall; 2 is goal (r=1); 3 is start position; 
        # 4 is a hole that terminates the episode (r=-1); 5 is a cliff that returns to initial position (-1)
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

        if count_visits:
            self.visits = np.zeros((len(self.map), len(self.map[0])), dtype=int)
        else:
            self.visits = None
        self.count_visits = count_visits
        
        self.actionset = list(Action)
        self.step = self.apply_action # another name for the function (similar to the name used in gym)

    def all_actions(self):
        return self.actionset
    
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
        
        arrived = (self.map[new_state[0]][new_state[1]] == 2)
        reward = 0.0 if self.reward_option=='goal' else -1.0
        if arrived:
            reward = 1.0 if self.reward_option=='goal' else 50.0
            self.state = None  #but don't change the observation (that will be returned)

        return self.observation, reward, arrived


# o robot deve ser um das classes que extendem AbstractRobotHardware 
# do projeto Ev3_Swarm

_ORIENT_ERROR_MARGIN = 10.0  # in degrees

class Ev3GridEnv:
    def __init__(self, robot, count_visits=False, reward_option='goal'):
        self.robot = robot
        # here, the "state" is the relative view of the agent
        # column and row are always assumed to be 0 in the start of an episode
        # negative columns and rows may appear
        self.initial_state = (0, 0, 0)  # row, column, orientation angle
        self.state = None
        assert reward_option in ['goal', 'step_cost']
        self.reward_option = reward_option
        
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
        print("Place the robot in the start position (use always the same!)")
        while not self.robot.brickButton.any():
            pass
        assert (self.robot.readColor() == 3), "Didn't sense green color in start state!"  # GREEN
        self.robot.speaker.beep()
        self.robot.resetOrientation()

        self.state = self.initial_state 
        if self.visits is not None:
            count = self.visits.get((self.state[0], self.state[1]), 0)
            self.visits[self.state[0], self.state[1]] = count + 1
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
            # se der problema, usar:
            # rounded_orientation = 90.0 * ((robot.orientation + _ORIENT_ERROR_MARGIN) // 90)
            # self.robot.turnToOrientation(rounded_orientation + 90)
            # ideia antiga:
            # delta = 360 if orientation == 0 else orientation
            # self.robot.turnToOrientation(360.0*((self.robot.orientation//360 + _ORIENTATION_MARGIN)) + delta)
            # if 0 (era 270) : 360 * orientation // 360 + 360
            # if 90 (era 0) : 360 * orientation // 360 + 90
            # if 180 (era 90) : 360 * orientation // 360 + 180
            # if 270 (era 180) : 360 * orientation // 360 + 270
        elif action == Action.TURN_COUNTER_CW:
            orientation = (orientation-90) % 360
            self.robot.turnToOrientation(self.robot.getOrientation() - 90)
            # se der problema, usar:
            # rounded_orientation = 90.0 * ((robot.orientation + _ORIENT_ERROR_MARGIN) // 90)
            # self.robot.turnToOrientation(rounded_orientation - 90)
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
                count = self.visits.get((self.state[0], self.state[1]), 0)
                self.visits[self.state[0], self.state[1]] = count + 1
        else:
            # prohibited moves: 
            # don't change self.state but set it to new_state to return it
            new_state = self.state
        
        arrived = self._check_goal()
        reward = 0.0 if self.reward_option=='goal' else -1.0
        if arrived:
            self.robot.speaker.beep()
            reward = 1.0 if self.reward_option=='goal' else 0.0  # TODO: rever
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

