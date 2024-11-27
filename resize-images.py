#! /usr/bin/env python3

import os
import re
import argparse
try:
    from PIL import Image
except ModuleNotFoundError as e:
    raise Exception("missing pillow - run: pip install Pillow") from e


golden_rate = 1280/720
default_size_x = 640
default_size_y = 360

parse = argparse.ArgumentParser(description="Script to resize pictures from a specific directory to the same size")
parse.add_argument("--directory", required=True, help="directory with images jpg")
args = parse.parse_args()

for filename in sorted(os.listdir(args.directory)):
    if not re.search("jpg", filename):
        continue
    with Image.open(args.directory + "/" + filename) as image:
        width, height = image.size
        rate = float(width)/float(height)
        is_golden = rate == golden_rate

        is_correted = False
        rate_from_default = width / default_size_x
        if rate_from_default == 1:
            pass 
        elif rate_from_default > 1:
            image = image.resize((default_size_x, int(height/rate_from_default)))
            is_correted = True
        else:
            image = image.resize((default_size_x, int(height/rate_from_default)), Image.Resampling.LANCZOS)
            is_correted = True

        if not is_golden:
            image = image.crop((0, 0, default_size_x, default_size_y))

        image.save(filename)
        print(f"{filename}: {width}x{height}, golden: {is_golden}, corrected: {is_correted}")


print(f"Golden rate: {golden_rate}")
