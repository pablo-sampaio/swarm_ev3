
To run this project, first your EV3 must be connected using the 
ev3dev-browser (VS Code extesion).

TO RUN A FILE (after changes in RL_in_EV3, except for 1st time)
---------------------------------------------------------------
1) Hit Ctrl+F5 (on the desired file in EV3_PROJ)
   - the file must start with "#!/usr/bin/env python3"
2) If a problem (runtime error) occurs: 
   - on the ev3dev-browser choose "Open SSH Terminal"
   - run: python3 <your-file.py>

 
EVERYTIME YOU CHANGE FILES IN *OTHER* PROJECTS
----------------------------------------------
1) On the "ev3dev Device Browser", click on "Dowload workspace"
2) Run the file


TO CONFIGURE ON THE 1st TIME
----------------------------
1) On the "ev3dev Device Browser", click on "Dowload workspace"
2) Connect to SSH shell
3) Run 
   chmod +x ~/RL_in_EV3/setup_libs
4) Run 
   ~/RL_in_EV3/setup_libs
5) Run the file