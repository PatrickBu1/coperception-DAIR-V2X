import json
import os
import math
impor





if __name__ == "__main__":
    os.chdir(r"C:\Users\jnynt\Desktop\AI4CE\data\cooperative-vehicle-infrastructure")
    coop_json = json.load(open("cooperative\data_info.json"))
    coop_json = sorted(coop_json, key=lambda x: int(x["vehicle_pointcloud_path"][-10: -4]))
    veh_json = json.load(open(os.path.join(dataroot, "vehicle-side/data_info.json")))
    inf_json = json.load(open(os.path.join(dataroot, "infrastructure-side/data_info.json")))