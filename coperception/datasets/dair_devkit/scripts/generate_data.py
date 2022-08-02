import json
import os
import uuid


def generate_uuid():
    i = str(uuid.uuid4())
    i = i.replace("-", "")
    return i


def generate_data():
    sample_dict = json.load(open("./samples.json"))
    scene_dict = json.load(open("./scenes.json"))

    dataroot = r"C:\Users\jnynt\Desktop\AI4CE\data\cooperative-vehicle-infrastructure"
    veh_json = json.load(open(os.path.join(dataroot, "vehicle-side/data_info.json")))
    inf_json = json.load(open(os.path.join(dataroot, "infrastructure-side/data_info.json")))

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

    with open('samples_2.json', 'w') as out_sample:
        json.dump(sample_dict, out_sample)

    with open('data.json', 'w') as out_data:
        json.dump(data_dict, out_data)


if __name__ == "__main__":
    generate_data()






