from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# Android Emulator Config
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1920
SCREEN_CHANNEL = 4
SCREEN_TOP_HEAD = 63
SCREEN_BOTTOM_HEAD = 126
# screen config
ADJACENT_BOUNDING_BOX_THRESHOLD = 3
NORM_VERTICAL_NEIGHBOR_MARGIN = 0.01
NORM_HORIZONTAL_NEIGHBOR_MARGIN = 0.01
INPUT_ACTION_UPSAMPLE_RATIO = 1
# XML screen config
# [CARBON-RETEST] Upstream's README says to set these to the device size. The
# harness reads the emulator's size from `adb shell wm size` and passes it in;
# the old run left the 1440x2960 default on a 1080x2280 Pixel 4.
import os
XML_SCREEN_WIDTH = int(os.environ.get("XML_SCREEN_WIDTH", 1440))
XML_SCREEN_HEIGHT = int(os.environ.get("XML_SCREEN_HEIGHT", 2960))