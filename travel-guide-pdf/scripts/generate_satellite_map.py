#!/usr/bin/env python3
"""
Generate a high-resolution satellite route map PNG using Esri World_Imagery tiles.

Usage:
  python3 generate_satellite_map.py --spec map_spec.json --out map.png

JSON spec format:
{
  "width": 1400,
  "height": 760,
  "zoom": 13,
  "padding": 0.18,
  "pins": [
    {"lat": 31.2304, "lon": 121.4737, "label": "1. The Bund", "color": "#0F766E"}
  ],
  "routes": [
    {"points": [[31.2304, 121.4737], [31.2270, 121.4920]], "color": "#2DD4BF", "width": 4, "dashed": false}
  ]
}
"""

import argparse
import io
import json
import math
import urllib.request
from PIL import Image, ImageDraw, ImageFont

TILE_SIZE = 256
ESRI_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"


def latlon_to_pixel(lat: float, lon: float, zoom: int) -> tuple[float, float]:
    n = 2 ** zoom
    x = (lon + 180.0) / 360.0 * n * TILE_SIZE
    lat_rad = math.radians(lat)
    y = (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n * TILE_SIZE
    return x, y


def fetch_tile(z: int, x: int, y: int) -> Image.Image:
    url = ESRI_URL.format(z=z, x=x, y=y)
    req = urllib.request.Request(url, headers={"User-Agent": "TravelGuidePDF/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return Image.open(io.BytesIO(resp.read())).convert("RGBA")


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_map(spec: dict, out_path: str) -> None:
    pins = spec["pins"]
    routes = spec.get("routes", [])
    zoom = spec.get("zoom", 13)
    out_w = spec.get("width", 1400)
    out_h = spec.get("height", 760)
    pad = spec.get("padding", 0.18)

    all_pts = [(p["lat"], p["lon"]) for p in pins]
    for r in routes:
        all_pts.extend((pt[0], pt[1]) for pt in r["points"])

    px_pts = [latlon_to_pixel(lat, lon, zoom) for lat, lon in all_pts]
    min_x, max_x = min(p[0] for p in px_pts), max(p[0] for p in px_pts)
    min_y, max_y = min(p[1] for p in px_pts), max(p[1] for p in px_pts)

    cx, cy = (min_x + max_x) / 2.0, (min_y + max_y) / 2.0
    span_x = max((max_x - min_x) * (1.0 + 2 * pad), out_w * 0.6)
    span_y = max((max_y - min_y) * (1.0 + 2 * pad), out_h * 0.6)

    scale = max(span_x / out_w, span_y / out_h)
    view_w, view_h = out_w * scale, out_h * scale
    left, top = cx - view_w / 2.0, cy - view_h / 2.0
    right, bottom = left + view_w, top + view_h

    tx0, tx1 = int(math.floor(left / TILE_SIZE)), int(math.floor(right / TILE_SIZE))
    ty0, ty1 = int(math.floor(top / TILE_SIZE)), int(math.floor(bottom / TILE_SIZE))

    canvas = Image.new("RGBA", ((tx1 - tx0 + 1) * TILE_SIZE, (ty1 - ty0 + 1) * TILE_SIZE))
    n_tiles = 2 ** zoom
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            if 0 <= ty < n_tiles:
                tile = fetch_tile(zoom, tx % n_tiles, ty)
                canvas.paste(tile, ((tx - tx0) * TILE_SIZE, (ty - ty0) * TILE_SIZE))

    crop_box = (
        left - tx0 * TILE_SIZE,
        top - ty0 * TILE_SIZE,
        right - tx0 * TILE_SIZE,
        bottom - ty0 * TILE_SIZE,
    )
    img = canvas.crop(crop_box).resize((out_w, out_h), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img, "RGBA")

    def to_out(lat: float, lon: float) -> tuple[float, float]:
        px, py = latlon_to_pixel(lat, lon, zoom)
        return (px - left) / scale, (py - top) / scale

    for route in routes:
        pts = [to_out(pt[0], pt[1]) for pt in route["points"]]
        color = route.get("color", "#2DD4BF")
        width = route.get("width", 4)
        if len(pts) >= 2:
            draw.line(pts, fill=color, width=width, joint="curve")

    font = load_font(18)
    for idx, pin in enumerate(pins, start=1):
        ox, oy = to_out(pin["lat"], pin["lon"])
        color = pin.get("color", "#0F766E")
        r = 12
        draw.ellipse((ox - r - 2, oy - r - 2, ox + r + 2, oy + r + 2), fill="#FFFFFF")
        draw.ellipse((ox - r, oy - r, ox + r, oy + r), fill=color)
        num_str = str(pin.get("num", idx))
        draw.text((ox - 4 * len(num_str), oy - 9), num_str, fill="#FFFFFF", font=load_font(15))

        label = pin.get("label", "")
        if label:
            bbox = draw.textbbox((0, 0), label, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            lx, ly = ox + r + 8, oy - th / 2 - 4
            draw.rounded_rectangle(
                (lx - 6, ly - 3, lx + tw + 8, ly + th + 5),
                radius=6,
                fill=(11, 23, 42, 220),
                outline=(45, 212, 191, 200),
                width=1,
            )
            draw.text((lx + 1, ly), label, fill="#F8FAFC", font=font)

    img.convert("RGB").save(out_path, "PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Esri World_Imagery satellite map PNG.")
    parser.add_argument("--spec", required=True, help="Path to JSON map specification")
    parser.add_argument("--out", required=True, help="Output PNG path")
    args = parser.parse_args()
    with open(args.spec, "r", encoding="utf-8") as f:
        spec = json.load(f)
    render_map(spec, args.out)
    print(f"Saved satellite map -> {args.out}")


if __name__ == "__main__":
    main()
