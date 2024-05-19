import threading
import time
import socket

#8 Message 564: CRISTART 564 LOGMSG INFO 445370 SocketCAN ReadLoop stopped 

class IgusRobolink:
    def __init__(self,ip, robot_type='robolink_dci'):
        self.robot_type = robot_type
        self.ip = ip
        self.server_address = None
        self.connected = False
        self.thread = None
        self.status = {
            'Status': False, 
            'Enabled': False,
            'PositionReached': False,
            'ReferenceAllReached': False,
            'MotionType': "",
            'Message': "",
            'CRI_Status': "", 
            'GlobalPosition': '',
            'Error':'',
            'GlobalSpeed':'',
            'MotionStatus':''
            
        }
        self.robot_position = {
            'x': 250.00, 
            'y': 0.0,
            'z': 250.00,
            'rx':-180.00,
            'ry':00.00,
            'rz':180.00,  
            'speed':0
                }        
        self.robot_limits={
            'z_min':115.00,
            'z_max':300.00,
            'x_min':130.00,
            'x_max':300.00,            
            'y_min':115.00,
            'y_max':300.00,          
        }
        self.robot_offset={
            'x':420.00,
            'y':-240.00,
            'z':115.00,
            'rx':180.00,
            'ry':0.00,
            'rz':-180.00               
        }         # rx, ry, rz = -179.99, -00.00, 180.00
        self.previous_status = {}
        self.messages_to_send = []

        print("Start thread")
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()   
    
    def connect(self):
        print("Connect")
        #self.ip = ip   
        self.server_address = (self.ip, 3920)
        global sock
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect(self.server_address)
            self.connected = True
            print(f"Connected to {self.ip} using {self.robot_type} ") 
            
        except Exception as e:
            print("Error connecting to robot:", e)       


    def reconnect(self):
        self.connect()   

    def disconnect(self):
        self.disable()
        if self.connected:
            try:
                sock.close()
                self.connected = False
                self.thread.join()  # Wartet, bis der Thread beendet ist
                print("Disconnected")                
                print("Disconnected from robot")
            except Exception as e:
                print("Error disconnecting from robot:", e)            

    def _run(self):
        print("in Thread")
        counter=0
        while True:
            if(self.connected):
                print("Thread connected")
                while True:
                    self.print_status()
                    try:
                        counter+=1
                        if len(self.messages_to_send) > 0:
                            self.command_buffer_write(True)
                        else:
                            self.heartbeat(True)
                        response = "test"
                        if not response:
                            print("Lost connection to robot, attempting to reconnect...")
                            self.reconnect()
                    except Exception as e:
                        print("Error in background thread:", e)
                        self.reconnect()
            else:
                print("Thread not connected")
                time.sleep(0.50)

    def enable(self):
        comm="CRISTART 1234 CMD Enable CRIEND"
        self.command_buffer_fill(comm)
        self.status['Enable'] = True 
        #time.sleep(2.0)


    def reset(self):
        comm="CRISTART 1234 CMD Reset CRIEND"
        self.command_buffer_fill(comm)
        #self.status['Enable'] = True 
        #time.sleep(2.0)
        
        
        
    def disable(self):
        comm="CRISTART 1234 CMD Disable CRIEND"
        self.command_buffer_fill(comm)
        #time.sleep(2.0)

    def enable_magnet(self):
        comm="CRISTART 1234 CMD DOUT 24 true CRIEND"
        self.command_buffer_fill(comm)


    def disable_magnet(self):
        comm="CRISTART 1234 CMD DOUT 24 false CRIEND"
        self.command_buffer_fill(comm)
        time.sleep(2.0)

    def get_status(self,req='all'):
        if req == 'all':
            return self.status
        else:
            return self.status[req]
            
    
    def move_pos(self,pos):
        x=pos['x']
        y=pos['y']   
        z=pos['z']  
        rx=pos['rx']
        ry=pos['ry']
        rz=pos['rz']
        speed=pos['speed']
        self.move(self, x, y, z, rx, ry, rz)

    def Set_Offset(self):
        print(f" current parameter {self.robot_offset}")
        return 0
    
    def moveo(self, x=0, y=0, z=0, rx=0, ry=0, rz=0,speed=0):
        xo = -1*y + self.robot_offset['x']
        yo = x + self.robot_offset['y']
        zo = z + self.robot_offset['z']
        rxo = rx + self.robot_offset['rx']
        ryo = ry + self.robot_offset['ry']
        rzo = rz + self.robot_offset['rz']
 
        return self.move(xo,yo,zo,rxo,ryo,rzo,speed)
    
    def move(self, x=240.00, y=0, z=240, rx=-180, ry=0, rz=180,speed=20):
        if(self.status['ReferenceAllReached']):
            # Startet einen Bewegungsthread
            self.status['PositionReached'] = False
            move_thread = threading.Thread(target=self._move, args=(x, y, z, rx, ry, rz,speed))
            move_thread.start()
            move_thread.join()          
            if self.status['PositionReached']:
                print("done")#("Position reached")
            #print(self.status['PositionReached'])
        else:
            self.status['Message'] = "Biite erst alle Achsen referenzieren"
            print(self.status)

    def _move(self, x, y, z, rx, ry, rz,speed=20):
        self.status['PositionReached'] = False
        #x = self.eval_limit(x,self.robot_limits['x_min'],self.robot_limits['x_max'])
        #y = self.eval_limit(y,self.robot_limits['y_min'],self.robot_limits['y_max'])        
        z = self.eval_limit(z,self.robot_limits['z_min'],self.robot_limits['z_max'])
        
        comm= f"CRISTART 1234 CMD Move Cart {x} {y} {z} {rx} {ry} {rz} 0 0 0 {speed} #base CRIEND"
        self.command_buffer_fill(comm)
        while(self.status['PositionReached'] != True):
            dummy=0
        return self.status['PositionReached']

    def eval_limit(self,value,limit_min,limit_max):
        #print(f"limit  {value}  {limit_min}  {limit_max}")
        if float(value) >= float(limit_max):
            print(f"limit MAX reached value: {value} Limit max: {limit_max}")
            return limit_max
        if float(value) <= float(limit_min):
            print(f"limit MIN reached value: {value} Limit min: {limit_min}")
            return limit_min     
        return value
        

        
    def Set_Limit(self, id='' ,val=130.00 ):
        if id != '':
            self.robot_limits[id]= str(val)
            

    
    
    def SetFlag_ReferenceAllJoints(self,flag):
        self.status['ReferenceAllReached'] = flag

    def SetFlag_PositionReached(self):
        self.status['PositionReached'] = True    
    
    def ReferenceAllJoints(self):
        # Startet einen Bewegungsthread
        self.status['ReferenceAllReached'] = False
        move_thread = threading.Thread(target=self._ReferenceAllJoints)
        move_thread.start()
        move_thread.join() 
        if self.status['ReferenceAllReached']:
            print("Reached")
            self.enable()
                
    
    def _ReferenceAllJoints(self):
        print(f"Reference all joints")

        comm="CRISTART 1234 CMD Enable CRIEND"
        self.command_buffer_fill(comm)
        time.sleep(1.5)
        comm="CRISTART 1234 CMD ReferenceAllJoints CRIEND"
        self.command_buffer_fill(comm)
        
        time.sleep(30)

        self.status['ReferenceAllReached'] = True

    def get_reference_info(self):
        #CRISTART 1234 CMD GetReferencingInfo CRIEND
        comm="CRISTART 1234 CMD GetReferencingInfo CRIEND"
        self.command_buffer_fill(comm)
    
    def set_ros_true(self):
        print("set true")
        self.status['PositionReached'] = True
    
    #["Joint", "CRISTART 1234 CMD MotionTypeJoint CRIEND"],
    #["CartBase", "CRISTART 1234 CMD MotionTypeCartBase CRIEND"],

    def motion_type(self,_type="cartesian"):
        if(_type=="joint"):
            print(_type)
            comm="CRISTART 1234 CMD MotionTypeJoint CRIEND"
            self.command_buffer_fill(comm)
            time.sleep(2.0)
            
        if(_type=="cartesian"):
            print(_type)
            comm="CRISTART 1234 CMD MotionTypeCartBase CRIEND"
            self.command_buffer_fill(comm)
            time.sleep(2.0)    

    

    def command_buffer_fill(self,comm):
        self.messages_to_send.append(comm)
    
    def command_buffer_write(self,log):
        #print("write_command_buffer" + str(len(messages_to_send)))
        if len(self.messages_to_send) > 0:
            for message in self.messages_to_send:
                #####print("-- Sending message:" ,  message)
                self.cri_msg(message,log)
                
        self.messages_to_send.clear()

    def heartbeat(self,log):
        messageAliveJog = "CRISTART 1234 ALIVEJOG 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 CRIEND"
        self.cri_msg(messageAliveJog,log)


    def heartbeat_robot_speed(self,x=0,y=0,z=0,rx=0,ry=0,rz=0,log="False"):
        tes=0
        messageAliveJog = f"CRISTART 1234 ALIVEJOG  {x} {y} {z} {rx} {ry} {rz} 0.0 0.0 0.0 CRIEND" 
        self.cri_msg(messageAliveJog,log)   
        #print_status()

    def cri_msg(self,stg,log):
        callback_str=stg.encode('utf-8')
        ret_str=bytearray(callback_str)
        rec = sock.sendall(ret_str)
    
        response="t"
        if(log):
            response = sock.recv(4096)#1*1024)  # Empfange bis zu 1024 Bytes (kann angepasst werden)
            #print(response)
            self.pars_msg(response)


#################################################################################################
# 0 1 2 3 4 usw
#['CRISTART', '217', 'LOGMSG', 'INFO', '90551', 'CRIServerManager:', 'Client', 'accepted', '']
#['CRISTART', '218', 'LOGMSG', 'INFO', '90552', 'CRI-Server:', 'starting', '']
#len 11 -->['CRISTART', '219', 'LOGMSG', 'INFO', '90552', 'CRIServerManager:', 'Client', 'connected', 'as', 'active', '']

# len 114
#['CRISTART', '23', 'STATUS', 'MODE', 'joint', 'POSJOINTSETPOINT', '11.77', '3.13', '13.11', '73.77', '11.76', '0.00', #'0.00', '0.00', '0.00', '0.00', '0.00', '0.00', '0.0', '0.0', '0.0', '0.0', 'POSJOINTCURRENT', '11.76', '3.13', '13.11', #'73.76', '11.75', '0.00', '0.00', '0.00', '0.00', '0.00', '0.00', '0.00', '0.0', '0.0', '0.0', '0.0', 'POSCARTROBOT', #'240.0', '50.0', '250.0', '-179.99', '0.00', '180.00', 'POSCARTPLATTFORM', '0.0', '0.0', '0.0', 'OVERRIDE', '90.0', 'DIN', #'0', 'DOUT', '0', 'ESTOP', '3', 'SUPPLY', '0', 'CURRENTALL', '0', 'CURRENTJOINTS', '700', '700', '800', '700', '600', '0', #'0', '0', '0', '0', '0', '0', '0', '0', '0', '0', 'ERROR pos79', 'NoError', '0', '0', '0', '0', '0', '0', '512', '512', '512', #'512', '512', '512', '512', '512', '512', '512', 'KINSTATE', '0', 'OPMODE', '-1', 'CARTSPEED', '0.0', 'GSIG', '00', #'FRAMEROBOT', 'base', '240.0', '50.0', '250.0', '-179.99', '0.00', '180.00', '']


#len-------- 101
#['CRISTART', '743', 'VARIABLES', 'ValuePosVariable', 'position', '283.239', '0', '271.723', '180', '3.68871e-05', '180', '0', '10', '0', '80', #'0', '0', '0', '0', '0', 'ValueNrVariable', 'programrunning', '0', 'ValueNrVariable', 'logicprogramrunning', '0', 'ValueNrVariable', 'parts-good', #'0', 'ValueNrVariable', 'parts-bad', '0', 'ValuePosVariable', 'userframe-a', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', #'0', 'ValuePosVariable', 'userframe-b', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', 'ValuePosVariable', 'userframe-#c', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', 'ValuePosVariable', 'position-userframe', '0', '0', '0', '0', '0', #'0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '']

#len-------- 40
#['CRISTART', '32', 'LOGMSG', 'INFO', '531450', 'Temps', 'Board', 'Robot:', '', '', '28.1', '', '', '30.0', '', '', '28.5', '', '', '36.9', '', '', #'33.2', 'Temps', 'Motor', 'Robot:', '', '-25.6', '', '-25.6', '', '-25.6', '', '-25.6', '', '-25.6', 'Temp', 'CPU:', '53.6', '']


#len-------- 63
# at startup when nnot enabled and not referenced    
#['CRISTART', '35', 'LOGMSG', 'INFO', '540155', 'Pos:', '', '', '283.2', '', '', '', '', '0.0', '', '', '271.7', '', '180.0', '', '', '', '0.0', #'', '180.0', '', '', '', 'Joints:', '', '', '', '', '0.0', '', '', '', '10.0', '', '', '', '', '0.0', '', '', '', '80.0', '', '', '', '', '0.0', #'', '', 'Status:', '_MNE_COM,', 'MotionNotAllowed', '', '', 'Prog:', 'Stp,', 'None', '']
    

#len-------- 61
#['CRISTART', '87', 'LOGMSG', 'INFO', '263731', 'Pos:', '', '', '254.1', '', '', '', '', '0.0', '', '', '291.7', '-170.3', '', '', '', '0.0', 
#'-180.0', '', '', '', 'Joints:', '', '', '', '', '0.0', '', '', '', '', '3.3', '', '', '', '', '2.8', '', '', '', '83.9', '', '', '', '-9.7', '', #'', 'Status:', 'NoError,', 'KinOK', '', '', 'Prog:', 'Stp,', 'None', '']

    
    def pars_msg(self,callback_msg):
        messages = callback_msg.split(b'CRIEND\n')
        message_dict = {}
        for i, message in enumerate(messages):
            if message.startswith(b'CRISTART'):
                parts = message.split(b' ')
                parts = [item.decode('utf-8').replace('#', '') for item in parts]

                if len(parts)==63: # only at statup
                    self.status['Error'] = parts[55]
                    self.status['MotionStatus'] = parts[56]
                    
                if len(parts)==61: # only at statup
                    self.status['Error'] = parts[53]
                    self.status['MotionStatus'] = parts[54]

                
                #if len(parts)!=114 and len(parts)!=101 :   
                 #   asda=0
                    #print("len--------",len(parts))
                    #print(parts)
                
                if len(parts)==114:
                    if parts[3] == 'MODE' and parts[22] == 'POSJOINTCURRENT':# and parts[40] == 'POSCARTROBOT':
                        
                        #print(f"  joint pos {parts[22]}  cart pos  {parts[39]}  cart speed  {parts[101]} ERROR  {parts[79]}")
                        self.status['GlobalPosition'] = (
                            parts[40] + " " + 
                            parts[41] + " " + 
                            parts[42] + " " + 
                            parts[43] + " " + 
                            parts[44] + " " + 
                            parts[45]
                        )
                        self.status['Error'] = parts[80]
                        self.status['GlobalSpeed'] = parts[102]

                if len(parts)==9:
                    if parts[6] == 'MoveTo' and parts[7] == 'done' :
                        self.status['PositionReached'] = True
                        #print("Ziel erreicht----###############-------------------------------------------------") 
                
                if len(parts)==11:
                    if parts[5] == 'CRIServerManager:' and parts[9] != '':
                        self.status['CRI_Status'] = parts[9]
                        #print("CRI_Status:   ",self.status['CRI_Status'])# , " len" , len(parts) )                 
    
    def print_status(self):
        if self.has_status_changed():
            status_string = ", ".join([f"{key}: {value}" for key, value in self.status.items()])
            #print(status_string)
            self.update_previous_status()        

    def has_status_changed(self):
        # Überprüfen, ob sich der Status geändert hat
        return self.status != self.previous_status

    def update_previous_status(self):
        # Aktualisieren des vorherigen Status
        self.previous_status = self.status.copy()
