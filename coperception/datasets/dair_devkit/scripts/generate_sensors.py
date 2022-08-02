import uuid
import json

def generate_uuid():
    i = str(uuid.uuid4())
    i = i.replace("-", "")
    return i

def generate_sensors():
    tokens = [generate_uuid() for i in range(4)]
    sensors = {
        tokens[0]: {"token": tokens[0], "channel": "CAM_FRONT_0", "modality": "camera"},
        tokens[1]: {"token": tokens[1], "channel": "CAM_FRONT_1", "modality": "camera"},
        tokens[2]: {"token": tokens[2], "channel": "LIDAR_TOP_0", "modality": "lidar"},
        tokens[3]: {"token": tokens[3], "channel": "LIDAR_TOP_1", "modality": "lidar"},
    }

    with open('sensors.json', 'w') as out_sensors:
        json.dump(sensors, out_sensors)


if __name__ == "__main__":
    generate_sensors()