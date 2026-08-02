#!/usr/bin/env python3
"""Generate a full biome-mask asset set for the game world.

This script writes:
- a color atlas PNG for world biome regions
- a grayscale index PNG with integer biome IDs
- per-biome alpha masks for downstream tooling
- a JSON manifest describing each biome layer
"""
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "01_world" / "biome_masks"
OUT_IMAGE = OUT_DIR / "world_biomemask_master_8k_PNG_v01.png"
OUT_INDEX = OUT_DIR / "world_biomemask_master_8k_INDEX_v01.png"
OUT_MANIFEST = OUT_DIR / "world_biomemask_master_8k_manifest_v01.json"
OUT_MASKS = OUT_DIR / "biome_masks_v01"

SMALL_RES = 2048
FINAL_RES = 8192
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


def build_labels(size: int, seed: int = SEED) -> np.ndarray:
    rng = np.random.default_rng(seed)
    height = width = size
    centers = []
    for name, _ in BIOMES:
        if name == "coastal":
            x = rng.integers(0, width // 6) if rng.random() < 0.5 else rng.integers(width * 5 // 6, width)
            y = rng.integers(0, height)
        else:
            x = rng.integers(width // 6, width * 5 // 6)
            y = rng.integers(height // 6, height * 5 // 6)
        centers.append((x, y))

    centers = np.array(centers, dtype=np.float32)
    ys, xs = np.mgrid[0:height, 0:width]
    grid = np.stack([xs, ys], axis=-1).astype(np.float32)

    distances = np.linalg.norm(grid[None, :, :, :] - centers[:, None, None, :], axis=-1)
    labels = np.argmin(distances, axis=0).astype(np.uint8)
    return labels


def create_color_atlas(labels: np.ndarray) -> Image.Image:
    height, width = labels.shape
    img = np.zeros((height, width, 3), dtype=np.uint8)
    for index, (_, color) in enumerate(BIOMES):
        img[labels == index] = color

    base = Image.fromarray(img, mode="RGB")
    base = base.filter(ImageFilter.GaussianBlur(radius=6))
    noise = np.random.normal(scale=6, size=(height, width, 3)).astype(np.int16)
    noisy = np.clip(np.array(base, dtype=np.int16) + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy, mode="RGB")


def add_legend(image: Image.Image, labels: np.ndarray) -> Image.Image:
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    except Exception:
        font = ImageFont.load_default()

    margin = 30
    box_w = 260
    box_h = 28 * len(BIOMES) + 20
    legend_x = image.width - box_w - margin
    legend_y = margin
    draw.rectangle([legend_x, legend_y, legend_x + box_w, legend_y + box_h], fill=(10, 10, 10, 200))

    for idx, (name, color) in enumerate(BIOMES):
        y = legend_y + 10 + idx * 28
        draw.rectangle([legend_x + 10, y, legend_x + 34, y + 20], fill=color)
        draw.text((legend_x + 44, y - 2), name, fill=(240, 240, 240), font=font)

    return image


def write_outputs(labels: np.ndarray) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_MASKS.mkdir(parents=True, exist_ok=True)

    atlas = create_color_atlas(labels)
    atlas = atlas.resize((FINAL_RES, FINAL_RES), resample=Image.LANCZOS)
    atlas = add_legend(atlas, labels)
    atlas.save(OUT_IMAGE, format="PNG")

    index_image = Image.fromarray(labels.astype(np.uint8), mode="L")
    index_image = index_image.resize((FINAL_RES, FINAL_RES), resample=Image.NEAREST)
    index_image.save(OUT_INDEX, format="PNG")

    manifest = {"biomes": []}
    for idx, (name, color) in enumerate(BIOMES):
        mask = (labels == idx).astype(np.uint8) * 255
        mask_image = Image.fromarray(mask, mode="L")
        mask_image = mask_image.filter(ImageFilter.GaussianBlur(radius=4))
        mask_image = mask_image.resize((FINAL_RES, FINAL_RES), resample=Image.LANCZOS)
        mask_path = OUT_MASKS / f"biome_{idx:02d}_{name}.png"
        mask_image.save(mask_path, format="PNG")
        manifest["biomes"].append({
            "id": idx,
            "name": name,
            "color": list(color),
            "mask": mask_path.relative_to(OUT_DIR).as_posix(),
        })

    with OUT_MANIFEST.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)


if __name__ == "__main__":
    labels = build_labels(SMALL_RES)
    write_outputs(labels)
    print(f"Saved atlas to {OUT_IMAGE}")
    print(f"Saved index image to {OUT_INDEX}")
    print(f"Saved masks to {OUT_MASKS}")
    print(f"Saved manifest to {OUT_MANIFEST}")
