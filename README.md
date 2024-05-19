### Class_IgusRobolink.py
This is a basic class to initialize and run the Igus Robolink Robot.  
It has the following capabilities:  
- Initialize and automatic check if the robot is already referenced. Otherwise it will automatically run an referencing sequence  
- run in cartesien coordinates to a relative (moveo) or absolute position (move). the callback is "done" if a defined position is done
- control an digital IO (i have a magnet atteched

## Limitations
- Init and connect process is controlled via time.sleep (delay) and not based on an connected callback
- if a position is not reached the system will hang in a while loop
  
