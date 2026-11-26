#!/usr/bin/env python3
"""
clinical-face-blur: Medical-grade patient & clinical staff face blurring and de-identification.
Supports video files, photo directories, and Google Drive links.
"""

import os
import sys

# Prevent Ultralytics from attempting background pip installs / checks
os.environ["YOLO_AUTOINSTALL"] = "False"
os.environ["YOLO_VERBOSE"] = "False"

import glob
import shutil
import argparse
import subprocess
from typing import List, Tuple, Optional
import cv2
import numpy as np
from PIL import Image, ImageOps

# Ensure references module is importable
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)

from references.gdrive_resolver import extract_gdrive_id, resolve_gdrive_item

MODEL_DIR = os.path.join(SKILL_ROOT, "models")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "yolov8n-pose.pt")

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".mkv", ".avi"}
PHOTO_EXTS = {".heic", ".jpg", ".jpeg", ".png", ".webp"}

def apply_feathered_blur(img: np.ndarray, cx: float, cy: float, rx: float, ry: float, blur_strength: int = 75):
    """Applies a broadcast-quality soft-edged feathered elliptical Gaussian blur."""
    H, W = img.shape[:2]
    x1 = max(0, int(cx - rx))
    x2 = min(W, int(cx + rx))
    y1 = max(0, int(cy - ry))
    y2 = min(H, int(cy + ry))
    if x2 <= x1 or y2 <= y1:
        return
    
    roi = img[y1:y2, x1:x2]
    k = max(51, int(min(rx, ry) * 0.45) // 2 * 2 + 1)
    blurred = cv2.GaussianBlur(roi, (k, k), k / 2.8)
    
    mask = np.zeros((y2 - y1, x2 - x1), dtype=np.float32)
    center = (int(cx - x1), int(cy - y1))
    axes = (int(rx * 0.85), int(ry * 0.85))
    cv2.ellipse(mask, center, axes, 0, 0, 360, 1.0, -1)
    
    fk = max(21, int(min(rx, ry) * 0.3) // 2 * 2 + 1)
    mask = cv2.GaussianBlur(mask, (fk, fk), fk / 3.0)
    mask = np.clip(mask, 0.0, 1.0)[:, :, np.newaxis]
    
    img[y1:y2, x1:x2] = (roi.astype(np.float32) * (1.0 - mask) + blurred.astype(np.float32) * mask).astype(np.uint8)

def smooth_trajectory(data: np.ndarray, window_len: int = 17) -> np.ndarray:
    N = len(data)
    smoothed = np.copy(data)
    hw = window_len // 2
    for i in range(N):
        i_start = max(0, i - hw)
        i_end = min(N, i + hw + 1)
        smoothed[i] = np.mean(data[i_start:i_end], axis=0)
    return smoothed

def process_video(video_path: str, output_path: Optional[str] = None, blur_strength: int = 75) -> str:
    from ultralytics import YOLO
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    if not output_path:
        dname = os.path.dirname(video_path)
        base = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(dname, f"{base}_blurred.mp4")
        
    temp_dir = os.path.join(os.path.dirname(output_path), ".temp_blur_proc")
    os.makedirs(temp_dir, exist_ok=True)
    temp_no_audio = os.path.join(temp_dir, "temp_video_no_audio.mp4")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[Video] Input: {os.path.basename(video_path)} ({width}x{height} @ {fps:.2f}fps, {total_frames} frames)")
    
    pose_model = YOLO(MODEL_PATH)
    
    # PASS 1: Detect head across all frames
    print("=== [Video] PASS 1: Detecting patient head & trajectory ===")
    raw_params = []
    frame_idx = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        H, W = frame.shape[:2]
        cand_boxes = []
        
        results = pose_model(frame, verbose=False, imgsz=640)
        for r in results:
            kpts = r.keypoints.xy.cpu().numpy()
            for kpt in kpts:
                head_pts = [p for p in kpt[:5] if p[0] > 0 and p[1] > 0]
                sh_pts = [p for p in kpt[5:7] if p[0] > 0 and p[1] > 0]
                
                if head_pts:
                    xs = [p[0] for p in head_pts]
                    ys = [p[1] for p in head_pts]
                    hcx = np.mean(xs)
                    hcy = np.mean(ys)
                    if 500 < hcx < 1450 and hcy < 500:
                        span_x = max(max(xs) - min(xs), 120)
                        span_y = max(max(ys) - min(ys), 120)
                        bx1 = hcx - span_x * 1.3
                        bx2 = hcx + span_x * 1.3
                        by1 = hcy - span_y * 1.4
                        by2 = hcy + span_y * 1.4
                        cand_boxes.append((bx1, by1, bx2, by2))
                elif sh_pts:
                    sh_cx = np.mean([p[0] for p in sh_pts])
                    sh_cy = min([p[1] for p in sh_pts])
                    if 550 < sh_cx < 1400 and sh_cy < 450:
                        bx1 = sh_cx - 180
                        bx2 = sh_cx + 180
                        by1 = 0
                        by2 = sh_cy + 30
                        cand_boxes.append((bx1, by1, bx2, by2))
                        
        if cand_boxes:
            min_x = max(0, min(b[0] for b in cand_boxes))
            min_y = max(0, min(b[1] for b in cand_boxes))
            max_x = min(W, max(b[2] for b in cand_boxes))
            max_y = min(H, max(b[3] for b in cand_boxes))
            cx = (min_x + max_x) / 2.0
            cy = (min_y + max_y) / 2.0
            rx = max((max_x - min_x) / 2.0 * 1.15, 110.0)
            ry = max((max_y - min_y) / 2.0 * 1.15, 110.0)
            raw_params.append([True, cx, cy, rx, ry])
        else:
            raw_params.append([False, 0.0, 0.0, 0.0, 0.0])
            
        frame_idx += 1
        if frame_idx % 250 == 0 or frame_idx == total_frames:
            print(f"  Scanned {frame_idx}/{total_frames} frames...")
    cap.release()
    
    # Interpolate missing frames
    raw_array = np.array(raw_params, dtype=np.float32)
    detected_mask = raw_array[:, 0] > 0.5
    indices = np.arange(total_frames)
    
    if np.any(detected_mask):
        det_indices = indices[detected_mask]
        coords = np.zeros((total_frames, 4), dtype=np.float32)
        for col in range(4):
            coords[:, col] = np.interp(indices, det_indices, raw_array[detected_mask, col+1])
    else:
        raise RuntimeError("No face detected in video!")
        
    smoothed_coords = smooth_trajectory(coords, window_len=17)
    print("=== [Video] PASS 1 Complete: Trajectory smoothed ===")
    
    # PASS 2: Render blurred frames to FFmpeg
    print("=== [Video] PASS 2: Rendering and encoding ===")
    ffmpeg_cmd = [
        ffmpeg_exe, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{width}x{height}", "-pix_fmt", "bgr24",
        "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", temp_no_audio
    ]
    pipe = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cx, cy, rx, ry = smoothed_coords[frame_idx]
        apply_feathered_blur(frame, cx, cy, rx, ry, blur_strength=blur_strength)
        pipe.stdin.write(frame.tobytes())
        frame_idx += 1
        if frame_idx % 250 == 0 or frame_idx == total_frames:
            print(f"  Rendered {frame_idx}/{total_frames} frames...")
    cap.release()
    pipe.stdin.close()
    pipe.wait()
    
    # Step 3: Mux Audio
    print("=== [Video] Step 3: Muxing synchronized audio ===")
    mux_cmd = [
        ffmpeg_exe, "-y",
        "-i", temp_no_audio,
        "-i", video_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0",
        "-map", "1:a:0?",
        output_path
    ]
    subprocess.run(mux_cmd, check=True, stdout=subprocess.DEVNULL)
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"Success! Output saved: {output_path}")
    return output_path

def process_photo(photo_path: str, output_dir: Optional[str] = None, blur_strength: int = 75, export_formats: List[str] = ["jpg"]):
    if not os.path.exists(photo_path):
        raise FileNotFoundError(f"Photo file not found: {photo_path}")
        
    from ultralytics import YOLO
    model = YOLO(MODEL_PATH)
    
    base_name = os.path.splitext(os.path.basename(photo_path))[0]
    ext = os.path.splitext(photo_path)[1].lower()
    
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(photo_path), "Blurred")
    os.makedirs(output_dir, exist_ok=True)
    
    # Read image via sips or PIL with EXIF transpose
    temp_jpg = os.path.join(output_dir, f".temp_{base_name}.jpg")
    if ext in [".heic", ".heif"]:
        subprocess.run(["sips", "-s", "format", "jpeg", photo_path, "--out", temp_jpg], check=True, stdout=subprocess.DEVNULL)
        pil_img = ImageOps.exif_transpose(Image.open(temp_jpg))
    else:
        pil_img = ImageOps.exif_transpose(Image.open(photo_path))
        
    arr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    H, W = arr.shape[:2]
    
    res = model(arr, verbose=False, imgsz=960)
    face_regions = []
    
    for r in res:
        kpts = r.keypoints.xy.cpu().numpy()
        confs = r.keypoints.conf.cpu().numpy() if r.keypoints.conf is not None else None
        for i, kpt in enumerate(kpts):
            head_pts = [p for p in kpt[:5] if p[0] > 0 and p[1] > 0]
            if len(head_pts) >= 2:
                xs = [p[0] for p in head_pts]
                ys = [p[1] for p in head_pts]
                if confs is not None:
                    head_conf = np.mean([confs[i][j] for j in range(5) if kpt[j][0] > 0])
                    if head_conf < 0.28:
                        continue
                span_x = max(max(xs) - min(xs), 120)
                span_y = max(max(ys) - min(ys), 120)
                cx = np.mean(xs)
                cy = np.mean(ys)
                rx = max(span_x * 1.35, 130)
                ry = max(span_y * 1.5, 140)
                
                # Check nose vs eyes for chin extension
                if kpt[0][1] > 0 and (kpt[1][1] > 0 or kpt[2][1] > 0):
                    eye_y = np.mean([kpt[j][1] for j in [1, 2] if kpt[j][1] > 0])
                    nose_y = kpt[0][1]
                    if nose_y > eye_y:
                        cy = eye_y + (nose_y - eye_y) * 1.4
                        ry = max(ry, (nose_y - eye_y) * 3.3)
                        rx = max(rx, ry * 0.85)
                face_regions.append((cx, cy, rx, ry))
                
    # Apply blur
    for cx, cy, rx, ry in face_regions:
        apply_feathered_blur(arr, cx, cy, rx, ry, blur_strength=blur_strength)
        
    # Save results
    out_jpg = os.path.join(output_dir, f"{base_name}_blurred.jpg")
    cv2.imwrite(out_jpg, arr, [cv2.IMWRITE_JPEG_QUALITY, 96])
    
    if "heic" in export_formats:
        out_heic = os.path.join(output_dir, f"{base_name}_blurred.HEIC")
        subprocess.run(["sips", "-s", "format", "heic", out_jpg, "--out", out_heic], check=True, stdout=subprocess.DEVNULL)
        
    if "jpg" not in export_formats and os.path.exists(out_jpg):
        os.remove(out_jpg)
        
    if os.path.exists(temp_jpg):
        os.remove(temp_jpg)
        
    print(f"[Photo] {base_name}: {len(face_regions)} faces blurred -> {output_dir}")

def process_photo_dir(folder_path: str, output_dir: Optional[str] = None, blur_strength: int = 75, export_formats: List[str] = ["jpg"]):
    if not output_dir:
        output_dir = os.path.join(folder_path, "Blurred")
    os.makedirs(output_dir, exist_ok=True)
    
    images = []
    for ext in PHOTO_EXTS:
        images.extend(glob.glob(os.path.join(folder_path, f"*{ext}")))
        images.extend(glob.glob(os.path.join(folder_path, f"*{ext.upper()}")))
        
    images = sorted(list(set(images)))
    images = [f for f in images if not f.endswith("_blurred.jpg") and not f.endswith("_blurred.jpeg") and not f.endswith("_blurred.HEIC") and not f.endswith("_blurred.heic")]
    print(f"[Photos] Found {len(images)} images in {folder_path}")
    
    for img_p in images:
        process_photo(img_p, output_dir=output_dir, blur_strength=blur_strength, export_formats=export_formats)
    print(f"All {len(images)} photos processed. Results saved to: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Clinical Media Patient Face Blurring & De-identification")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    
    # Auto subcommand
    p_auto = subparsers.add_parser("auto", help="Auto-detect media from local path or Google Drive URL")
    p_auto.add_argument("--input", required=True, help="File path, folder path, or Google Drive URL")
    p_auto.add_argument("--output-dir", default=None, help="Output directory")
    p_auto.add_argument("--blur-strength", type=int, default=75, help="Blur kernel strength")
    p_auto.add_argument("--format", choices=["jpg", "heic", "both"], default="jpg", help="Export format for photos (default: jpg)")
    
    # Video subcommand
    p_vid = subparsers.add_parser("video", help="Process a clinical video file")
    p_vid.add_argument("--input", required=True, help="Path to video file")
    p_vid.add_argument("--output", default=None, help="Path to output video file")
    p_vid.add_argument("--blur-strength", type=int, default=75, help="Blur kernel strength")
    
    # Photo subcommand
    p_img = subparsers.add_parser("photo", help="Process a clinical photo or folder of photos")
    p_img.add_argument("--input", required=True, help="Path to photo or folder")
    p_img.add_argument("--output-dir", default=None, help="Output directory")
    p_img.add_argument("--blur-strength", type=int, default=75, help="Blur kernel strength")
    p_img.add_argument("--format", choices=["jpg", "heic", "both"], default="jpg", help="Export format (default: jpg)")
    
    args = parser.parse_args()
    
    if args.subcommand == "auto":
        inp = args.input.strip()
        gdrive_id = extract_gdrive_id(inp)
        if gdrive_id:
            print(f"[Auto] Detected Google Drive ID: {gdrive_id}")
            resolved = resolve_gdrive_item(gdrive_id)
            if not resolved:
                print(f"Error: Could not resolve Google Drive ID {gdrive_id} in local DriveFS. Ensure Google Drive for Mac is running.")
                sys.exit(1)
            print(f"[Auto] Resolved: {resolved['title']} ({resolved['type']}) at {resolved['local_path']}")
            inp = resolved['local_path']
            
        fmts = ["jpg"] if args.format == "jpg" else (["heic"] if args.format == "heic" else ["jpg", "heic"])
        if os.path.isdir(inp):
            process_photo_dir(inp, output_dir=args.output_dir, blur_strength=args.blur_strength, export_formats=fmts)
        elif os.path.isfile(inp):
            ext = os.path.splitext(inp)[1].lower()
            if ext in VIDEO_EXTS:
                process_video(inp, output_path=args.output_dir, blur_strength=args.blur_strength)
            elif ext in PHOTO_EXTS:
                process_photo(inp, output_dir=args.output_dir, blur_strength=args.blur_strength, export_formats=fmts)
            else:
                print(f"Error: Unsupported media extension {ext}")
                sys.exit(1)
        else:
            print(f"Error: Target path does not exist: {inp}")
            sys.exit(1)
            
    elif args.subcommand == "video":
        process_video(args.input, output_path=args.output, blur_strength=args.blur_strength)
        
    elif args.subcommand == "photo":
        fmts = ["jpg"] if args.format == "jpg" else (["heic"] if args.format == "heic" else ["jpg", "heic"])
        if os.path.isdir(args.input):
            process_photo_dir(args.input, output_dir=args.output_dir, blur_strength=args.blur_strength, export_formats=fmts)
        else:
            process_photo(args.input, output_dir=args.output_dir, blur_strength=args.blur_strength, export_formats=fmts)

if __name__ == "__main__":
    main()
