
To run this project, first your EV3 must be connected to the device, 
using the ev3dev-browser (VS Code extesion).

Tested with:
- ev3dev-browser 1.1.0 + ev3dev-stretch 
- ev3dev-browser 0.8.1 + ev3dev-jessie


TO CONFIGURE ON THE 1st TIME YOU RUN THE PROJECT ON THE DEVICE
(or after major changes without tests)
--------------------------------------------------------------
1) On the "ev3dev Device Browser", click on "Dowload workspace"
2) On the device, right click and choose "Open SSH Terminal"
3) Run 
   chmod +x ~/RL_in_EV3/setup_libs
4) Run 
   ~/RL_in_EV3/setup_libs
5) Run the file (see below)


TO RUN A FILE 
(possibly after changes to "RL_in_EV3" folder)
---------------------------------------------------------
1) Hit Ctrl+F5 (on the desired file in EV3_PROJ)
   - the file must start with "#!/usr/bin/env python3"
2) If a problem (runtime error) occurs or if your are using ev3dev-jessie: 
   - on the ev3dev-browser choose "Open SSH Terminal"
   - run: python3 <your-file.py>

 
EVERYTIME YOU CHANGE FILES IN *OTHER* FOLDERS
----------------------------------------------
1) On the "ev3dev Device Browser", click on "Dowload workspace"
2) Run the file you want
