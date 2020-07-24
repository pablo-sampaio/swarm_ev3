
To run this project, first your EV3 must be connected to the device, 
using the ev3dev-browser (VS Code extesion).

Tested with:
- **ev3dev-browser 1.1.0 + ev3dev-stretch**
- **ev3dev-browser 0.8.1 + ev3dev-jessie**


## TO CONFIGURE 

Use this on the first time you run the project. 

1. On the "ev3dev Device Browser", click on "Dowload workspace"
1. On the device, right click and choose "Open SSH Terminal"
1. Run 
   - chmod +x ~/RL_in_EV3/setup_paths
1. Run 
   - ~/RL_in_EV3/setup_libs
1. Run the file (see below)

Attention: if you change the names of directories in "Common" folder or if you create new, you will have to adjust the setup script.


## TO RUN A FILE 
Use this, if you haven't changed since last donwload to EV3 or 
after changes made to "RL_in_EV3" folder only.

1. Hit Ctrl+F5 (on the desired file in EV3_PROJ)
   - the file must start with "#!/usr/bin/env python3"
1. If a problem (runtime error) occurs or if your are using ev3dev-jessie: 
   - on the ev3dev-browser choose "Open SSH Terminal"
   - run: python3 <your-file.py>

 
## EVERYTIME YOU CHANGE FILES IN THE **COMMON** FOLDER

1. On the "ev3dev Device Browser", click on "Dowload workspace"
1. Run the file you want using the procedure above
