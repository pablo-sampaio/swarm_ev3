# Swarm EV3 Projects

This repository hosts a series of projects utilizing the **LEGO Mindstorms EV3** platform to develop and test algorithms for controlling multi-robot (multi-agent) systems in collective tasks. The EV3 platform was chosen for its balance of computational and sensor limitations, making it an ideal testbed for algorithms intended for agents with similar constraints.

The core objective of these projects is to explore the development of scalable algorithms that, while tested on EV3, are designed to be ported and applied to larger systems potentially involving thousands of agents on more constrained platforms.


## Technical Details

- **Languages**: *Python* (most of the code) and *C++* (just the Arduino driver).
- **EV3 Kit**: The code works with 45544 (mounted with the "Educator" base) or 31313 (mounted with one of these bases: "Seshan's Enterprise", "Riley Rover", "Lego Kraz3").
- **EV3 Operating system**: [ev3dev](http://www.ev3dev.org/), loaded from a SD card.
- **Other hardware pieces**: Some projects require an **Arduino** interfacing an RFID MFRC522, with the Arduino connected to the EV3 through the USB port. The C++ code for the Arduino is provided. 
- **IDE**: All projects should open in *VS Code*. 


## Projects

All these projects are available in this repository. Each one has its own *VS Code* workspace in the root folder.

- **Graph_Exploration** - Implements ECEP and  NCEP algorithms (see references).

- **RL_Simulated** - A project that tests Reinforcement Learning (RL) algorithms (like *DynaQ+*) with simulated agents (not using EV3).

- **RL_in_EV3** - A project to run/test RL algorithms in the EV3 robots.

- **RFID_Arduino_Driver** - Contains the source code that must be uploaded to an
Arduino. The code defines a communication protocol through the serial port that allows the EV3 (or even a PC) read/write from/to RFID tags.


## Running the Projects

Detailed instructions for setting up the robot and running the code is found inside `RL_in_EV3/` folder.

For other projects, the instructions are mostly the same.


## Common Code

The other folders contains code shared by different projects.

- **Common** - Functions and classes for controlling the robot
    - *BotHardware* - To control diverse bases assembled with EV3 (45444 or 31313).
    - *PID* - Very simple PID controller.
    - *LinesNavigation* - Provides functions to detect and walk on lines interlinked in arbitrary ways. Don't need to be a grid, but you need to mark, somehow the crossings on lines (e.g. a color, or a RFID tag).
    - *RfidReader* - A module to communicate with the RFID MFRC522, interfaced by the Arduino. To work, the Arduino *must* run the driver developed in the RFID_Arduino_Driver project.

- **Common RL** - Reinforcement learning code 
    - *agents.py* - Implementation of Dyna-Q+ (generalization of Q-Learning) and some realtime search algorithms, that can be applied to all environments (real or simulated).
    - *environments.py* - Simulated environment in a grid world is provided together with other "environment" used as interfaces to control the EV3 in a real setting that mimics a grid (with square cells).

- **RFID_Arduino_Driver** - C++ code for Arduino or similar boards, used in *GraphExploration* project.


## Other Informations

These projects were developed by professor Pablo A. Sampaio, with some help of undergraduate students of UFRPE University (Recife-Brazil). Some of the algorithms were published in conferences.


## References

P. Azevedo Sampaio and J. Washington Pereira, ["Multi-Robot Navigation and Exploration in Graphs with Entrance-Dependent Identification of the Edges,"](https://ieeexplore.ieee.org/document/9018598) 2019 Latin American Robotics Symposium (LARS), 2019 Brazilian Symposium on Robotics (SBR) and 2019 Workshop on Robotics in Education (WRE), Rio Grande, Brazil, 2019, pp. 323-328, doi: 10.1109/LARS-SBR-WRE48964.2019.00063.

--

*Prof. Pablo A. Sampaio*

*Universidade Federal Rural de Pernambuco*

