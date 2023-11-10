import time

from BotHardware import RileyRoverBase
from RL.environments import Action


def align_with_walls(robot):
    ANGLE_TO_SCAN = 15
    VELOCITY = 40

    # 1. Scan from -ANGLE_TO_SCAN to +ANGLE_TO_SCAN to find the min distance
    min_distance = max(robot.getDistanceAhead(), robot.getDistanceAhead())
    #print("Finding minimum distance...")
    #print(" - initial distance:", min_distance)
    
    robot.resetOrientation()

    robot.turnToOrientation(-ANGLE_TO_SCAN, VELOCITY)
    robot.turnForEver(VELOCITY)

    while robot.getOrientation() < ANGLE_TO_SCAN:
        distance = max(robot.getDistanceAhead(), robot.getDistanceAhead())
        if distance < min_distance:
            min_distance = distance
    robot.stopMotors()

    #print(" - min distance:", min_distance)

    # 2. Scan multiple times from +ANGLE_TO_SCAN to -ANGLE_TO_SCAN to stop at "min distance + error"
    #    where the admissable error is increased in each scan.
    #print("Scanning to stop at minimum distance...")
    error = 0.05
    scan_min_dist = robot.getDistanceAhead()
    found = scan_min_dist <= (min_distance + error)

    while not found:
        robot.turnForEver(-VELOCITY)
        while not found and robot.getOrientation() > -ANGLE_TO_SCAN:
            distance = robot.getDistanceAhead()
            scan_min_dist = min(distance, scan_min_dist)
            found = distance <= (min_distance + error)

        if found:
            break

        error *= 2.0
        robot.turnForEver(+VELOCITY)
        while not found and robot.getOrientation() < +ANGLE_TO_SCAN:
            distance = robot.getDistanceAhead()
            scan_min_dist = min(distance, scan_min_dist)
            found = distance <= (min_distance + error)

        error *= 2.0
        #print(" - after 2 scans, admissable error is", error, "min distance found was", scan_min_dist)
        #print(" - last distance was", distance)

    robot.stopMotors()
    #print("Final distance:", robot.getDistanceAhead())
    #print("Final orientation:", robot.getOrientation())



class RileyRoverGridEnv:
    '''
    An environment that interfaces to a real EV3 robot that physically executes the actions.
    This class was specially created for the RilleyRoverBase, but may work with other bases (like Kraz3Base) too.
    The obstacles are detected using a distance (US or IR) sensor.
    '''
    def __init__(self, robot, count_visits=False, reward_option='goal', wait_every_step=0.0, safe_distance=23.0):
        self.robot = robot
        self.min_safe_distance = safe_distance
        # Here, the 'transition' is the relative view of the agent
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
        self.wait_every_step = wait_every_step

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
            
            self.robot.runMotorsDistance(25.0, 150) # anda 25.0 cm

        elif action == Action.TURN_CW:
            orientation = (orientation+90) % 360
            self.robot.turn(90)
        elif action == Action.TURN_COUNTER_CW:
            orientation = (orientation-90) % 360
            self.robot.turn(-90)
        else:
            raise Exception("Invalid action")
        
        self.epi_steps += 1
        #if (self.epi_steps % 5) == 0:
            # alinha o robô, girando até minimizar a distância à parede
            #align_with_walls(self.robot)

        return (row, col, orientation)

    def reset_visits(self):
        old_visits = self.visits
        if self.count_visits:
            self.visits = {}
        return old_visits

    def _front_allowed(self):
        return self.robot.getDistanceAhead() >= self.min_safe_distance

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
