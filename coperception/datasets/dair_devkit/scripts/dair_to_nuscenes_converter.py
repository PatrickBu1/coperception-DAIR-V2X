import json
import os
import math
import uuid
from scipy.spatial.transform import Rotation as R
import numpy as np


def generate_samples_and_scenes(coop_json, veh_json, inf_json):
    scene_dict = dict()
    sample_dict = dict()

    scene_count = 0
    scene_sample_count = 0
    total_sample_count = 0

    curr_scene_token = generate_uuid()
    first_sample_token = generate_uuid()

    prev_sample_token = ""
    this_sample_token = first_sample_token
    next_sample_token = generate_uuid()

    prev_batch_id = 0
    curr_batch_id = 0

    for idx, coop in enumerate(coop_json):
        veh_info = None
        inf_info = None

        for veh in veh_json:
            if veh["image_path"][-10:] == coop["vehicle_image_path"][-10:]:
                veh_info = veh

        for inf in inf_json:
            if inf["image_path"][-10:] == coop["infrastructure_image_path"][-10:]:
                inf_info = inf

        if veh_info is None or inf_info is None:
            continue

        if veh_info["batch_id"] == inf_info["batch_id"]:
            curr_batch_id = veh_info["batch_id"]
            avg_timestamp = (int(veh_info["image_timestamp"]) + int(inf_info["image_timestamp"]) +
                             int(veh_info["pointcloud_timestamp"]) + int(inf_info["pointcloud_timestamp"])) // 4
            sample_dict[this_sample_token] = {
                "anns": 0,
                "data": 0,
                "token": this_sample_token,
                "scene_token": curr_scene_token,
                "timestamp": avg_timestamp,
                "veh_img_timestamp": int(veh_info["image_timestamp"]),
                "inf_img_timestamp": int(inf_info["image_timestamp"]),
                "veh_pcd_timestamp": int(veh_info["pointcloud_timestamp"]),
                "inf_pcd_timestamp": int(inf_info["pointcloud_timestamp"]),
                "prev": prev_sample_token,
                "next": ""
            }
            total_sample_count += 1
            scene_sample_count += 1
            if prev_sample_token != "":
                sample_dict[prev_sample_token]["next"] = this_sample_token
        elif idx != len(coop_json) - 1:
            continue

        if ((curr_batch_id != prev_batch_id and scene_count > 0) or (idx == len(coop_json) - 1)) and scene_sample_count >= 10:
            sample_dict[this_sample_token]["prev"] = prev_sample_token if idx == len(coop_json) - 1 else ""
            scene_dict[curr_scene_token] = {
                "first_sample_token": first_sample_token,
                "last_sample_token": this_sample_token if idx == len(coop_json) - 1 else prev_sample_token,
                "name": "scene-{}".format(scene_count if scene_count >= 10 else str(0) + str(scene_count)),
                "nbr_samples": scene_sample_count,
                "token": curr_scene_token
            }
            curr_scene_token = generate_uuid()
            sample_dict[this_sample_token]["scene_token"] = curr_scene_token
            first_sample_token = this_sample_token
            total_sample_count += scene_sample_count
            scene_sample_count = 0
            scene_count += 1

        if scene_count == 0:
            scene_count += 1

        prev_sample_token = this_sample_token
        this_sample_token = next_sample_token
        next_sample_token = generate_uuid()
        prev_batch_id = curr_batch_id

    return scene_dict, sample_dict


def generate_data(scene_dict, sample_dict, veh_json, inf_json):
    data_dict = dict()

    for scene_token in scene_dict:
        curr_scene = scene_dict[scene_token]

        curr_sample_token = curr_scene["first_sample_token"]
        scene_finished = False

        prev_veh_img_token = ""
        curr_veh_img_token = generate_uuid()
        prev_veh_pcd_token = ""
        curr_veh_pcd_token = generate_uuid()
        prev_inf_img_token = ""
        curr_inf_img_token = generate_uuid()
        prev_inf_pcd_token = ""
        curr_inf_pcd_token = generate_uuid()

        while not scene_finished:
            # the following is data for one sample
            veh_img_path = ""
            veh_img_timestamp = 0
            veh_pcd_path = ""
            veh_pcd_timestamp = 0
            inf_img_path = ""
            inf_img_timestamp = 0
            inf_pcd_path = ""
            inf_pcd_timestamp = 0

            for v in veh_json:
                if int(v["image_timestamp"]) == sample_dict[curr_sample_token]["veh_img_timestamp"]:
                    veh_img_path = v['image_path']
                    veh_img_timestamp = v["image_timestamp"]
                    veh_pcd_path = v['pointcloud_path']
                    veh_pcd_timestamp = v["pointcloud_timestamp"]

            for i in inf_json:
                if int(i["image_timestamp"]) == sample_dict[curr_sample_token]["inf_img_timestamp"]:
                    inf_img_path = i['image_path']
                    inf_img_timestamp = i["image_timestamp"]
                    inf_pcd_path = i['pointcloud_path']
                    inf_pcd_timestamp = i["pointcloud_timestamp"]

            data_dict[curr_veh_img_token] = {
                "calibrated_sensor_token": 0, "ego_pose_token": 0, "fileformat": "jpg",
                "filename": "vehicle-side/"+veh_img_path, "height": 1080, "is_key_frame": True, "next": "",
                "prev": prev_veh_img_token, "sample_token": curr_sample_token, "timestamp": veh_img_timestamp,
                "token": curr_veh_img_token, "width": 1920
            }

            data_dict[curr_veh_pcd_token] = {
                "calibrated_sensor_token": 0, "ego_pose_token": 0, "fileformat": "pcd",
                "filename": "vehicle-side/"+veh_pcd_path,
                "height": 0, "is_key_frame": True, "next": "", "prev": prev_veh_pcd_token,
                "sample_token": curr_sample_token, "timestamp": veh_pcd_timestamp, "token": curr_veh_pcd_token,
                "width": 0
            }

            data_dict[curr_inf_img_token] = {
                "calibrated_sensor_token": 0, "ego_pose_token": 0, "fileformat": "jpg",
                "filename": "infrastructure-side/"+inf_img_path,
                "height": 1080, "is_key_frame": True, "next": "", "prev": prev_inf_img_token,
                "sample_token": curr_sample_token, "timestamp": inf_img_timestamp, "token": curr_inf_img_token,
                "width": 1920
            }

            data_dict[curr_inf_pcd_token] = {
                "calibrated_sensor_token": 0, "ego_pose_token": 0, "fileformat": "pcd",
                "filename": "infrastructure-side/"+inf_pcd_path,
                "height": 0, "is_key_frame": True, "next": "", "prev": prev_inf_pcd_token,
                "sample_token": curr_sample_token, "timestamp": inf_pcd_timestamp, "token": curr_inf_pcd_token,
                "width": 0
            }

            sample_dict[curr_sample_token]["data"] = {
                "CAM_FRONT_0": curr_veh_img_token,
                "CAM_FRONT_1": curr_inf_img_token,
                "LIDAR_TOP_0": curr_veh_pcd_token,
                "LIDAR_TOP_1": curr_inf_pcd_token
            }

            if prev_veh_img_token != "" and prev_inf_img_token != "":
                data_dict[prev_veh_img_token]["next"] = curr_veh_img_token
                data_dict[prev_veh_pcd_token]["next"] = curr_veh_pcd_token
                data_dict[prev_inf_img_token]["next"] = curr_inf_img_token
                data_dict[prev_inf_pcd_token]["next"] = curr_inf_pcd_token

            if curr_sample_token == curr_scene["last_sample_token"]:
                scene_finished = True


            curr_sample_token = sample_dict[curr_sample_token]["next"]
            prev_veh_img_token = curr_veh_img_token
            prev_veh_pcd_token = curr_veh_pcd_token
            prev_inf_img_token = curr_inf_img_token
            prev_inf_pcd_token = curr_inf_pcd_token

            curr_veh_img_token = generate_uuid()
            curr_veh_pcd_token = generate_uuid()
            curr_inf_img_token = generate_uuid()
            curr_inf_pcd_token = generate_uuid()

    return sample_dict, data_dict


def generate_ego_pose_and_calib(dataroot, data_dict, veh_json, inf_json):
    # sample_dict = json.load(open("../metadata/sample_2.json"))
    calib_dict = dict()
    ego_pose_dict = dict()
    # data_map = {
    #     "CAM_FRONT_O": "image_timestamp",
    #     "CAM_FRONT_1": "image_timestamp",
    #     "LIDAR_TOP_O": "pointcloud_timestamp",
    #     "LIDAR_TOP_1": "pointcloud_timestamp"
    # }
    #
    # for sample_key in sample_dict:
    #     sample_data = sample_dict[sample_key]["data"]
    #     for data_token in sample_data:
    #         timestamp =
    #
    for data_key in data_dict:
        data_category = data_dict[data_key]["filename"][0] # vehicle (v) or infrastructure (i)
        assert data_category == "v" or data_category == "i"
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
                    sensor_token = "0"

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
                    sensor_token = "2"

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
                    sensor_token = "1"

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
                    sensor_token = "3"

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

    return ego_pose_dict, calib_dict, data_dict


def generate_uuid():
    i = str(uuid.uuid4())
    i = i.replace("-", "")
    return i

def vertices_to_rotation(point_matrix):
    four_pts = point_matrix[0:4]
    x = four_pts[:, 0]
    y = four_pts[:, 1]
    z = four_pts[:, 2]

    zero_ref = [i for i in point_matrix[0]]

    for i in range(4):
        x[i] -= zero_ref[0]
        y[i] -= zero_ref[1]
        z[i] -= zero_ref[2]

    z_angle = math.atan2(y[2], x[2])
    # y_angle = math.atan2(z[2], x[2])
    # x_angle = math.atan2(z[2], y[2])

    r = R.from_rotvec(np.array([0, 0, z_angle])).as_quat()
    return r.tolist()


def generate_anns(dataroot, coop_json, samples_json, data_json):
    type_dict = {
        "car": "0",
        "truck": '1',
        "van": "2",
        "bus": "3",
        "pedestrian": "4",
        "cyclist": "5",
        "tricyclist": "6",
        "motorcyclist": "7",
        "barrow": "8",
        "trafficcone": "9",
        "unknowns_movable": "10"
    }

    visibility_dict = {
        "00": "0",
        "01": "1",
        "02": "2",
        "10": "3",
        "11": "4",
        "12": "5",
        "20": "6",
        "21": "7",
        "22": "8"
    }

    anns_dict = dict()

    for sample_key in samples_json:
        veh_img_data_token = samples_json[sample_key]["data"]["CAM_FRONT_0"]
        veh_img_path = data_json[veh_img_data_token]["filename"][-10:]

        sample_anns = []
        for coop in coop_json:
            if coop["vehicle_image_path"][-10:] == veh_img_path:
                coop_labels = json.load(open(os.path.join(dataroot, coop["cooperative_label_path"])))

                prev_ann_token = ""
                next_ann_token = generate_uuid()

                for idx, label in enumerate(coop_labels):
                    attribute_token = type_dict[label["type"]]
                    t_state = str(label["truncated_state"])
                    t_state = "2" if t_state == "3" else t_state
                    visibility_token = visibility_dict[t_state + str(label["occluded_state"])]
                    world_loc_3d = [label["3d_location"][c] for c in ["x", "y", "z"]]
                    dim_3d = [label["3d_dimensions"][c] for c in ["w", "l", "h"]]
                    world_8_points = np.array(label["world_8_points"])
                    rotation = vertices_to_rotation(world_8_points[0:4])
                    rotation = [rotation[i] for i in range(1, 4)] + [rotation[0]]

                    this_ann_token = next_ann_token
                    next_ann_token = generate_uuid()

                    curr_ann = {
                        "token": this_ann_token,
                        "sample_token": sample_key,
                        "attribute_token": attribute_token,
                        "visibility_token": visibility_token,
                        "translation": world_loc_3d,
                        "size": dim_3d,
                        "rotation": rotation,
                        "num_lidar_pts": 0,
                        "world_8_pts": world_8_points.tolist(),
                        "prev": prev_ann_token,
                        "next": "" if idx == len(coop_labels) else next_ann_token
                    }

                    prev_ann_token = this_ann_token
                    sample_anns.append(this_ann_token)
                    anns_dict[this_ann_token] = curr_ann

        samples_json[sample_key]["anns"] = sample_anns

        anns_dict_fh = dict(list(anns_dict.items())[:len(anns_dict) // 2])
        anns_dict_lh = dict(list(anns_dict.items())[len(anns_dict) // 2:])

    return samples_json, anns_dict_fh, anns_dict_lh


if __name__ == "__main__":
    dataroot = r"C:\Users\jnynt\Desktop\AI4CE\data\cooperative-vehicle-infrastructure"
    coop_json = json.load(open(os.path.join(dataroot, "cooperative\data_info.json")))
    coop_json = sorted(coop_json, key=lambda x: int(x["vehicle_pointcloud_path"][-10: -4]))
    veh_json = json.load(open(os.path.join(dataroot, "vehicle-side/data_info.json")))
    inf_json = json.load(open(os.path.join(dataroot, "infrastructure-side/data_info.json")))

    # scene, sample = generate_samples_and_scenes(coop_json, veh_json, inf_json)
    #
    # sample_2, data = generate_data(scene, sample, veh_json, inf_json)
    # ego_pose, calib, data_2 = generate_ego_pose_and_calib(data, veh_json, inf_json)

    sample_2 = json.load(open("../metadata/sample_2.json"))
    data_2 = json.load(open("../metadata/data_2.json"))

    sample_3, anns_fh, anns_lh = generate_anns(dataroot, coop_json, sample_2, data_2)

    with open("../metadata/sample_3.json", 'w') as out_sample:
        json.dump(sample_3, out_sample)

    with open("../metadata/anns.json", 'w') as out_anns_fh:
        json.dump(anns_fh, out_anns_fh)

    with open("../metadata/anns_lh.json", 'w') as out_anns_lh:
        json.dump(anns_lh, out_anns_lh)




