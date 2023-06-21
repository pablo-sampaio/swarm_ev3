
# RL_Simulated

This folder contains experiments with reinforcement learning algorithms with some experimental modifications.
The environment is a simple grid-based maze. 

The classes for the algorithms and the environment are in folder `Common\RL`. But here we provide some description:

- class `SimulatedEnv` implements a simple maze, with the standard size of 5 rows x 7 columns. Two reward systems are offered:
  - 'goal': the agent receives +1 when reaches the goal cell, and 0 in every other step
  - 'step_cost': the agent receives -1 in every timestep, and 0 when it reaches the goal

- class `DynaQPlusAgent`implements Dyna-Q+ (that can also run as a Dyna-Q or as a Q-Learning, depending on the parameters).
We provide these extra features:
  - the Q-table may have an experimental *'initial value'*
  - the first episode may be run with a *'initial_policy'* other than the standard epsilon-greedy policy
  - parameter `model_option` allows to set how much of the state x action space is represented in the agent's internal model 
  (that is used in the planning steps)

The most relevant files are named `"exper_[reward_type]-[num] - [experiment id].py"` where:
- `[reward_type]` may be 'goal' or 'step' (shorthand for the step_cost reward)
- `[num]` is a number used simply to define a desired ordering between the files =)
- `[experiment id]` identifies the type of experiment, i.e. the kind of parameter that is varied
