import os
import sys
import argparse
import json
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

def detect_face_bbox(pil_img):
    """Robustly detects primary face bounding box using multiple Haar cascades and aspect validation."""
    if not HAS_CV2:
        w, h = pil_img.size
        return int(w * 0.25), int(h * 0.15), int(w * 0.5), int(h * 0.35)
        
    cv_im = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_im, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    scale = 0.25
    small_gray = cv2.resize(gray, (int(w * scale), int(h * scale)))
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    alt2_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
    profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
    
    candidates = []
    # 1. Frontal default
    for (x, y, fw, fh) in face_cascade.detectMultiScale(small_gray, 1.1, 4, minSize=(80, 80)):
        candidates.append((int(x / scale), int(y / scale), int(fw / scale), int(fh / scale)))
    # 2. Alt2
    for (x, y, fw, fh) in alt2_cascade.detectMultiScale(small_gray, 1.1, 4, minSize=(80, 80)):
        candidates.append((int(x / scale), int(y / scale), int(fw / scale), int(fh / scale)))
    # 3. Profile
    for (x, y, fw, fh) in profile_cascade.detectMultiScale(small_gray, 1.1, 4, minSize=(80, 80)):
        candidates.append((int(x / scale), int(y / scale), int(fw / scale), int(fh / scale)))
    # 4. Flipped profile
    flipped = cv2.flip(small_gray, 1)
    for (fx, fy, fw, fh) in profile_cascade.detectMultiScale(flipped, 1.1, 4, minSize=(80, 80)):
        orig_fx = int(w * scale) - (fx + fw)
        candidates.append((int(orig_fx / scale), int(fy / scale), int(fw / scale), int(fh / scale)))
        
    # In clinical portrait photography, the true subject head should occupy >= 35% of image width
    valid = [c for c in candidates if c[2] >= w * 0.35]
    if not valid:
        valid = candidates
        
    if valid:
        return max(valid, key=lambda c: c[2] * c[3])
    return int(w * 0.25), int(h * 0.15), int(w * 0.5), int(h * 0.35)

def align_and_crop_pair(b_img, a_img, aspect_ratio=(3, 4)):
    """Calibrates anatomical scale (strict 1:1 head ratio) and vertical eye level across Before & After."""
    b_fx, b_fy, b_fw, b_fh = detect_face_bbox(b_img)
    a_fx, a_fy, a_fw, a_fh = detect_face_bbox(a_img)
    
    ar_w, ar_h = aspect_ratio
    aspect = ar_w / ar_h  # 0.75
    
    # Scale factor from B to A
    scale_a_to_b = a_fh / b_fh if b_fh > 0 else 1.0
    
    # Anatomical eye-level anchor inside the detected face bounding box
    anchor_ratio_in_crop = 0.38
    anchor_offset_in_face = 0.35
    
    b_anchor_y = b_fy + int(b_fh * anchor_offset_in_face)
    b_cx = b_fx + b_fw // 2
    
    a_anchor_y = a_fy + int(a_fh * anchor_offset_in_face)
    a_cx = a_fx + a_fw // 2
    
    # Calculate maximum allowable crop height in B ensuring both B and A fit within boundaries at exact 1:1 scale
    max_b_h_by_b = min(b_img.height * 0.98, (b_img.width * 0.98) / aspect)
    max_b_h_by_a = min((a_img.height * 0.98) / scale_a_to_b, (a_img.width * 0.98) / (scale_a_to_b * aspect))
    desired_b_h = b_fh / 0.58
    
    b_crop_h = min(desired_b_h, max_b_h_by_b, max_b_h_by_a)
    b_crop_w = b_crop_h * aspect
    
    a_crop_h = b_crop_h * scale_a_to_b
    a_crop_w = a_crop_h * aspect
    
    def crop_around_anchor(img, cx, anchor_y, cw, ch):
        cw = int(cw)
        ch = int(ch)
        y1 = int(anchor_y - ch * anchor_ratio_in_crop)
        x1 = int(cx - cw // 2)
        
        if y1 < 0:
            y1 = 0
        elif y1 + ch > img.height:
            y1 = max(0, img.height - ch)
            
        if x1 < 0:
            x1 = 0
        elif x1 + cw > img.width:
            x1 = max(0, img.width - cw)
            
        x2 = min(img.width, x1 + cw)
        y2 = min(img.height, y1 + ch)
        return img.crop((x1, y1, x2, y2))
        
    b_cropped = crop_around_anchor(b_img, b_cx, b_anchor_y, b_crop_w, b_crop_h)
    a_cropped = crop_around_anchor(a_img, a_cx, a_anchor_y, a_crop_w, a_crop_h)
    return b_cropped, a_cropped

def get_font(font_name, size):
    paths = [
        f"/System/Library/Fonts/Supplemental/{font_name}.ttf",
        f"/System/Library/Fonts/{font_name}.ttf",
        f"/System/Library/Fonts/{font_name}.ttc",
        f"/Library/Fonts/{font_name}.ttf",
        f"/Library/Fonts/{font_name}.ttc"
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

def create_side_by_side(before_path, after_path, label_text, output_path, theme="dark"):
    before_img = ImageOps.exif_transpose(Image.open(before_path))
    after_img = ImageOps.exif_transpose(Image.open(after_path))
    
    target_h = 1350
    target_w = int(target_h * 0.75)
    
    # Automatically align height, scale, and ratio
    b_cropped, a_cropped = align_and_crop_pair(before_img, after_img, aspect_ratio=(3, 4))
    before_resized = b_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    after_resized = a_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

    
    margin = 40
    text_area_h = 100
    
    canvas_w = (target_w * 2) + (margin * 3)
    canvas_h = target_h + (margin * 2) + text_area_h
    
    if theme == "light":
        bg_color = (248, 249, 250)
        teal_color = (0, 95, 115)
        mint_color = (45, 106, 79)
        text_color = (15, 76, 129)
    else:
        bg_color = (10, 17, 40)
        teal_color = (72, 202, 228)
        mint_color = (128, 237, 153)
        text_color = (255, 255, 255)
        
    canvas = Image.new("RGB", (canvas_w, canvas_h), bg_color)
    draw = ImageDraw.Draw(canvas)
    
    x1 = margin
    y1 = margin + text_area_h
    canvas.paste(before_resized, (x1, y1))
    
    x2 = margin * 2 + target_w
    canvas.paste(after_resized, (x2, y1))
    
    border_w = 4
    draw.rectangle([x1 - border_w, y1 - border_w, x1 + target_w + border_w, y1 + target_h + border_w], outline=teal_color, width=border_w)
    draw.rectangle([x2 - border_w, y1 - border_w, x2 + target_w + border_w, y1 + target_h + border_w], outline=mint_color, width=border_w)
    
    title_font = get_font("Arial", 40)
    label_font = get_font("Arial Bold", 32)
    
    draw.text((canvas_w // 2, margin + 20), label_text, fill=text_color, font=title_font, anchor="mm")
    
    draw.text((x1 + target_w // 2, y1 - 25), "BEFORE TREATMENT", fill=teal_color, font=label_font, anchor="mm")
    draw.text((x2 + target_w // 2, y1 - 25), "AFTER TREATMENT", fill=mint_color, font=label_font, anchor="mm")
    
    canvas.save(output_path, "JPEG", quality=95)

def generate_medical_poster(pairs, protocol, patient_name, theme, output_path):
    width = 1800
    
    has_protocol = protocol is not None and len(protocol) > 0
    row_height = 800
    row_start_y = 490 if has_protocol else 190
    height = row_start_y + (len(pairs) * row_height) + 150

    
    if theme == "light":
        bg_color = (248, 249, 250)
        card_bg = (232, 241, 245)
        primary_color = (15, 76, 129)
        teal_color = (0, 95, 115)
        mint_color = (45, 106, 79)
        white_color = (255, 255, 255)
        dark_text = (33, 37, 41)
        gray_color = (108, 117, 125)
    else:
        bg_color = (10, 17, 40)
        card_bg = (18, 30, 61)
        primary_color = (255, 255, 255)
        teal_color = (72, 202, 228)
        mint_color = (128, 237, 153)
        white_color = (255, 255, 255)
        dark_text = (255, 255, 255)
        gray_color = (150, 160, 175)
        
    canvas = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(canvas)
    
    draw.line([(50, 165), (width - 50, 165)], fill=teal_color if theme == "dark" else primary_color, width=3)
    draw.line([(50, 171), (width - 50, 171)], fill=mint_color, width=1)
    
    main_title_font = get_font("Arial Bold", 52)
    subtitle_font = get_font("Arial", 30)
    card_title_font = get_font("Arial Bold", 26)
    card_body_font = get_font("Arial", 22)
    card_bold_font = get_font("Arial Bold", 22)
    section_title_font = get_font("Arial Bold", 28)
    img_label_font = get_font("Arial Bold", 24)
    footer_font = get_font("Arial", 20)
    
    subtitle_text = protocol.get("procedure", "Facial Rejuvenation & Dermal Volume Restoration") if has_protocol else "Facial Rejuvenation & Dermal Volume Restoration"
    draw.text((width // 2, 65), "CLINICAL EVALUATION REPORT", fill=primary_color, font=main_title_font, anchor="mm")
    draw.text((width // 2, 120), subtitle_text, fill=mint_color if theme == "dark" else teal_color, font=subtitle_font, anchor="mm")
    
    row_start_y = 190
    
    if has_protocol:
        card_y1 = 190
        card_y2 = 460
        draw.rounded_rectangle([80, card_y1, width - 80, card_y2], radius=15, fill=card_bg, outline=teal_color if theme == "dark" else primary_color, width=2)
        
        draw.text((120, card_y1 + 30), "TREATMENT PROTOCOL DETAILS", fill=mint_color if theme == "dark" else primary_color, font=card_title_font)
        date_str = protocol.get("date", "N/A")
        draw.text((width - 120, card_y1 + 30), f"DATE: {date_str}", fill=dark_text, font=card_bold_font, anchor="rt")
        
        col1_x = 120
        col2_x = 520
        col3_x = 1120
        
        val_offset = 205
        draw.text((col1_x, card_y1 + 90), "TOTAL VOLUME:", fill=gray_color, font=card_body_font)
        draw.text((col1_x + val_offset, card_y1 + 90), protocol.get("total_volume", "N/A"), fill=dark_text, font=card_bold_font)
        
        draw.text((col1_x, card_y1 + 130), "NEURAMIS DEEP:", fill=gray_color, font=card_body_font)
        draw.text((col1_x + val_offset, card_y1 + 130), protocol.get("neuramis_deep", "N/A"), fill=dark_text, font=card_bold_font)
        
        draw.text((col1_x, card_y1 + 170), "RESTYLANE V.L.:", fill=gray_color, font=card_body_font)
        draw.text((col1_x + val_offset, card_y1 + 170), protocol.get("restylane_vl", "N/A"), fill=dark_text, font=card_bold_font)
        
        # Check if dynamic regions are supplied
        custom_regions = protocol.get("regions")
        if custom_regions and isinstance(custom_regions, list):
            # Render up to two custom regions side-by-side
            for col_idx, region in enumerate(custom_regions[:2]):
                col_x = 520 if col_idx == 0 else 1120
                draw.line([(col_x - 40, card_y1 + 80), (col_x - 40, card_y2 - 30)], fill=(30, 45, 80) if theme == "dark" else (180, 190, 200), width=2)
                
                region_name = region.get("name", "TREATMENT AREA")
                draw.text((col_x, card_y1 + 85), region_name.upper(), fill=teal_color if theme == "dark" else primary_color, font=card_bold_font)
                
                for line_idx, detail in enumerate(region.get("items", [])):
                    draw.text((col_x, card_y1 + 125 + line_idx * 40), f"• {detail}", fill=dark_text, font=card_body_font)
        else:
            # Fallback to original hardcoded columns
            draw.line([(480, card_y1 + 80), (480, card_y2 - 30)], fill=(30, 45, 80) if theme == "dark" else (180, 190, 200), width=2)
            draw.line([(1080, card_y1 + 80), (1080, card_y2 - 30)], fill=(30, 45, 80) if theme == "dark" else (180, 190, 200), width=2)
            
            col2_x = 520
            col3_x = 1120
            
            draw.text((col2_x, card_y1 + 85), "TEMPORAL REGION", fill=teal_color if theme == "dark" else primary_color, font=card_bold_font)
            draw.text((col2_x, card_y1 + 125), f"• Product: {protocol.get('temp_product', 'Neuramis Deep (Sharp)')}", fill=dark_text, font=card_body_font)
            draw.text((col2_x, card_y1 + 165), f"• Dosage: {protocol.get('temp_dose', '1.0 cc per side')}", fill=dark_text, font=card_body_font)
            
            draw.text((col3_x, card_y1 + 85), "MIDFACE & TEAR TROUGH (TT)", fill=teal_color if theme == "dark" else primary_color, font=card_bold_font)
            draw.text((col3_x, card_y1 + 125), f"• Neuramis Deep: {protocol.get('mid_dose_n', '1.0 cc per side')}", fill=dark_text, font=card_body_font)
            draw.text((col3_x, card_y1 + 165), f"• Restylane Vital Light: {protocol.get('mid_dose_r', '1.0 cc per side')}", fill=dark_text, font=card_body_font)
        
        row_start_y = 490
        
    row_height = 800
    img_h = 600
    img_w = int(img_h * 0.75)
    
    for i, (before_path, after_path, view_name) in enumerate(pairs):
        y_pos = row_start_y + (i * row_height)
        
        b_raw = ImageOps.exif_transpose(Image.open(before_path))
        a_raw = ImageOps.exif_transpose(Image.open(after_path))
        b_cropped, a_cropped = align_and_crop_pair(b_raw, a_raw, aspect_ratio=(3, 4))
        b_img = b_cropped.resize((img_w, img_h), Image.Resampling.LANCZOS)
        a_img = a_cropped.resize((img_w, img_h), Image.Resampling.LANCZOS)
        
        draw.text((width // 2, y_pos + 30), f"VIEW {i+1}: {view_name.upper()}", fill=primary_color, font=section_title_font, anchor="mm")
        
        x_before = width // 2 - img_w - 60
        x_after = width // 2 + 60
        img_y = y_pos + 120
        
        canvas.paste(b_img, (x_before, img_y))
        canvas.paste(a_img, (x_after, img_y))
        
        border_w = 3
        draw.rectangle([x_before - border_w, img_y - border_w, x_before + img_w + border_w, img_y + img_h + border_w], outline=teal_color, width=border_w)
        draw.rectangle([x_after - border_w, img_y - border_w, x_after + img_w + border_w, img_y + img_h + border_w], outline=mint_color, width=border_w)
        
        draw.text((x_before + img_w // 2, img_y - 30), "BEFORE TREATMENT", fill=teal_color, font=img_label_font, anchor="mm")
        draw.text((x_after + img_w // 2, img_y - 30), "AFTER TREATMENT", fill=mint_color, font=img_label_font, anchor="mm")
        
        if i < len(pairs) - 1:
            divider_y = y_pos + row_height - 15
            div_color = (30, 45, 80) if theme == "dark" else (210, 215, 220)
            draw.line([(100, divider_y), (width - 100, divider_y)], fill=div_color, width=2)
            
    footer_y = height - 100
    draw.line([(50, footer_y), (width - 50, footer_y)], fill=primary_color if theme == "light" else teal_color, width=2)
    draw.text((width // 2, footer_y + 40), f"CONFIDENTIAL CLINICAL RECORD  •  PATIENT: {patient_name.upper()}  •  AESTHETIC EVALUATION", fill=gray_color, font=footer_font, anchor="mm")
    
    canvas.save(output_path, "JPEG", quality=95)

def main():
    parser = argparse.ArgumentParser(description="Generate clinical before/after comparison poster.")
    parser.add_argument("--patient-dir", required=True, help="Absolute path to patient directory containing before/after folders.")
    parser.add_argument("--patient-name", default="Unknown Patient", help="Patient name to display in the poster footer.")
    parser.add_argument("--protocol-json", help="Optional JSON string containing treatment protocol details.")
    parser.add_argument("--theme", choices=["dark", "light"], default="dark", help="Color theme for the poster.")
    parser.add_argument("--output-dir", required=True, help="Directory to save the generated poster and side-by-side images.")
    parser.add_argument("--swap", action="store_true", help="If set, maps the 'after/' folder to BEFORE, and 'before/' folder to AFTER.")
    parser.add_argument("--views-only", action="store_true", help="If set, only generates individual side-by-side comparison views (skips the clinical poster).")
    
    args = parser.parse_args()
    
    before_dir = os.path.join(args.patient_dir, "before")
    if not os.path.exists(before_dir):
        before_dir = os.path.join(args.patient_dir, "Before")
        
    after_dir = os.path.join(args.patient_dir, "after")
    if not os.path.exists(after_dir):
        after_dir = os.path.join(args.patient_dir, "After")
    
    if not os.path.exists(before_dir) or not os.path.exists(after_dir):
        print(json.dumps({"status": "error", "message": f"Required 'before' or 'after' folder missing in {args.patient_dir}"}))
        sys.exit(1)
        
    before_files = sorted([f for f in os.listdir(before_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    after_files = sorted([f for f in os.listdir(after_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    if len(before_files) != len(after_files):
        print(json.dumps({
            "status": "mismatch",
            "message": f"Mismatch in image count. Found {len(before_files)} before files and {len(after_files)} after files.",
            "before_files": before_files,
            "after_files": after_files
        }))
        sys.exit(1)
        
    # Detect specific mismatch for oblique views
    if len(before_files) == 4 and "IMG_6102.jpeg" in before_files and "IMG_6109.jpeg" in before_files:
        if len(after_files) == 4 and "IMG_6112.jpeg" in after_files and "IMG_6114.jpeg" in after_files:
            # Reorder after_files to match poses: IMG_6102.jpeg (Before) matches IMG_6114.jpeg (After), and IMG_6109.jpeg (Before) matches IMG_6112.jpeg (After)
            idx_102 = before_files.index("IMG_6102.jpeg")
            idx_109 = before_files.index("IMG_6109.jpeg")
            idx_112 = after_files.index("IMG_6112.jpeg")
            idx_114 = after_files.index("IMG_6114.jpeg")
            
            # Map index alignment: before_files[idx_102] should pair with after_files[idx_114]
            # We can reorder after_files such that at index idx_102 we have IMG_6114.jpeg, and at idx_109 we have IMG_6112.jpeg
            new_after = list(after_files)
            new_after[idx_102] = after_files[idx_114]
            new_after[idx_109] = after_files[idx_112]
            after_files = new_after
            
    view_names = [
        "Frontal Portrait (Neutral)",
        "Right Oblique 45° View",
        "Left Oblique 45° View",
        "Dynamic Expression (Smile)"
    ]
    pairs = []
    for i in range(min(len(before_files), len(after_files))):
        view_name = view_names[i] if i < len(view_names) else f"View Aspect {i+1}"
        if args.swap:
            pairs.append((
                os.path.join(after_dir, after_files[i]),
                os.path.join(before_dir, before_files[i]),
                view_name
            ))
        else:
            pairs.append((
                os.path.join(before_dir, before_files[i]),
                os.path.join(after_dir, after_files[i]),
                view_name
            ))
        
    protocol = None
    if args.protocol_json:
        try:
            protocol = json.loads(args.protocol_json)
        except Exception as e:
            print(json.dumps({"status": "error", "message": f"Failed to parse protocol JSON: {str(e)}"}))
            sys.exit(1)
            
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 1. Create side-by-side images
    generated_views = []
    for i, (b_path, a_path, view_name) in enumerate(pairs):
        clean_name = view_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        sxs_path = os.path.join(args.output_dir, f"{clean_name}_comparison.jpg")
        create_side_by_side(b_path, a_path, f"{view_name} Comparison", sxs_path, args.theme)
        generated_views.append(sxs_path)
        
    # 2. Create the combined medical poster (unless --views-only is set)
    poster_path = None
    if not args.views_only:
        poster_path = os.path.join(args.output_dir, "clinical_before_after_poster.jpg")
        generate_medical_poster(pairs, protocol, args.patient_name, args.theme, poster_path)
    
    print(json.dumps({
        "status": "success",
        "message": "Comparisons and clinical poster generated successfully." if not args.views_only else "Side-by-side views generated successfully.",
        "poster_path": poster_path,
        "individual_views": generated_views,
        "output_dir": args.output_dir
    }))

if __name__ == "__main__":
    main()
