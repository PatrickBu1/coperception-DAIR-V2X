import uuid
import json
import os


def generate_uuid():
    i = str(uuid.uuid4())
    i = i.replace("-", "")
    return i


def generate_samples_and_scenes():
    dataroot = r"C:\Users\jnynt\Desktop\AI4CE\data\cooperative-vehicle-infrastructure"
    coop_json = json.load(open(os.path.join(dataroot, "cooperative\data_info.json")))
    coop_json = sorted(coop_json, key=lambda x: int(x["vehicle_pointcloud_path"][-10: -4]))
    veh_json = json.load(open(os.path.join(dataroot, "vehicle-side/data_info.json")))
    inf_json = json.load(open(os.path.join(dataroot, "infrastructure-side/data_info.json")))

    scene_dict = dict()
    sample_dict = dict()

    scene_count = 0
    sample_count = 0
    sample_sum = 0

    curr_scene_token = generate_uuid()
    first_sample_token = generate_uuid()

    prev_sample_token = ""
    next_sample_token = first_sample_token

    veh_batch_id = -1
    inf_batch_id = -1
    unfound_count = 0

    for i in range(len(coop_json)):
        veh_root = coop_json[i]["vehicle_image_path"][-16:]
        inf_root = coop_json[i]["infrastructure_image_path"][-16:]

        curr_veh_batch_id = 0
        curr_inf_batch_id = 0
        curr_veh_img_timestamp = 0
        curr_veh_pcd_timestamp = 0
        curr_inf_img_timestamp = 0
        curr_inf_pcd_timestamp = 0

        veh_found_flag = False
        inf_found_flag = False

        for j in range(len(veh_json)):
            if veh_json[j]["image_path"] == veh_root:
                veh_found_flag = True
                curr_veh_batch_id = veh_json[j]["batch_id"]
                curr_veh_img_timestamp = int(veh_json[j]["image_timestamp"])
                curr_veh_pcd_timestamp = int(veh_json[j]["pointcloud_timestamp"])

        for j in range(len(inf_json)):
            if inf_json[j]["image_path"] == inf_root:
                inf_found_flag = True
                curr_inf_batch_id = inf_json[j]["batch_id"]
                curr_inf_img_timestamp = int(inf_json[j]["image_timestamp"])
                curr_inf_pcd_timestamp = int(veh_json[j]["pointcloud_timestamp"])

        if veh_found_flag == False or inf_found_flag == False:
            unfound_count += 1
            continue

        this_sample_token = next_sample_token
        avg_timestamp = (curr_veh_img_timestamp + curr_inf_img_timestamp +
                         curr_veh_pcd_timestamp + curr_inf_pcd_timestamp) // 4
        sample_dict[this_sample_token] = {
            "anns": 0,
            "data": 0,
            "token": this_sample_token,
            "scene_token": curr_scene_token,
            "timestamp": avg_timestamp,
            "veh_img_timestamp": curr_veh_img_timestamp,
            "inf_img_timestamp": curr_inf_img_timestamp,
            "veh_pcd_timestamp": curr_veh_pcd_timestamp,
            "inf_pcd_timestamp": curr_inf_pcd_timestamp,
            "next": "",
            "prev": prev_sample_token
        }

        next_sample_token = generate_uuid()

        if curr_veh_batch_id != veh_batch_id and curr_inf_batch_id != inf_batch_id:
            veh_batch_id = curr_veh_batch_id
            inf_batch_id = curr_inf_batch_id

            if scene_count > 0:
                sample_dict[this_sample_token]["prev"] = ""
                scene_entry = {
                    "first_sample_token": first_sample_token,
                    "last_sample_token": prev_sample_token,
                    "name": "scene-{}".format(scene_count if scene_count >= 10 else str(0) + str(scene_count)),
                    "nbr_samples": sample_count,
                    "token": curr_scene_token
                }
                scene_dict[curr_scene_token] = scene_entry
                curr_scene_token = generate_uuid()
                sample_dict[this_sample_token]["scene_token"] = curr_scene_token
                first_sample_token = this_sample_token
                sample_sum += sample_count
                sample_count = 0

            scene_count += 1

        elif i == len(coop_json)-1:
            scene_entry = {
                "first_sample_token": first_sample_token,
                "last_sample_token": this_sample_token,
                "name": "scene-{}".format(scene_count if scene_count >= 10 else str(0) + str(scene_count)),
                "nbr_samples": sample_count + 1,
                "token": curr_scene_token
            }
            scene_dict[curr_scene_token] = scene_entry
            sample_dict[this_sample_token]["scene_token"] = curr_scene_token
            sample_sum += sample_count + 1

        elif prev_sample_token != "":
            sample_dict[prev_sample_token]["next"] = this_sample_token

        prev_sample_token = this_sample_token
        sample_count += 1

    with open('scenes.json', 'w') as out_scene:
        json.dump(scene_dict, out_scene)

    with open('samples.json', 'w') as out_sample:
        json.dump(sample_dict, out_sample)

    print("unfound: ", unfound_count)


if __name__ == "__main__":
    generate_samples_and_scenes()