#!/usr/bin/env python3

import os
from PIL import Image

images = []
image_paths = ["area_circumference.png", "total_average.png", "calculator.png", "radians.png", "triangle_area.png", "swap.png", "smallest.png", "sum_to_fifty.png", "factorial.png"]
# for file in os.listdir():
#     if file.endswith(".png"):
#         image_paths.append(file)

for path in image_paths:
    images.append(Image.open("output/PNG/" + path))

pdf1_filename = "Tejas_P_Herle_9_1_21_CPS_Assignment.pdf"
im = images.pop(0)
im.save(pdf1_filename, "PDF" ,resolution=100.0, save_all=True, append_images=images)

