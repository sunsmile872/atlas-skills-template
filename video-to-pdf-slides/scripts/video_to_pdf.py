# /// script
# dependencies = [
#   "opencv-python",
#   "pillow",
#   "static-ffmpeg"
# ]
# ///

import os
import sys
import json
import argparse
from PIL import Image

# Import and initialize static-ffmpeg to ensure ffmpeg binaries are in the path
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass

# =====================================================================
# 1. Slide Extraction
# =====================================================================
def extract_and_filter_slides(video_path, output_dir, metadata_path, slide_threshold=6.0, stability_threshold=1.5, stability_timeout=5, sample_fps=1.0, min_duration=10.0):
    import cv2
    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file: {video_path}", file=sys.stderr)
        sys.exit(1)
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    print(f"FPS: {fps:.2f}, Total Frames: {total_frames}, Duration: {duration:.2f} seconds ({duration/60:.2f} mins)")
    
    sample_interval = max(1, int(fps / sample_fps))
    
    last_saved_gray = None
    prev_gray = None
    
    frame_idx = 0
    raw_slides = []
    
    pending_slide_color = None
    pending_slide_gray = None
    change_seconds = 0
    
    last_save_time = 0.0
    
    print("Analyzing video and detecting slide changes...")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_idx % sample_interval == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_resized = cv2.resize(gray, (320, 180))
            timestamp_sec = frame_idx / fps if fps > 0 else 0
            
            if last_saved_gray is None:
                raw_slides.append({
                    "start_time": timestamp_sec,
                    "frame": frame.copy()
                })
                last_saved_gray = gray_resized.copy()
                prev_gray = gray_resized.copy()
                last_save_time = timestamp_sec
            else:
                diff_from_last = cv2.absdiff(gray_resized, last_saved_gray).mean()
                diff_from_prev = cv2.absdiff(gray_resized, prev_gray).mean()
                
                if diff_from_last > slide_threshold:
                    if diff_from_prev < stability_threshold:
                        if timestamp_sec - last_save_time >= 2.0:
                            if len(raw_slides) > 0:
                                raw_slides[-1]["end_time"] = timestamp_sec
                            raw_slides.append({
                                "start_time": timestamp_sec,
                                "frame": frame.copy()
                            })
                            last_saved_gray = gray_resized.copy()
                            last_save_time = timestamp_sec
                        pending_slide_color = None
                        pending_slide_gray = None
                        change_seconds = 0
                    else:
                        pending_slide_color = frame.copy()
                        pending_slide_gray = gray_resized.copy()
                        change_seconds += 1
                        
                        if change_seconds >= stability_timeout:
                            if timestamp_sec - last_save_time >= 2.0:
                                if len(raw_slides) > 0:
                                    raw_slides[-1]["end_time"] = timestamp_sec
                                raw_slides.append({
                                    "start_time": timestamp_sec,
                                    "frame": pending_slide_color.copy()
                                })
                                last_saved_gray = pending_slide_gray.copy()
                                last_save_time = timestamp_sec
                            pending_slide_color = None
                            pending_slide_gray = None
                            change_seconds = 0
                else:
                    pending_slide_color = None
                    pending_slide_gray = None
                    change_seconds = 0
                    
                prev_gray = gray_resized.copy()
        
        frame_idx += 1
        
    cap.release()
    
    if len(raw_slides) > 0:
        raw_slides[-1]["end_time"] = duration
        
    print(f"Detected {len(raw_slides)} raw slide transitions. Merging slides shorter than {min_duration}s...")
    
    filtered_slides = []
    for slide in raw_slides:
        slide_duration = slide["end_time"] - slide["start_time"]
        if not filtered_slides:
            filtered_slides.append(slide)
        else:
            prev_slide = filtered_slides[-1]
            prev_duration = prev_slide["end_time"] - prev_slide["start_time"]
            
            if slide_duration < min_duration:
                prev_slide["end_time"] = slide["end_time"]
            else:
                if prev_duration < min_duration:
                    slide["start_time"] = prev_slide["start_time"]
                    filtered_slides[-1] = slide
                else:
                    filtered_slides.append(slide)
                    
    metadata_list = []
    for i, slide in enumerate(filtered_slides):
        slide_path = os.path.join(output_dir, f"slide_{i:03d}.jpg")
        cv2.imwrite(slide_path, slide["frame"])
        metadata_list.append({
            "index": i,
            "start_time": slide["start_time"],
            "end_time": slide["end_time"],
            "duration": slide["end_time"] - slide["start_time"],
            "image_path": slide_path
        })
        
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata_list, f, indent=4, ensure_ascii=False)
        
    print(f"Extraction successful! Saved {len(filtered_slides)} slides to: {output_dir}")
    print(f"Metadata saved to: {metadata_path}")


# =====================================================================
# 2. PDF Compilation
# =====================================================================
def compile_pdf_from_metadata(metadata_path, output_pdf):
    if not os.path.exists(metadata_path):
        print(f"Error: Metadata file not found at: {metadata_path}", file=sys.stderr)
        sys.exit(1)
        
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        
    metadata.sort(key=lambda x: x["index"])
    
    images = []
    metadata_dir = os.path.dirname(os.path.abspath(metadata_path))
    
    for entry in metadata:
        img_path = entry["image_path"]
        if not os.path.isabs(img_path):
            img_path = os.path.join(metadata_dir, img_path)
            
        if os.path.exists(img_path):
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)
        else:
            print(f"Warning: Slide image not found at: {img_path}", file=sys.stderr)
            
    if not images:
        print("Error: No images found to compile into PDF.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Compiling {len(images)} slides into PDF...")
    images[0].save(output_pdf, save_all=True, append_images=images[1:])
    print(f"Success! PDF compiled and saved to: {output_pdf}")


# =====================================================================
# 3. Slide Metadata Filtering
# =====================================================================
def filter_metadata(metadata_path, similarity_threshold=5.0, black_threshold=18.0, black_pixel_pct_threshold=85.0):
    import cv2
    import numpy as np
    
    if not os.path.exists(metadata_path):
        print(f"Warning: Metadata file not found for filtering: {metadata_path}", file=sys.stderr)
        return
        
    print(f"Applying second-pass content filtering on: {metadata_path}")
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        
    metadata.sort(key=lambda x: x["index"])
    
    filtered_by_content = []
    metadata_dir = os.path.dirname(os.path.abspath(metadata_path))
    
    # First pass: Filter out black/Zoom screens
    for entry in metadata:
        img_path = entry["image_path"]
        if not os.path.isabs(img_path):
            img_path = os.path.join(metadata_dir, img_path)
            
        if os.path.exists(img_path):
            img = cv2.imread(img_path)
            if img is None:
                filtered_by_content.append(entry)
                continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray_resized = cv2.resize(gray, (320, 180))
            
            black_pct = np.mean(gray_resized < 15) * 100
            mean_val = np.mean(gray_resized)
            
            if mean_val < black_threshold or black_pct > black_pixel_pct_threshold:
                print(f"Filtering out slide {entry['index']} (Unnecessary black/Zoom screen: Mean={mean_val:.1f}, BlackPct={black_pct:.1f}%)")
                try:
                    os.remove(img_path)
                except Exception:
                    pass
                continue
                
            entry["_gray"] = gray_resized
            filtered_by_content.append(entry)
        else:
            filtered_by_content.append(entry)
            
    # Second pass: Merge similar consecutive slides
    final_slides = []
    for entry in filtered_by_content:
        if not final_slides:
            final_slides.append(entry)
        else:
            prev = final_slides[-1]
            if "_gray" in entry and "_gray" in prev:
                diff = cv2.absdiff(entry["_gray"], prev["_gray"]).mean()
                if diff < similarity_threshold:
                    print(f"Merging slide {entry['index']} into slide {prev['index']} (Visual diff={diff:.2f} < {similarity_threshold})")
                    prev["end_time"] = entry["end_time"]
                    prev["duration"] = prev["end_time"] - prev["start_time"]
                    img_path = entry["image_path"]
                    if not os.path.isabs(img_path):
                        img_path = os.path.join(metadata_dir, img_path)
                    try:
                        os.remove(img_path)
                    except Exception:
                        pass
                    continue
            final_slides.append(entry)
            
    # Clean up temp keys
    for entry in final_slides:
        if "_gray" in entry:
            del entry["_gray"]
            
    # Re-index remaining slides
    for idx, entry in enumerate(final_slides):
        entry["index"] = idx
        
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(final_slides, f, indent=4, ensure_ascii=False)
    
    print(f"Filtering complete: Kept {len(final_slides)} of {len(metadata)} slides.")


# =====================================================================
# 4. Main Wrapper
# =====================================================================
def run_pipeline(video_path, output_pdf, output_dir=None, metadata_path=None, threshold=6.0, min_duration=10.0):
    pdf_abs_path = os.path.abspath(output_pdf)
    pdf_dir = os.path.dirname(pdf_abs_path)
    pdf_base = os.path.splitext(os.path.basename(pdf_abs_path))[0]
    
    if not output_dir:
        output_dir = os.path.join(pdf_dir, f"{pdf_base}_slides")
    if not metadata_path:
        metadata_path = os.path.join(pdf_dir, f"{pdf_base}_metadata.json")
        
    extract_and_filter_slides(
        video_path=video_path,
        output_dir=output_dir,
        metadata_path=metadata_path,
        slide_threshold=threshold,
        min_duration=min_duration
    )
    
    # Filter the metadata before compiling
    filter_metadata(metadata_path)
    
    compile_pdf_from_metadata(
        metadata_path=metadata_path,
        output_pdf=pdf_abs_path
    )


# =====================================================================
# Main Parser
# =====================================================================
def main():
    parser = argparse.ArgumentParser(description="Slide Extraction and PDF Compilation Utility")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # extract-slides command
    p_extract = subparsers.add_parser("extract-slides", help="Extract visual slides from a video file")
    p_extract.add_argument("--video", required=True, help="Path to the source video file")
    p_extract.add_argument("--output-dir", required=True, help="Directory to save extracted slide images (JPEGs)")
    p_extract.add_argument("--metadata", required=True, help="Path to save the JSON slides metadata")
    p_extract.add_argument("--threshold", type=float, default=6.0, help="Difference threshold for slide transitions (lower is more sensitive)")
    p_extract.add_argument("--min-duration", type=float, default=10.0, help="Minimum duration (seconds) a slide must be visible to be kept")
    
    # compile-pdf command
    p_compile = subparsers.add_parser("compile-pdf", help="Compile slide images into a single PDF")
    p_compile.add_argument("--metadata", required=True, help="Path to the JSON slides metadata")
    p_compile.add_argument("--output-pdf", required=True, help="Path to save the final compiled PDF file")
    
    # run command (full pipeline)
    p_run = subparsers.add_parser("run", help="Run full pipeline: extract slides and compile PDF in one command")
    p_run.add_argument("--video", required=True, help="Path to the source video file")
    p_run.add_argument("--output-pdf", required=True, help="Path to save the final compiled PDF file")
    p_run.add_argument("--output-dir", help="Directory to save slide images (default: <pdf_dir>/<pdf_name>_slides)")
    p_run.add_argument("--metadata", help="Path to slides metadata file (default: <pdf_dir>/<pdf_name>_metadata.json)")
    p_run.add_argument("--threshold", type=float, default=6.0, help="Difference threshold for slide transitions")
    p_run.add_argument("--min-duration", type=float, default=10.0, help="Minimum duration (seconds) a slide must be visible")
    
    args = parser.parse_args()
    
    if args.command == "extract-slides":
        extract_and_filter_slides(
            video_path=args.video,
            output_dir=args.output_dir,
            metadata_path=args.metadata,
            slide_threshold=args.threshold,
            min_duration=args.min_duration
        )
    elif args.command == "compile-pdf":
        compile_pdf_from_metadata(
            metadata_path=args.metadata,
            output_pdf=args.output_pdf
        )
    elif args.command == "run":
        run_pipeline(
            video_path=args.video,
            output_pdf=args.output_pdf,
            output_dir=args.output_dir,
            metadata_path=args.metadata,
            threshold=args.threshold,
            min_duration=args.min_duration
        )

if __name__ == "__main__":
    main()
