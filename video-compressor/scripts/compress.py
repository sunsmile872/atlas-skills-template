#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import json

# Try to import dependencies, auto-installing if missing
try:
    import static_ffmpeg
    import cv2
    import numpy as np
except ImportError:
    print("Missing dependencies. Attempting to install static-ffmpeg and opencv-python...", file=sys.stderr)
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "static-ffmpeg", "opencv-python", "--user"])
        import static_ffmpeg
        import cv2
        import numpy as np
        print("Dependencies successfully installed.", file=sys.stderr)
    except Exception as e:
        print(f"Failed to install dependencies: {e}", file=sys.stderr)
        sys.exit(1)

def run_compress(args):
    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)
    
    if not os.path.exists(input_path):
        print(f"Error: Input file does not exist at {input_path}", file=sys.stderr)
        sys.exit(1)
        
    # Ensure static_ffmpeg is on PATH
    static_ffmpeg.add_paths()
    
    # Construct FFmpeg command
    cmd = ["ffmpeg", "-i", input_path]
    
    # Encoder parameters
    if args.encoder == "hevc_videotoolbox":
        cmd += ["-c:v", "hevc_videotoolbox", "-q:v", str(args.quality)]
    else:
        cmd += ["-c:v", "libx265", "-crf", str(args.crf), "-preset", args.preset]
        
    # Video filters (scaling)
    if args.scale:
        if ":" in args.scale or "=" in args.scale:
            scale_filter = args.scale
        else:
            scale_filter = f"scale=-2:{args.scale}"
        cmd += ["-vf", scale_filter]
        
    # Output framerate
    if args.fps:
        cmd += ["-r", str(args.fps)]
        
    # Audio parameters
    cmd += ["-c:a", "aac", "-b:a", "96k"]
    
    # Overwrite output file
    cmd += ["-y", output_path]
    
    print(f"Running compression command: {' '.join(cmd)}", file=sys.stderr)
    
    try:
        # Run process and stream progress to stderr
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            sys.stderr.write(line)
        process.wait()
        
        if process.returncode != 0:
            print(f"FFmpeg process failed with exit code {process.returncode}", file=sys.stderr)
            sys.exit(1)
            
        orig_size = os.path.getsize(input_path)
        comp_size = os.path.getsize(output_path)
        savings = (1 - (comp_size / orig_size)) * 100
        
        result = {
            "status": "success",
            "input_file": input_path,
            "output_file": output_path,
            "original_size_bytes": orig_size,
            "compressed_size_bytes": comp_size,
            "reduction_percentage": round(savings, 2)
        }
        
        if args.output_json:
            with open(args.output_json, "w") as f:
                json.dump(result, f, indent=2)
            print(f"Success! Quality metrics written to {args.output_json}")
        else:
            print(json.dumps(result, indent=2))
            
    except Exception as e:
        print(f"Compression failed with error: {e}", file=sys.stderr)
        sys.exit(1)

def run_validate(args):
    orig_path = os.path.abspath(args.original)
    comp_path = os.path.abspath(args.compressed)
    
    if not os.path.exists(orig_path) or not os.path.exists(comp_path):
        print("Error: Either original or compressed file path does not exist", file=sys.stderr)
        sys.exit(1)
        
    cap_orig = cv2.VideoCapture(orig_path)
    cap_comp = cv2.VideoCapture(comp_path)
    
    cap_orig.set(cv2.CAP_PROP_POS_FRAMES, args.frame)
    cap_comp.set(cv2.CAP_PROP_POS_FRAMES, args.frame)
    
    ret_orig, frame_orig = cap_orig.read()
    ret_comp, frame_comp = cap_comp.read()
    
    cap_orig.release()
    cap_comp.release()
    
    if not ret_orig or not ret_comp:
        print(f"Error: Failed to read frame {args.frame} from one or both videos", file=sys.stderr)
        sys.exit(1)
        
    # Resize compressed frame if sizes do not match (e.g. resolution changed)
    h_orig, w_orig, _ = frame_orig.shape
    h_comp, w_comp, _ = frame_comp.shape
    if (h_orig, w_orig) != (h_comp, w_comp):
        frame_comp_resized = cv2.resize(frame_comp, (w_orig, h_orig), interpolation=cv2.INTER_CUBIC)
    else:
        frame_comp_resized = frame_comp
        
    psnr = cv2.PSNR(frame_orig, frame_comp_resized)
    diff = cv2.absdiff(frame_orig, frame_comp_resized)
    max_diff = int(np.max(diff))
    mean_diff = float(np.mean(diff))
    
    result = {
        "status": "success",
        "frame_number": args.frame,
        "psnr_db": round(psnr, 2),
        "max_pixel_difference": max_diff,
        "mean_pixel_difference": round(mean_diff, 4),
        "resolution_original": f"{w_orig}x{h_orig}",
        "resolution_compressed": f"{w_comp}x{h_comp}"
    }
    
    if args.output_json:
        with open(args.output_json, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Success! Validation metrics written to {args.output_json}")
    else:
        print(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Video compression and quality validation utility.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Compress command
    compress_parser = subparsers.add_parser("compress", help="Compress a video file.")
    compress_parser.add_argument("--input", required=True, help="Input video file path.")
    compress_parser.add_argument("--output", required=True, help="Output compressed video file path.")
    compress_parser.add_argument("--crf", type=int, default=26, help="Constant Rate Factor (default: 26).")
    compress_parser.add_argument("--preset", default="ultrafast", help="FFmpeg speed/compression preset (default: ultrafast).")
    compress_parser.add_argument("--encoder", default="libx265", help="Video encoder to use (libx265 or hevc_videotoolbox).")
    compress_parser.add_argument("--scale", help="Scale height (e.g. 1080) or full scale filter (e.g. scale=-2:1080).")
    compress_parser.add_argument("--fps", help="Output framerate (e.g. 30, 15).")
    compress_parser.add_argument("--quality", type=int, default=50, help="Quality for videotoolbox (q:v, default: 50).")
    compress_parser.add_argument("--output-json", help="Path to write JSON results file instead of stdout.")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate visual quality difference.")
    validate_parser.add_argument("--original", required=True, help="Path to original video.")
    validate_parser.add_argument("--compressed", required=True, help="Path to compressed video.")
    validate_parser.add_argument("--frame", type=int, default=450, help="Frame index to check (default: 450).")
    validate_parser.add_argument("--output-json", help="Path to write JSON results file instead of stdout.")
    
    args = parser.parse_args()
    
    if args.command == "compress":
        run_compress(args)
    elif args.command == "validate":
        run_validate(args)

if __name__ == "__main__":
    main()
