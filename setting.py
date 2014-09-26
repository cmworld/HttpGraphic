# -*- coding: utf-8 -*-

import os

DEBUG = True

LOG_FILE = './error.log'
LOG_LEVEL = 10

UPLOAD_PATH = '图片存储绝对路径'
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

LOCALSTORAGE = True


filename_template = {
    "resize_wh" : "{name}_{width}_{height}{ext}",
    "resize_w"  : "{name}_w{width}{ext}",
    "resize_h"  : "{name}_h{height}{ext}",
    "cut_wh"    : "{name}_c_{width}_{height}{ext}"
}