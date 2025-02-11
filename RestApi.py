from flask import Flask, request, jsonify
from Class_IgusRobolink import IgusRobolink 
import time
from time import sleep
import multiprocessing

app = Flask(__name__)

# basic commands to run the robot via Rest API

## curl -X POST http://localhost:5000/connect
## curl -X POST http://localhost:5000/enable
## curl -X POST http://localhost:5000/reference

#curl -X POST http://localhost:5000/move \
#     -H "Content-Type: application/json" 
#     -d '{
#           "x": 246.3,
#           "y": 356.3 ,
#           "z": 201.3,
#           "rx": -350.22,
#           "ry": -0.42,
#           "rz": 359.97,
#           "speed": 10
#         }'

## robot.moveo(240.0 ,165.9 ,176.7, -350.18, -0.0 ,360.0,10) ## referenzing position
#curl -X POST http://localhost:5000/move \
#     -H "Content-Type: application/json" \
#     -d '{
#           "x": 240.0 ,
#           "y": 165.9  ,
#           "z": 176.7,
#          "rx": -350.18,
#           "ry": -0.0,
 #          "rz": 360.0,
#           "speed": 10
#         }'

robot = IgusRobolink("192.168.3.11")

@app.route('/connect', methods=['POST'])
def connect():
    print("Rest Connect")
    try:
        robot.connect()
        return jsonify({"status": "success", "message": "Robot connected"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/disconnect', methods=['POST'])
def disconnect():
    print("Rest Disconnect")
    try:
        robot.disconnect()
        return jsonify({"status": "success", "message": "Robot connected"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/enable', methods=['POST'])
def enable():
    try:
        robot.enable()
        return jsonify({"status": "success", "message": "Robot enabled"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/reference', methods=['POST'])
def reference_all_joints():
    try:
        robot.ReferenceAllJoints()
        return jsonify({"status": "success", "message": "All joints referenced"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/motion_type', methods=['POST'])
def motion_type():
    try:
        motion_type = request.json.get("type", "cartesian")
        #robot.motion_type(motion_type)
        return jsonify({"status": "success", "message": f"Motion type set to {motion_type}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/move', methods=['POST'])
def move():
    try:
        data = request.json
        x = data.get("x", 0)
        y = data.get("y", 0)
        z = data.get("z", 0)
        rx = data.get("rx", 0)
        ry = data.get("ry", 0)
        rz = data.get("rz", 0)
        speed = data.get("speed", 100)
        print(data)
        robot.moveo(x, y, z, rx, ry, rz, speed)
        return jsonify({"status": "success", "message": "Movement executed"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

#curl -X POST http://localhost:5000/coordinates \
#-H "Content-Type: application/json" \
#-d '{
#  "coordinates": [
#    [240.0, 165.9, 176.7],
#    [280.0, 200, 176.7],
#    [240.0, 165.9, 176.7]
#  ]
#}'

@app.route('/coordinates', methods=['POST'])
def receive_coordinates():
    try:
        coordinates = request.json.get("coordinates", [])
        if not isinstance(coordinates, list) or not all(isinstance(coord, list) and len(coord) == 3 for coord in coordinates):
            return jsonify({"status": "error", "message": "Invalid format. Expected [[x,y,z], [x,y,z], [x,y,z]]"}), 400

        print(f"Received coordinates: {coordinates}")
        # TODO --> speed setpoint
        for coordinate in coordinates:  
            position = robot.get_status('RelativePosition')
            position_values = [float(x) for x in position.split()]
            new_pos = {
                "x":coordinate[0],
                "y":coordinate[1],
                "z":coordinate[2],
                "rx":position_values[3],
                "ry":position_values[4],
                "rz":position_values[5],
    
            }
            print("new posion from Array: ",new_pos)
            speed = 10
            robot.moveo(
                        new_pos["x"], 
                        new_pos["y"], 
                        new_pos["z"], 
                        new_pos["rx"], 
                        new_pos["ry"], 
                        new_pos["rz"], 
                        speed)
            
            return jsonify({"status": "success", "message": "Coordinates received", "data": coordinates})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# curl -X GET http://localhost:5000/position
@app.route('/position', methods=['GET'])
def get_position():
    try:
        position = robot.get_status('RelativePosition')
        position_values = [float(x) for x in position.split()]

        response = {
            "x": position_values[0],
            "y": position_values[1],
            "z": position_values[2],
            "rx": position_values[3],
            "ry": position_values[4],
            "rz": position_values[5]
        }
        
        return jsonify({"status": "success", "position": response})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



if __name__ == '__main__':

    app.run(host='localhost', port=5000)
    #app.run(host='0.0.0.0', port=5000)    
