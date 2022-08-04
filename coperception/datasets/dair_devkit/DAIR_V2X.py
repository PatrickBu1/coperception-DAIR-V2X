import json
import math
import os
import sys
import time
import re
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

        if self.version not in ["V2X_C_coop", "V2X_C_inf", "V2X_C_veh", "V2X_I", "V2X_V"]:
            raise AttributeError("version must be from the following:\n"
                                 "\"V2X_C_coop:\" - cooperative data under DAIR-V2X-C\n"
                                 "\"V2X_C_inf\" - infrastructure-only data under DAIR-V2X-C\n"
                                 "\"V2X_C_veh\" - vehicle-only data under DAIR-V2X-C\n"
                                 "\"V2X_I\" - infrastructure-only DAIR-V2X-I dataset\n"
                                 "\"V2X_V\" - vehicle-only DAIR-V2X-V dataset\n"
                                 )

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
            print("Loading DAIR-V2X tables...")

        metadata_base_path = "metadata"
        self.metadata_list = ["sample", "data", "ego_pose", "calibrated_sensor",
                     "sample_annotation", "attribute", "sensor", "visibility", "category"]
        self._metadata = dict()

        self.scenes = json.load(open(os.path.join(metadata_base_path, "scenes.json")))
        for name in self.metadata_list:
            self._metadata[name] = json.load(open(os.path.join(metadata_base_path, name + ".json")))

        load_time = round(time.time() - start_load_time, 3)
        if verbose:
            for name in self.metadata_list:
                print(len(self._metadata[name]), name)
            print("Done loading in", load_time, "seconds")

    def get(self, entity_name: str, token: str):
        if type(entity_name) != str:
            raise TypeError("entity name should be type string")
        self._check_token_format(token)
        if entity_name not in self.metadata_list:
            raise KeyError("entity name is not valid")

        data_unprocessed = self._metadata[entity_name][token]
        # TODO: modify the unprocessed data based on its category
        return data_unprocessed

    def list_scenes(self):
        for scene in self.scenes.values():
            tm = int(self._metadata["samples"][scene["first_sample_token"]]["timestamp"][0:10])
            duration = int(self._metadata["samples"][scene["last_sample_token"]]["timestamp"][0:10]) - tm
            anns_count = 0
            next_sample_token = scene["first_sample_token"]
            while next_sample_token != "":
                sample = self._metadata[next_sample_token]
                anns_count += len(sample["anns"])
                next_sample_token = sample["next"]

            print(scene["name"], end=", ")
            print("["+str(dt.datetime.utcfromtimestamp(tm))+"] ", end=", ")
            print(str(duration)+"s", end=", ")
            print("#anns:", anns_count)

    def list_sample(self, token: str):
        self._check_token_format()
        if token not in self._metadata["sample"]:
            raise KeyError("Token provided is not a sample token")

        sample = self._metadata["sample"][token]
        print("Sample: ", sample["token"])

        for data_name in sample["data"]:
            print("sample_data_token:", sample["data"][data_name], end=", ")
            print("mod:", "camera" if data_name[0] == "C" else "lidar", end=", ")
            print("channel:", data_name)

        for ann_token in sample["anns"]:
            print("sample_annotation_token:", ann_token, end=", ")
            category = self._metadata["attribute"][self._metadata["sample_annotation"]["attribute_token"]]["name"]
            print("category: ", category)

    def _check_token_format(self, token: str):
        if type(token) != str or (len(token) != 32 and not bool(re.match("[a-z\d]", token))):
            raise err.FormatError("token is of the wrong format")

    def _check_file_integrity(self, dataroot, version):
        fs = json.load(open("./{}_metadata/file_structure.json".format(version)))
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






