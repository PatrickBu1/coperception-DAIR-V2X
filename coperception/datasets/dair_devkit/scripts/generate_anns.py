import os
import json
import math
import uuid
import numpy as np
from scipy.spatial.transform import Rotation as R


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


def generate_anns():
    dataroot = r"C:\Users\jnynt\Desktop\AI4CE\data\cooperative-vehicle-infrastructure"
    coop_json = json.load(open(os.path.join(dataroot, "cooperative\data_info.json")))
    coop_json = sorted(coop_json, key=lambda x: int(x["vehicle_pointcloud_path"][-10: -4]))
    samples_json = json.load(open("./samples_2.json"))
    data_json = json.load(open("./data_2.json"))

    type_dict = {
        "car": "44554da304b74c19b80c82900db09066",
        "truck": '18582eee507d42609b071ff51a102277',
        "van": "185b04baea824d079e5de06b11ea8b75",
        "bus": "0fff58d23ef445449819e3fe25c8cc38",
        "pedestrian": "43f33adcfb704e82942fddebc7616d18",
        "cyclist": "e552a4bc742c4e49bdbbaef681e65f19",
        "tricyclist": "48a93acf25824cc58fdf71bba51a0fb2",
        "motorcyclist": "ac701125b312413ab27c04317e72c974",
        "barrow": "cc9d455920724f28b0ce28b4155fe7f4",
        "trafficcone": "0ed81ff7592746e9b554bf1ad7084ca5",
        "unknowns_movable": "656cb07a464444ddb3fc8b23986c5919"
    }

    visibility_dict = {
        "00": "ada0d58e2f954e959014ae45cd741463",
        "01": "783077e6539a4431bcc09da52256872f",
        "02": "17cb249cb5bd46b2a64e1bc4cf14ad6b",
        "10": "cd57f9f6150b4deea942bb17a1acdebf",
        "11": "83e32447d12540cdbb6f358358364212",
        "12": "207faaee2e2c4a0cb372327620a1afd3",
        "20": "8fc94a0c6bd94db8b85a32c77a95e7a0",
        "21": "e232315cde6f4b478429c227c9ded458",
        "22": "a01aa07623204882a229796755996d17"
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

    with open("samples_3.json", "w") as out_sample:
        json.dump(samples_json, out_sample)

    with open("anns.json", "w") as out_anns:
        json.dump(anns_dict, out_anns)


if __name__ == "__main__":
    generate_anns()