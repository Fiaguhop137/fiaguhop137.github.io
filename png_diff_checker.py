#!/usr/bin/env python3
import sys
from PIL import Image,ImageOps
if len(sys.argv)!=4:
    print(f"Usage: {sys.argv[0]} image_1.png image_2.png result.png")
    sys.exit(1)
image_1=Image.open(sys.argv[1]).convert("RGBA")
image_2=Image.open(sys.argv[2]).convert("RGBA")
output_path=sys.argv[3]
area_1=image_1.width*image_1.height
area_2=image_2.width*image_2.height
if area_1<=area_2:
    smaller=image_1
    larger=image_2
else:
    smaller=image_2
    larger=image_1
inverted=ImageOps.invert(smaller.convert("RGB")).convert("RGBA")
alpha=inverted.getchannel("A")
alpha=alpha.point(lambda a:a//2)
inverted.putalpha(alpha)
x=(larger.width-smaller.width)//2
y=(larger.height-smaller.height)//2
result=larger.copy()
result.alpha_composite(inverted,(x,y))
result.save(output_path)