import json
import math
import os
import sys
import time
import cv2
import matplotlib.pyplot as plt
import numpy as np
import sklearn.metrics
from PIL import Image
from matplotlib import rcParams
from matplotlib.axes import Axes
from pyquaternion import Quaternion
from tqdm import tqdm

if sys.version_info[0] != 3:
    raise ValueError("DAIR-V2X dev-kit only supports Python version 3.")

class DAIRV2X:
    def __init__(self,
                 dataroot: str,
                 version: str="v2x-c",
                 verbose: bool=True,
                 ):
        self.dataroot = dataroot
        self.version = version
        self.verbose = verbose



