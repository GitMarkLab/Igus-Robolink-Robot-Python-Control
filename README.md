### Class_IgusRobolink.py
This is a basic class to initialize and run the Igus Robolink Robot based on the CRI Interface from Common Place Robotics. In my case it is an RL-DCi-5S-M  

## It has the following capabilities:  
- Initialize and automatic check if the robot is already referenced. Otherwise it will automatically run an referencing sequence  
- run in cartesien coordinates to a relative (moveo) or absolute position (move) position. The callback is "done" if a defined position is reached
- control an digital IO (i have a magnet atteched

## Limitations
- Init and connect process is controlled via time.sleep (delay) and not based on an connected callback
- if a position is not reached the system will hang in a while loop

## further Links
https://wiki.cpr-robots.com/images/8/81/CPR_RobotInterfaceCRI_V17.pdf

  
