# Script for creating DAIR-V2X metadata - ego pose, sensors, and calibration information
# Does not need to be refactored. This script only runs once during development

import json
import os
import uuid
from scipy.spatial.transform import Rotation as R
import numpy as np

def generate_uuid():
    i = str(uuid.uuid4())
    i = i.replace("-", "")
    return i

def generate_ego_pose_and_calib():
    dataroot = r"C:\Users\jnynt\Desktop\AI4CE\data\cooperative-vehicle-infrastructure"
    data_dict = json.load(open("./data.json"))
    veh_json = json.load(open(os.path.join(dataroot, "vehicle-side/data_info.json")))
    inf_json = json.load(open(os.path.join(dataroot, "infrastructure-side/data_info.json")))

    calib_dict = dict()
    ego_pose_dict = dict()

    for data_key in data_dict:
        data_category = data_dict[data_key]["filename"][0] # vehicle (v) or infrastructure (i)
        data_type = data_dict[data_key]["fileformat"]
        timestamp = str(data_dict[data_key]["timestamp"])

        sensor_token = ""
        ego_translation = None
        ego_rotation = None
        calib_translation = None
        calib_rotation = None
        calib_camera_intrinsic = None

        if data_category == "v":
            for v in veh_json:
                if data_type == "jpg" and v["image_timestamp"] == timestamp:
                    ego_to_world_json = json.load(
                        open(os.path.join(dataroot, "vehicle-side/", v["calib_novatel_to_world_path"])))
                    lidar_to_ego_json = json.load(
                        open(os.path.join(dataroot, "vehicle-side/", v["calib_lidar_to_novatel_path"])))
                    lidar_to_camera_json = json.load(
                        open(os.path.join(dataroot, "vehicle-side/", v["calib_lidar_to_camera_path"])))
                    camera_intrinsic_json = json.load(
                        open(os.path.join(dataroot, "vehicle-side/", v["calib_camera_intrinsic_path"])))
                    sensor_token = "840e57cdaa1847e4952da53df1f1c10a"

                    ego_translation = np.array([n[0] for n in ego_to_world_json["translation"]]).tolist()
                    ego_rotation = R.from_matrix(ego_to_world_json["rotation"]) # a scipy Rotation object
                    lidar_translation = np.array([n[0] for n in lidar_to_ego_json["transform"]["translation"]])
                    lidar_rotation = R.from_matrix(lidar_to_ego_json["transform"]["rotation"])
                    calib_translation = np.subtract(lidar_translation,
                                                    np.array([n[0] for n in lidar_to_camera_json["translation"]])).tolist()
                    calib_rotation = lidar_rotation * R.from_matrix(lidar_to_camera_json["rotation"]).inv()
                    calib_camera_intrinsic = np.array(camera_intrinsic_json["cam_K"])
                    calib_camera_intrinsic = np.reshape(calib_camera_intrinsic, (3, 3)).tolist()

                elif data_type == "pcd" and v["pointcloud_timestamp"] == timestamp:
                    ego_to_world_json = json.load(
                        open(os.path.join(dataroot, "vehicle-side/", v["calib_novatel_to_world_path"])))
                    lidar_to_ego_json = json.load(
                        open(os.path.join(dataroot, "vehicle-side/", v["calib_lidar_to_novatel_path"])))
                    sensor_token = "60e0952fecdc4c97ac3e33d21284e45b"

                    ego_translation = np.array([n[0] for n in ego_to_world_json["translation"]]).tolist()
                    ego_rotation = R.from_matrix(ego_to_world_json["rotation"])
                    calib_translation = np.array([n[0] for n in lidar_to_ego_json["transform"]["translation"]]).tolist()
                    calib_rotation = R.from_matrix(lidar_to_ego_json["transform"]["rotation"])

        elif data_category == "i":
            for i in inf_json:
                if data_type == "jpg" and i["image_timestamp"] == timestamp:
                    lidar_to_world_json = json.load( # ego is the lidar itself
                        open(os.path.join(dataroot, "infrastructure-side/", i["calib_virtuallidar_to_world_path"])))
                    lidar_to_camera_json = json.load(
                        open(os.path.join(dataroot, "infrastructure-side/", i["calib_virtuallidar_to_camera_path"])))
                    camera_intrinsic_json = json.load(
                        open(os.path.join(dataroot, "infrastructure-side/", i["calib_camera_intrinsic_path"])))
                    sensor_token = "9d4a80be31514652b8872e900c8dc91e"

                    ego_translation = np.array([n[0] for n in lidar_to_world_json["translation"]]).tolist()
                    ego_rotation = R.from_matrix(lidar_to_world_json["rotation"])
                    calib_translation = np.subtract(np.array([0, 0, 0]),
                                                     np.array([n[0] for n in lidar_to_camera_json["translation"]])).tolist()
                    calib_rotation = ego_rotation * R.from_matrix(lidar_to_camera_json["rotation"]).inv()
                    calib_camera_intrinsic = np.array(camera_intrinsic_json["cam_K"])
                    calib_camera_intrinsic = np.reshape(calib_camera_intrinsic, (3, 3)).tolist()

                elif data_type == "pcd" and i["pointcloud_timestamp"] == timestamp:
                    lidar_to_world_json = json.load(  # ego is the lidar itself
                        open(os.path.join(dataroot, "infrastructure-side/", i["calib_virtuallidar_to_world_path"])))
                    sensor_token = "5b48b10c9609487facfb366dc742e2cc"

                    ego_translation = np.array([n[0] for n in lidar_to_world_json["translation"]]).tolist()
                    ego_rotation = R.from_matrix(lidar_to_world_json["rotation"])
                    calib_translation = [0, 0, 0]
                    calib_rotation = ego_rotation * ego_rotation.inv()

        ego_pose_token = generate_uuid()
        ego_pose = {
            "rotation": ego_rotation.as_quat().tolist(),
            "token": ego_pose_token,
            "translation": ego_translation,
            "timestamp": int(timestamp)
        }

        calibrated_sensor_token = generate_uuid()
        calibrated_sensor = {
            "token": calibrated_sensor_token,
            "sensor_token": sensor_token,
            "camera_intrinsic": calib_camera_intrinsic,
            "translation": calib_translation,
            "rotation": calib_rotation.as_quat().tolist(),
        }

        data_dict[data_key]["ego_pose_token"] = ego_pose_token
        data_dict[data_key]["calibrated_sensor_token"] = calibrated_sensor_token
        ego_pose_dict[ego_pose_token] = ego_pose
        calib_dict[calibrated_sensor_token] = calibrated_sensor

    with open("ego_pose.json", "w") as out_ego:
        json.dump(ego_pose_dict, out_ego)

    with open("calibrated_sensor.json", "w") as out_calib:
        json.dump(calib_dict, out_calib)

    with open("data_2.json", "w") as out_data:
        json.dump(data_dict, out_data)

if __name__ == "__main__":
    generate_ego_pose_and_calib()