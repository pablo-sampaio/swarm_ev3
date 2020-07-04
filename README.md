# swarm_ev3


Projects:

Common - Contains modules that can be used to diverse projects with EV3. In special:
- BotHardware
- PID - very simple PID controller.
- LinesNavigation - to detect and walk on lines interlinked in arbitrary ways. Don't need to be a grid, but you need to mark, somehow the crossings on lines (e.g. a color, or a RFID tag).
- RfidReader - module to access a RFID anthenna, interfaced by an Arduino (that must be running the driver in the corresponding project)

Graph_Exploration - Implements ECEP / NCEP.

RFID_Arduino_Driver - Project that contains the source code that must be uploaded to an
Arduino. This Arduino is an interface to an RFID, which is used in some projects.

RL_Simulated - A project that implements some Reinforcement Learning (RL) algorithms (like DynaQ+) in a simulated way.

RL_in_EV3 - A project to run/test RL algorithms in the EV3 robots.


IDES:
PyCharm 2017.3
ev3dev jessie de set de 2018
python 3 + pyserial
VS Code + PlatformIO

