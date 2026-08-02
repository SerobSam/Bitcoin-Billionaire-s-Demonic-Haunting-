#!/usr/bin/env python3
"""Generate an 8k biome mask PNG at 01_world/biome_masks/world_biomemask_master_8k_PNG_v01.png
Creates a smooth Voronoi-like partition at 2048 then upsamples to 8192 for speed.
"""
import os
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont

OUT_PATH = os.path.join("01_world","biome_masks","world_biomemask_master_8k_PNG_v01.png")
SMALL = 2048
FINAL = 8192
SEED = 12345

BIOMES = [
    ("coastal", (52, 168, 172)),
    ("forest", (42, 153, 64)),
    ("cavern", (88, 24, 69)),
    ("quarry", (136, 98, 61)),
    ("urban", (120, 120, 120)),
    ("desert", (233, 188, 121)),
    ("swamp", (88, 102, 24)),
    ("glacier", (200, 230, 250)),
]

np.random.seed(SEED)
H = W = SMALL
k = len(BIOMES)
# choose biome centers with a bias towards edges for coast
centers = []
for i in range(k):
    if BIOMES[i][0] == "coastal":
        x = np.random.randint(0, W//6) if np.random.rand() < 0.5 else np.random.randint(W*5//6, W)
        y = np.random.randint(0, H)
    else:
        x = np.random.randint(W//6, W*5//6)
        y = np.random.randint(H//6, H*5//6)
    centers.append((x, y))
centers = np.array(centers)

# build grid
xs = np.arange(W, dtype=np.int32)
ys = np.arange(H, dtype=np.int32)
xx, yy = np.meshgrid(xs, ys)
# compute distances to each center
pts = centers[:, None, None, :]
# broadcast: centers (k,1,1,2), grid (H,W) => distances (k,H,W)
# compute squared distances to save memory
cx = centers[:, 0][:, None, None]
cy = centers[:, 1][:, None, None]
# distances squared
d2 = (xx[None, :, :] - cx)**2 + (yy[None, :, :] - cy)**2
labels = np.argmin(d2, axis=0).astype(np.uint8)

# convert labels to RGB
img = np.zeros((H, W, 3), dtype=np.uint8)
for i, (_, color) in enumerate(BIOMES):
    img[labels == i] = color

# smooth boundaries by blurring a bit
pil = Image.fromarray(img, mode="RGB")
pil = pil.filter(ImageFilter.GaussianBlur(radius=6))
# optional subtle noise overlay to break perfect color bands
noise = np.random.normal(scale=6, size=(H, W, 3)).astype(np.int16)
noisy = np.clip(np.array(pil, dtype=np.int16) + noise, 0, 255).astype(np.uint8)
pil = Image.fromarray(noisy, mode="RGB")

# upscale to final size with Lanczos
pil = pil.resize((FINAL, FINAL), resample=Image.LANCZOS)

# draw compact legend in corner
draw = ImageDraw.Draw(pil)
try:
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
except Exception:
    font = ImageFont.load_default()
margin = 30
box_w = 240
box_h = 28 * k + 20
legend_x = FINAL - box_w - margin
legend_y = margin
# background
draw.rectangle([legend_x, legend_y, legend_x + box_w, legend_y + box_h], fill=(10,10,10,200))
for i, (name, color) in enumerate(BIOMES):
    y = legend_y + 10 + i*28
    draw.rectangle([legend_x + 10, y, legend_x + 10 + 20, y+20], fill=color)
    draw.text((legend_x + 40, y - 2), name, fill=(240,240,240), font=font)

# ensure output directory exists
out_dir = os.path.dirname(OUT_PATH)
if out_dir and not os.path.exists(out_dir):
    os.makedirs(out_dir, exist_ok=True)

pil.save(OUT_PATH, format="PNG")
print(f"Saved biome mask to {OUT_PATH}")
