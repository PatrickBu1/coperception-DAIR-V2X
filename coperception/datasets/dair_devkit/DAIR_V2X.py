import json
import math
import os
import sys
import time
import re
import copy
import cv2
import matplotlib.pyplot as plt
import numpy as np
import sklearn.metrics
from PIL import Image
from matplotlib import rcParams
from matplotlib.axes import Axes
from pyquaternion import Quaternion
from tqdm import tqdm
import datetime as dt

import misc.errors as err

if sys.version_info[0] != 3:
    raise ValueError("DAIR-V2X dev-kit only supports Python version 3.")

class DAIR_V2X:
    def __init__(self,
                 dataroot: str,
                 verbose: bool=True,
                 ):
        self.dataroot = dataroot
        self.verbose = verbose

        start_load_time = time.time()
        if verbose:
            print("Checking file integrity of data under dataroot...")

        try:
            self._check_file_integrity(dataroot)
        except Exception:
            raise FileNotFoundError(
                "The dataset files are either incomplete or redundant.\n"
                "To obtain the correct file structure, please refer to \n"
                " the website: https://thudair.baai.ac.cn"
            )

        if verbose:
            print("======")
            print("Loading DAIR-V2X tables...")

        metadata_base_path = "metadata"
        self.metadata_map = {
            "scene": "scene.json",
            "sample": "sample_3.json",
            "sample_data": "data_2.json",
            "ego_pose": "ego_pose.json",
            "calibrated_sensor": "calibrated_sensor.json",
            "sample_annotation": "anns.json",
            "attribute": "attribute.json",
            "sensor": "sensor.json",
            "visibility": "visibility.json"
        }

        self._meta = dict()

        for name in self.metadata_map:
            self._meta[name] = json.load(open(os.path.join(metadata_base_path, self.metadata_map[name])))

        self._scene = copy.deepcopy(list(self._meta["scene"].values()))

        anns_lh = json.load(open("./metadata/anns_lh.json"))
        self._meta["sample_annotation"].update(anns_lh)

        load_time = round(time.time() - start_load_time, 3)
        if verbose:
            print(len(self._scene), "scene, ")
            for name in self.metadata_map:
                print(len(self._meta[name]), name, end=",\n")
            print("Done loading in", load_time, "seconds")
            print("======")

    @property
    def scene(self):
        return copy.deepcopy(self._scene)

    @property
    def visibility(self):
        return copy.copy(list(self._meta["visibility"].values()))

    @property
    def sensor(self):
        return copy.copy(list(self._meta["sensor"].values()))

    def get(self, entity_name: str, token: str):
        if type(entity_name) != str:
            raise TypeError("entity name should be type string")
        self._check_token_format(token)
        if entity_name not in self.metadata_map:
            raise KeyError("entity name is not valid")

        data_unprocessed = self._meta[entity_name][token]
        # TODO: modify the unprocessed data based on its category
        return data_unprocessed

    def list_scenes(self):
        for scene in self._scene.values():
            tm = int(str(self._meta["sample"][scene["first_sample_token"]]["timestamp"])[0:10])
            duration = int(str(self._meta["sample"][scene["last_sample_token"]]["timestamp"])[0:10]) - tm
            anns_count = 0
            next_sample_token = scene["first_sample_token"]
            while next_sample_token != "":
                sample = self._meta["sample"][next_sample_token]
                anns_count += len(sample["anns"])
                next_sample_token = sample["next"]

            print(scene["name"], end=", ")
            print("["+str(dt.datetime.utcfromtimestamp(tm))+"] ", end=", ")
            print(str(duration)+"s", end=", ")
            print("#anns:", anns_count)

    def list_sample(self, token: str):
        self._check_token_format(token)
        if token not in self._meta["sample"]:
            raise KeyError("Token provided is not a sample token")

        sample = self._meta["sample"][token]
        print("Sample: ", sample["token"])

        for data_name in sample["data"]:
            print("sample_data_token:", sample["data"][data_name], end=", ")
            print("mod:", "camera" if data_name[0] == "C" else "lidar", end=", ")
            print("channel:", data_name)

        for ann_token in sample["anns"]:
            print("sample_annotation_token:", ann_token, end=", ")
            category = self._meta["attribute"][self._meta["sample_annotation"][ann_token]["attribute_token"]]["name"]
            print("category: ", category)

    def list_attributes(self):
        attr_counts = [0 for i in range(11)]
        for ann_token in self._meta["sample_annotation"]:
            ann = self._meta["sample_annotation"][ann_token]
            attr_counts[int(ann["attribute_token"])] += 1
        for i, count in enumerate(attr_counts):
            print(self._meta["attribute"][str(i)]["name"] + ":", count)

    def _check_token_format(self, token: str):
        if type(token) != str or (len(token) != 32 and not bool(re.match("[a-z\d]", token))):
            raise err.FormatError("token is of the wrong format")

    def _check_file_integrity(self, dataroot):
        fs = json.load(open("./metadata/file_structure.json"))
        for root, dirs, files in os.walk(dataroot, topdown=True):
            curr_node = fs
            root_dir = root[len(dataroot):]
            root_dir = root_dir.replace("\\", "/")
            root_dir = list(filter(('').__ne__, root_dir.split('/')))

            for entry in root_dir:
                curr_node = curr_node[entry]

            if isinstance(curr_node, int) and len(files) != curr_node:
                raise Exception

            elif isinstance(curr_node, dict):
                elems = list(curr_node.keys())
                count = len(elems)
                for folder in dirs:
                    if folder in elems:
                        elems.remove(folder)
                        count -= 1
                for file in files:
                    if file in elems:
                        elems.remove(file)
                        count -= 1
                if len(elems) != 0 or count < 0:
                    raise Exception







