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


@app.route('/move_positionarray_speed', methods=['POST'])
def move_positionarray_speed():
    try:
        data = request.json
        coordinates = data.get("coordinates", [])
        speed = data.get("speed", 10)  # Default speed is 10 if not provided

        if not isinstance(coordinates, list) or not all(isinstance(coord, list) and len(coord) == 3 for coord in coordinates):
            return jsonify({"status": "error", "message": "Invalid format. Expected coordinates: [[x,y,z], [x,y,z], [x,y,z]]"}), 400

        if not isinstance(speed, (int, float)) or speed <= 0:
            return jsonify({"status": "error", "message": "Invalid speed. Expected a positive number."}), 400

        print(f"Received coordinates: {coordinates}")
        print(f"Received speed: {speed}")

        for coordinate in coordinates:  
            position = robot.get_status('RelativePosition')
            position_values = [float(x) for x in position.split()]
            new_pos = {
                "x": coordinate[0],
                "y": coordinate[1],
                "z": coordinate[2],
                "rx": position_values[3],
                "ry": position_values[4],
                "rz": position_values[5],
            }
            print("New position from Array: ", new_pos)
            
            robot.moveo(
                new_pos["x"], 
                new_pos["y"], 
                new_pos["z"], 
                new_pos["rx"], 
                new_pos["ry"], 
                new_pos["rz"], 
                speed
            )
            
        return jsonify({"status": "success", "message": "Coordinates processed", "data": {"coordinates": coordinates, "speed": speed}})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500







#curl -X POST http://localhost:5000/move_coordinates \
#-H "Content-Type: application/json" \
#-d '{"coordinates": {"x": 12}, "speed": 50}'

#curl -X POST http://localhost:5000/move_coordinates \
#-H "Content-Type: application/json" \
#-d '{"coordinates": {"x": 12, "y": 15, "z": 20}, "speed": 50}'






# curl -X POST http://localhost:5000/move_relative \
# -H "Content-Type: application/json" \
# -d '{
#   "coordinates": {"x": 10, "y": -5, "z": 20},
#   "speed": 50
# }'


@app.route('/move_relative', methods=['POST'])
def move_relative():
    try:
        data = request.json
        offsets = data.get("coordinates", {})
        speed = data.get("speed", 10)

        # Validierung der eingegebenen Koordinaten
        valid_coordinates = ["x", "y", "z", "rx", "ry", "rz"]
        for coord in offsets.keys():
            if coord not in valid_coordinates:
                return jsonify({"status": "error", "message": f"Invalid coordinate: {coord}"})

        # Aktuelle Position abrufen
        position = robot.get_status('RelativePosition')
        position_values = [float(x) for x in position.split()]

        # Mapping der aktuellen Position auf Koordinaten
        current_position = {
            "x": position_values[0],
            "y": position_values[1],
            "z": position_values[2],
            "rx": position_values[3],
            "ry": position_values[4],
            "rz": position_values[5]
        }

        # Aktualisierung der Koordinaten (relative Werte)
        new_position = current_position.copy()
        for coord, offset in offsets.items():
            new_position[coord] += offset

        # Bewegung ausführen mit aktualisierten Werten
        robot.moveo(
            new_position["x"], new_position["y"], new_position["z"],
            new_position["rx"], new_position["ry"], new_position["rz"],
            speed
        )

        return jsonify({
            "status": "success",
            "message": f"Moved by relative offsets",
            "new_position": new_position
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

#curl -X POST http://localhost:5000/move_sleep_position \
#-H "Content-Type: application/json" \
#-d '{"speed": 10}'

@app.route('/move_sleep_position', methods=['POST'])
def move_sleep_position():
    try:
        # Vordefinierte Schlafposition
        sleep_position = {
            "x": 246.3,
            "y": 356.3,
            "z": 201.3,
            "rx": -350.22,
            "ry": -0.42,
            "rz": 359.97
        }
        speed = request.json.get("speed", 10)  # Geschwindigkeit optional aus der Anfrage übernehmen

        # Bewegung zur Schlafposition ausführen
        robot.moveo(
            sleep_position["x"], sleep_position["y"], sleep_position["z"],
            sleep_position["rx"], sleep_position["ry"], sleep_position["rz"],
            speed
        )

        return jsonify({
            "status": "success",
            "message": "Moved to sleep position",
            "sleep_position": sleep_position,
            "speed": speed
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


#curl -X POST http://localhost:5000/move_reference_position \
#-H "Content-Type: application/json" \
#-d '{"speed": 10}'



@app.route('/move_reference_position', methods=['POST'])
def move_reference_position():
    try:
        # Vordefinierte Referenzposition
        reference_position = {
            "x": 240.0,
            "y": 165.9,
            "z": 176.7,
            "rx": -350.18,
            "ry": -0.0,
            "rz": 360.0
        }
        speed = request.json.get("speed", 10)  # Geschwindigkeit optional aus der Anfrage übernehmen

        # Bewegung zur Referenzposition ausführen
        robot.moveo(
            reference_position["x"], reference_position["y"], reference_position["z"],
            reference_position["rx"], reference_position["ry"], reference_position["rz"],
            speed
        )

        return jsonify({
            "status": "success",
            "message": "Moved to reference position",
            "reference_position": reference_position,
            "speed": speed
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':

    app.run(host='localhost', port=5000)
    #app.run(host='0.0.0.0', port=5000)    
