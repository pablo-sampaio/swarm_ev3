# Swarm EV3 Projects

This repository contains a set of projects that use **Lego Mindstorms EV3** robotic plataform to test algorithms to control multi-robots (multi-agents) in collective tasks. The algorithms assume that the robots/agents are limited in their computational resources and sensors capabilities. 

Most algorithms are designed for multiple agents, to run with pottentially thousands, although never tested in more than a few. (An even simpler robotic plataform could run the same algorithms, and EV3 was use to be more ready-to-use).

## Technical Details

Languages: Python (most of the code) and C (just the Arduino driver).

The EV3 run the [ev3dev](http://www.ev3dev.org/) operating system, version *jessie*.

Some projects require an **Arduino** interfacing an RFID MFRC522, with the Arduino connected to the EV3 through the USB port. The C code for the Arduino is provided. 

Most of the projects should open in *VS Code* IDE. An older PyCharm project file is also present (but it is not actively used).

## Projects

**Common** - Just a directory that contains modules used in diverse projects with EV3:
- *BotHardware* - Functions to control diverse bases mounted with EV3 (45444 or 31313).
- *PID* - Very simple PID controller.
- *LinesNavigation* - Provides functions to detect and walk on lines interlinked in arbitrary ways. Don't need to be a grid, but you need to mark, somehow the crossings on lines (e.g. a color, or a RFID tag).
- *RfidReader* - A module to communicate with the RFID MFRC522, interfaced by the Arduino. To work, the Arduino *must* run the driver in the corresponding project.

**Graph_Exploration** - Implements ECEP and  NCEP algorithms.

**RFID_Arduino_Driver** - Contains the source code that must be uploaded to an
Arduino. The code defines a communication protocol through the serial port that allows the EV3 (or even a PC) read/write from/to RFID tags.

**RL_Simulated** - A project that implements some Reinforcement Learning (RL) algorithms (like *DynaQ+*) in a simulated way.

*RL_in_EV3* - A project to run/test RL algorithms in the EV3 robots.


## Other Informations

These projects were developed by professor Pablo A. Sampaio, with undergrad students. Some of the algorithms were published in conferences.

*Prof. Pablo A. Sampaio*
*Universidade Federal Rural de Pernambuco*

