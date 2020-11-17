# Swarm EV3 Projects

This repository contains a set of projects that use **Lego Mindstorms EV3** robotic plataform to test algorithms to control multi-robots (multi-agents) in collective tasks. The algorithms assume that the robots/agents are limited in their computational resources and sensors capabilities. 

Most algorithms are designed for multiple agents, to run with pottentially thousands, although never tested in more than a few. (The algorithms could be run in much simpler robotic platforms, but EV3 was used because it is more ready to use).

## Technical Details

- **Languages**: *Python* (most of the code) and *C* (just the Arduino driver).
- **EV3 Kit**: The code works with 45544 (mounted with the "Educator" base) or 31313 (mounted with the "Enterprise" base).
- **Operating system** (EV3): [ev3dev](http://www.ev3dev.org/), version *jessie*.
- **Other hardware pieces**: Some projects require an **Arduino** interfacing an RFID MFRC522, with the Arduino connected to the EV3 through the USB port. The C code for the Arduino is provided. 
- **IDE**: All projects should open in *VS Code*. (Older PyCharm project settings may also be present, but it is not actively used).

## Projects

**Common** - Just a directory that contains modules used in diverse projects with EV3:
- *BotHardware* - Functions to control diverse bases mounted with EV3 (45444 or 31313).
- *PID* - Very simple PID controller.
- *LinesNavigation* - Provides functions to detect and walk on lines interlinked in arbitrary ways. Don't need to be a grid, but you need to mark, somehow the crossings on lines (e.g. a color, or a RFID tag).
- *RfidReader* - A module to communicate with the RFID MFRC522, interfaced by the Arduino. To work, the Arduino *must* run the driver developed in the RFID_Arduino_Driver project.
- *RL* - Reinforcement learning environments and agents (algorithms). A simple simulated environment in a grid world is provided together with another "environment" used as interface  to control the EV3 in a real setting that mimics a grid (with square cells). The RL agents can be applied seamlessly in both.

**Graph_Exploration** - Implements ECEP and  NCEP algorithms.

**RFID_Arduino_Driver** - Contains the source code that must be uploaded to an
Arduino. The code defines a communication protocol through the serial port that allows the EV3 (or even a PC) read/write from/to RFID tags.

**RL_Simulated** - A project that tests Reinforcement Learning (RL) algorithms (like *DynaQ+*) with simulated agents (not using EV3).

**RL_in_EV3** - A project to run/test RL algorithms in the EV3 robots.


## Other Informations

These projects were developed by professor Pablo A. Sampaio, with undergraduate students. Some of the algorithms were published in conferences.

## References

P. Azevedo Sampaio and J. Washington Pereira, ["Multi-Robot Navigation and Exploration in Graphs with Entrance-Dependent Identification of the Edges,"](https://ieeexplore.ieee.org/document/9018598) 2019 Latin American Robotics Symposium (LARS), 2019 Brazilian Symposium on Robotics (SBR) and 2019 Workshop on Robotics in Education (WRE), Rio Grande, Brazil, 2019, pp. 323-328, doi: 10.1109/LARS-SBR-WRE48964.2019.00063.

--

*Prof. Pablo A. Sampaio*

*Universidade Federal Rural de Pernambuco*

