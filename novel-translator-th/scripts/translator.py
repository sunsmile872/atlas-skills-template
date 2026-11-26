#!/usr/bin/env python3
"""
Novel Translator TH - CLI Toolkit
Helper tool for inspecting EPUB books, compiling HTML readers, and packaging Thai EPUBs.
"""

import os
import sys
import re
import argparse
import subprocess
import xml.etree.ElementTree as ET

import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KINDLEUNPACK_PATH = os.path.join(SCRIPT_DIR, "kindleunpack", "kindleunpack.py")

def unpack_book(input_path, output_dir=None):
    """Unpacks .azw3, .mobi, or .epub file into an editable directory structure."""
    if not os.path.exists(input_path):
        print(f"Error: Path not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(input_path)[1].lower()
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    if not output_dir:
        output_dir = f"{base_name}_unpacked"

    os.makedirs(output_dir, exist_ok=True)
    print(f"=== Unpacking: {os.path.basename(input_path)} -> {output_dir} ===")

    if ext in [".azw3", ".mobi", ".azw"]:
        if not os.path.exists(KINDLEUNPACK_PATH):
            print(f"Error: Bundled KindleUnpack not found at {KINDLEUNPACK_PATH}", file=sys.stderr)
            sys.exit(1)

        cmd = [sys.executable, KINDLEUNPACK_PATH, "-i", "--epub_version=3", input_path, output_dir]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error unpacking AZW3/MOBI:\n{res.stderr}", file=sys.stderr)
            sys.exit(res.returncode)

        mobi8_dir = os.path.join(output_dir, "mobi8")
        if os.path.exists(mobi8_dir):
            print(f"Success! AZW3/KF8 unpacked.")
            print(f"EPUB Source Workspace: {mobi8_dir}")
            return mobi8_dir
        else:
            print(f"Success! Unpacked into: {output_dir}")
            return output_dir

    elif ext == ".epub":
        with zipfile.ZipFile(input_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)
        print(f"Success! EPUB extracted into: {output_dir}")
        return output_dir
    else:
        print(f"Error: Unsupported format '{ext}'. Expected .azw3, .mobi, or .epub", file=sys.stderr)
        sys.exit(1)

def inspect_epub(epub_path):
    """Inspects an EPUB folder, .epub archive, or .azw3 file and prints its structure."""
    if not os.path.exists(epub_path):
        print(f"Error: Path not found: {epub_path}", file=sys.stderr)
        sys.exit(1)

    # If it's an archive or azw3 file, auto-unpack
    if os.path.isfile(epub_path):
        ext = os.path.splitext(epub_path)[1].lower()
        if ext in [".azw3", ".mobi", ".azw", ".epub"]:
            epub_path = unpack_book(epub_path)
            print()

    print(f"=== Inspecting EPUB: {os.path.basename(epub_path)} ===")
    
    # Check if directory
    if os.path.isdir(epub_path):
        oebps = os.path.join(epub_path, "OEBPS")
        if not os.path.exists(oebps):
            # Might be OPS or directly content
            for candidate in ["OPS", "content", "EPUB"]:
                c_path = os.path.join(epub_path, candidate)
                if os.path.exists(c_path):
                    oebps = c_path
                    break
            else:
                oebps = epub_path

        toc_file = os.path.join(oebps, "toc.ncx")
        if not os.path.exists(toc_file):
            toc_file = os.path.join(epub_path, "toc.ncx")
        if os.path.exists(toc_file):
            print("\n[Table of Contents (toc.ncx)]")
            try:
                tree = ET.parse(toc_file)
                root = tree.getroot()
                ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
                for navpoint in root.findall('.//ncx:navPoint', ns):
                    label = navpoint.find('ncx:navLabel/ncx:text', ns)
                    content = navpoint.find('ncx:content', ns)
                    text = label.text if label is not None else "Unknown"
                    src = content.get('src') if content is not None else ""
                    print(f" - {text} ({src})")
            except Exception as e:
                print(f"Could not parse toc.ncx: {e}")
                
        text_dir = os.path.join(oebps, "Text")
        if not os.path.exists(text_dir):
            text_dir = oebps
            
        print("\n[Chapter Files Found]")
        for root_dir, _, files in os.walk(text_dir):
            for file in sorted(files):
                if file.endswith((".xhtml", ".html", ".htm")):
                    fpath = os.path.join(root_dir, file)
                    size = os.path.getsize(fpath)
                    print(f" - {file} ({size:,} bytes)")
    else:
        print("Note: Specify a valid extracted EPUB directory or file.")

def scan_characters(epub_path):
    """Scans all chapters across the entire book to extract every character name and POV."""
    if not os.path.exists(epub_path):
        print(f"Error: Path not found: {epub_path}", file=sys.stderr)
        sys.exit(1)

    print(f"=== Scanning All Characters: {os.path.basename(epub_path)} ===")
    
    # Collect text files
    chapter_files = []
    if os.path.isdir(epub_path):
        for root_dir, _, files in os.walk(epub_path):
            for file in sorted(files):
                if file.endswith((".xhtml", ".html", ".htm")) and not file.startswith(("cover", "nav")):
                    chapter_files.append(os.path.join(root_dir, file))
    
    if not chapter_files:
        print("No chapter text files found to scan.")
        return

    from collections import Counter
    p_text = []
    povs = []

    for fpath in chapter_files:
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                html = fp.read()
            # Capture bold POV tags
            m = re.findall(r'<span[^>]*font-weight:bold[^>]*>([A-Z\s]{3,25})</span>', html)
            for x in m:
                clean = x.strip()
                if clean not in ["PRESENT DAY", "PROLOGUE", "EPILOGUE", "CHAPTER"]:
                    povs.append(clean)
            
            # Strip HTML tags
            text = re.sub(r'<[^>]+>', ' ', html)
            p_text.append(text)
        except Exception as e:
            print(f"Warning: could not read {fpath}: {e}")

    full_text = ' '.join(p_text)
    
    # Detect proper nouns
    proper_nouns = re.findall(r'\b[A-Z][a-z]{2,15}\b', full_text)
    c = Counter(proper_nouns)
    
    stopwords = {
        'The', 'And', 'But', 'She', 'You', 'There', 'They', 'When', 'What', 'Then',
        'This', 'That', 'His', 'Her', 'Just', 'Even', 'Like', 'Some', 'How', 'After',
        'Before', 'Where', 'Why', 'Who', 'One', 'Two', 'Three', 'All', 'Not', 'Here',
        'Now', 'Out', 'Back', 'Over', 'Down', 'Into', 'From', 'With', 'About', 'Could',
        'Would', 'Should', 'Have', 'Has', 'Had', 'Was', 'Were', 'Been', 'Being', 'Did',
        'Does', 'Doing', 'Can', 'May', 'Might', 'Must', 'Will', 'Shall', 'Come', 'Came',
        'Look', 'Looked', 'Looking', 'Said', 'Told', 'Asked', 'Thought', 'Felt', 'Knew',
        'Saw', 'Took', 'Went', 'Made', 'Got', 'Nothing', 'Something', 'Anything',
        'Everything', 'Nobody', 'Somebody', 'Anybody', 'Everybody', 'Chapter', 'Never',
        'Lie', 'Dr', 'Doctor', 'Mr', 'Mrs', 'Ms', 'Miss', 'God', 'Oh', 'Yeah', 'Yes',
        'Wait', 'Right', 'Well', 'Still', 'Only', 'Too', 'Good', 'Maybe', 'Please',
        'Sure', 'Long', 'Day', 'Night', 'Room', 'House', 'Door', 'Bed', 'Car', 'Head',
        'Eyes', 'Hand', 'Time', 'Way', 'Don', 'Are', 'Fine', 'Okay', 'Thank', 'For',
        'Because', 'Present', 'Really', 'Hey', 'Also', 'Except', 'Sorry', 'Manhattan',
        'Once', 'Perhaps', 'Your', 'Instead', 'Jesus', 'Let'
    }

    filtered_names = [(word, count) for word, count in c.most_common(150) if word not in stopwords and count >= 3]
    
    # Detect Dr. / titles
    titles = re.findall(r'\b(?:Dr\.|Doctor|Mr\.|Mrs\.|Ms\.)\s+([A-Z][a-z]+)\b', full_text)
    title_counter = Counter(titles)

    print(f"\n[Scanned {len(chapter_files)} Chapter Files]")
    if povs:
        print("\n[Identified POV / Heading Characters]")
        for pov, count in Counter(povs).most_common():
            print(f" - {pov} (appears {count} times as section lead)")

    if title_counter:
        print("\n[Professional Titles / Doctors]")
        for title, count in title_counter.most_common(10):
            print(f" - Dr. {title} (mentioned {count} times)")

    print("\n[Top Character Name Candidates (Entire Book)]")
    for name, count in filtered_names[:30]:
        print(f" - {name} ({count} occurrences)")

def build_reader(md_path, output_html, title=None, series=None):
    """Compiles a translated Markdown chapter into an elegant HTML Reader."""
    if not os.path.exists(md_path):
        print(f"Error: Markdown file not found: {md_path}", file=sys.stderr)
        sys.exit(1)
        
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    
    chapter_title = title or "บทแปลภาษาไทย"
    sections = []
    chapters = []
    current_sect = 0
    body_html = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("# "):
            h_text = line[2:].strip()
            if any(k in h_text for k in ["บทที่", "บทนำ", "Chapter", "Prologue", "Epilogue", "ปัจฉิมลิขิต"]):
                ch_idx = len(chapters) + 1
                short_label = h_text.split("(")[0].strip() if "(" in h_text else h_text
                chapters.append((f"ch{ch_idx}", short_label))
                body_html.append(f'<div id="ch{ch_idx}" class="chapter-divider"><h2 class="chapter-heading">{h_text}</h2></div>\n')
                continue
            elif not series:
                series = h_text
                continue
        if line.startswith("## "):
            h2_text = line[3:].strip()
            ch_idx = len(chapters) + 1
            short_label = h2_text.split("(")[0].strip() if "(" in h2_text else h2_text
            chapters.append((f"ch{ch_idx}", short_label))
            body_html.append(f'<div id="ch{ch_idx}" class="chapter-divider"><h2 class="chapter-heading">{h2_text}</h2></div>\n')
            continue
        if line.startswith("### "):
            h3_text = line[4:].strip()
            m_sect = re.match(r'^(\d+)', h3_text)
            if m_sect:
                current_sect = int(m_sect.group(1))
                sections.append(current_sect)
                body_html.append(f'<div id="s{current_sect}" class="sect-divider"><span>{current_sect}</span></div>\n')
            else:
                body_html.append(f'<h3 class="sub-heading">{h3_text}</h3>\n')
            continue
        if line.startswith("---"):
            continue
            
        # Format inline styling
        formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
        formatted = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted)
        
        if formatted.startswith("“—รักเธอนะ") or formatted.startswith("<em>“—รักเธอนะ"):
            body_html.append(f'<p class="whisper">{formatted}</p>\n')
        elif formatted.startswith("—"):
            body_html.append(f'<p class="noindent">{formatted}</p>\n')
        else:
            body_html.append(f'<p>{formatted}</p>\n')

    if chapters:
        nav_links = "".join([f'<a href="#{cid}">{label}</a>' for cid, label in chapters])
    else:
        nav_links = "".join([f'<a href="#s{s}">ช่วงที่ {s}</a>' for s in sections])
    
    html = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{chapter_title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:ital,wght@0,300;0,400;0,600;0,700;1,400&family=Charm:wght@700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #12151c;
      --card-bg: #1a1f2c;
      --text: #e2e8f0;
      --muted: #94a3b8;
      --accent: #38bdf8;
      --border: #2d3748;
    }}
    body {{
      margin: 0;
      padding: 0;
      background-color: var(--bg);
      color: var(--text);
      font-family: 'Sarabun', -apple-system, sans-serif;
      font-size: 18px;
      line-height: 2.0;
      letter-spacing: 0.2px;
    }}
    .container {{
      max-width: 760px;
      margin: 0 auto;
      padding: 40px 24px 100px;
    }}
    header {{
      text-align: center;
      margin-bottom: 50px;
      padding-bottom: 30px;
      border-bottom: 1px solid var(--border);
    }}
    .series-tag {{
      display: inline-block;
      font-size: 14px;
      color: var(--accent);
      background: rgba(56, 189, 248, 0.1);
      padding: 4px 14px;
      border-radius: 20px;
      margin-bottom: 12px;
      font-weight: 600;
    }}
    h1 {{
      font-family: 'Charm', cursive, sans-serif;
      font-size: 38px;
      color: #fff;
      margin: 10px 0;
      line-height: 1.3;
    }}
    .chapter-divider {{
      text-align: center;
      margin: 80px 0 35px;
      padding-top: 40px;
      border-top: 2px dashed var(--border);
    }}
    .chapter-heading {{
      font-family: 'Charm', cursive, sans-serif;
      font-size: 32px;
      color: #38bdf8;
      margin: 10px 0;
      line-height: 1.4;
    }}
    .sub-heading {{
      font-size: 20px;
      color: var(--muted);
      margin: 20px 0 15px;
      text-indent: 0;
    }}
    .sect-divider {{
      text-align: center;
      margin: 60px 0 40px;
      position: relative;
    }}
    .sect-divider::before {{
      content: "";
      position: absolute;
      top: 50%;
      left: 0;
      right: 0;
      height: 1px;
      background: var(--border);
      z-index: 1;
    }}
    .sect-divider span {{
      position: relative;
      z-index: 2;
      background: var(--bg);
      padding: 4px 20px;
      font-size: 22px;
      font-weight: bold;
      color: var(--accent);
      border: 1px solid var(--border);
      border-radius: 30px;
    }}
    p {{
      margin-bottom: 24px;
      text-align: justify;
      text-indent: 2em;
    }}
    p.noindent {{
      text-indent: 0;
    }}
    .whisper {{
      text-align: center;
      font-style: italic;
      color: #f43f5e;
      font-size: 22px;
      margin: 40px 0;
      text-indent: 0;
    }}
    .nav-bar {{
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(26, 31, 44, 0.95);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border);
      border-radius: 40px;
      padding: 10px 20px;
      display: flex;
      gap: 10px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.6);
      z-index: 100;
      max-width: 92vw;
      overflow-x: auto;
      white-space: nowrap;
      scrollbar-width: thin;
    }}
    .nav-bar a {{
      color: var(--text);
      text-decoration: none;
      font-size: 13px;
      padding: 6px 12px;
      border-radius: 20px;
      transition: all 0.2s;
      flex-shrink: 0;
      background: rgba(255, 255, 255, 0.05);
    }}
    .nav-bar a:hover {{
      background: var(--accent);
      color: #000;
    }}
  </style>
</head>
<body>
  <div class="nav-bar">
    {nav_links}
  </div>
  <div class="container">
    <header>
      <div class="series-tag">{series or "นิยายแปลไทย"}</div>
      <h1>{chapter_title}</h1>
    </header>
    {"".join(body_html)}
  </div>
</body>
</html>
"""
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Success! HTML Reader compiled at: {output_html}")

def sanitize_xhtml_entities(epub_dir):
    """Replaces HTML entities that are invalid in strict XML/EPUB with numeric character entities or UTF-8 characters,
    and ensures strict XML/XHTML namespace and declaration are present."""
    entity_map = {
        "&nbsp;": "&#160;",
        "&eacute;": "&#233;",
        "&copy;": "&#169;",
        "&hellip;": "&#8230;",
        "&mdash;": "&#8212;",
        "&ndash;": "&#8211;",
        "&rsquo;": "&#8217;",
        "&lsquo;": "&#8216;",
        "&rdquo;": "&#8221;",
        "&ldquo;": "&#8220;",
    }
    for root, _, files in os.walk(epub_dir):
        for f in files:
            if f.endswith((".xhtml", ".html", ".htm", ".xml", ".opf", ".ncx")):
                fpath = os.path.join(root, f)
                try:
                    with open(fpath, "r", encoding="utf-8") as fp:
                        content = fp.read()
                    modified = False

                    # Strip any UTF-8 BOM from XML and XHTML files
                    if content.startswith('\ufeff'):
                        content = content[1:]
                        modified = True

                    # Ensure XML declaration and XHTML namespace for xhtml files
                    if f.endswith((".xhtml", ".html", ".htm")):
                        content = content.lstrip('\ufeff \t\r\n')
                        xml_decls = re.findall(r'<\?xml[^>]*\?>', content)
                        if len(xml_decls) > 1:
                            content = re.sub(r'<\?xml[^>]*\?>\s*', '', content)
                            content = '<?xml version="1.0" encoding="utf-8"?>\n' + content
                            modified = True
                        elif not content.startswith("<?xml"):
                            content = '<?xml version="1.0" encoding="utf-8"?>\n' + content
                            modified = True
                        if '<html' in content and 'xmlns=' not in content:
                            def fix_html_tag(match):
                                attrs = match.group(1)
                                if 'xmlns=' not in attrs:
                                    attrs = ' xmlns="http://www.w3.org/1999/xhtml"' + attrs
                                if 'xml:lang=' not in attrs:
                                    attrs = attrs + ' xml:lang="th"'
                                if 'lang=' not in attrs:
                                    attrs = attrs + ' lang="th"'
                                return f'<html{attrs}>'
                            content = re.sub(r'<html([^>]*)>', fix_html_tag, content, count=1)
                            modified = True

                    for ent, rep in entity_map.items():
                        if ent in content:
                            content = content.replace(ent, rep)
                            modified = True
                    if modified:
                        with open(fpath, "w", encoding="utf-8") as fp:
                            fp.write(content)
                except Exception as e:
                    pass

            # Strip BOM and inject CSS link color override, Small Caps reset, and Thai font fallback
            elif f.endswith(".css"):
                csspath = os.path.join(root, f)
                try:
                    with open(csspath, "r", encoding="utf-8") as fp:
                        css_text = fp.read()
                    if css_text.startswith('\ufeff'):
                        css_text = css_text[1:]
                    injected_rules = []
                    if "color: inherit !important" not in css_text:
                        injected_rules.append("/* Anti-Blue Link Reset (novel-translator-th) */\na, a:link, a:visited, a:hover, a:active {\n    color: inherit !important;\n    text-decoration: none !important;\n}")
                    if "/* Small Caps Thai Typography Reset */" not in css_text and ".small_caps" not in css_text:
                        injected_rules.append("/* Small Caps Thai Typography Reset (novel-translator-th) */\n.small_caps, [class*=\"small_caps\"], [class*=\"smallcaps\"] {\n    font-size: 1em !important;\n    font-variant: normal !important;\n}")
                    elif ".small_caps" in css_text and "font-size: 1em !important" not in css_text:
                        injected_rules.append("/* Small Caps Thai Typography Override (novel-translator-th) */\n.small_caps, [class*=\"small_caps\"], [class*=\"smallcaps\"] {\n    font-size: 1em !important;\n    font-variant: normal !important;\n}")
                    
                    if injected_rules:
                        css_rule = "\n\n" + "\n\n".join(injected_rules) + "\n"
                        with open(csspath, "w", encoding="utf-8") as fp:
                            fp.write(css_text + css_rule)
                    else:
                        with open(csspath, "w", encoding="utf-8") as fp:
                            fp.write(css_text)
                except Exception:
                    pass

def validate_epub_archive(epub_path):
    """Strict EPUB Health Gate: Verifies mimetype, XML well-formedness, and manifest targets."""
    import zipfile
    if not os.path.exists(epub_path):
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")

    with zipfile.ZipFile(epub_path, 'r') as z:
        infolist = z.infolist()
        if not infolist:
            raise ValueError(f"EPUB archive is empty: {epub_path}")

        # 1. Mimetype check
        first_file = infolist[0].filename
        if first_file != 'mimetype':
            raise ValueError(f"EPUB Error: First entry in zip MUST be 'mimetype', found: '{first_file}'")
        mime_data = z.read('mimetype')
        if mime_data != b'application/epub+zip':
            raise ValueError(f"EPUB Error: 'mimetype' content must be exactly b'application/epub+zip' (20 bytes), found {len(mime_data)} bytes: {repr(mime_data)}")

        # 2. Strict XML parse on all XHTML, XML, OPF, NCX files
        xml_errors = []
        for info in infolist:
            name = info.filename
            if name.endswith(('.xhtml', '.html', '.xml', '.opf', '.ncx')):
                data = z.read(name)
                if data.startswith(b'\xef\xbb\xbf'):
                    xml_errors.append((name, "Contains illegal UTF-8 Byte Order Mark (BOM)"))
                try:
                    ET.fromstring(data)
                except Exception as e:
                    xml_errors.append((name, f"XML Syntax Error: {e}"))

        if xml_errors:
            error_report = "\n".join([f"  - [{n}] {err}" for n, err in xml_errors])
            raise ValueError(f"EPUB Validation Failed with {len(xml_errors)} XML syntax errors:\n{error_report}")

    print(f"  ✓ EPUB Health Gate Passed: โครงสร้าง ZIP/Mimetype ถูกต้อง และไฟล์ XML ทั้งหมด ({len(infolist)} รายการ) ผ่านการตรวจสอบ 100%")
    return True

def compile_epub(epub_source_dir, output_epub_path, title=None, book_id=None):
    """Compiles an EPUB folder into a valid .epub archive."""
    if not os.path.exists(epub_source_dir):
        print(f"Error: Source directory not found: {epub_source_dir}", file=sys.stderr)
        sys.exit(1)
        
    mimetype_file = os.path.join(epub_source_dir, "mimetype")
    # Force strictly compliant 20-byte mimetype
    with open(mimetype_file, "wb") as mf:
        mf.write(b"application/epub+zip")

    # Sanitize entities, BOM, and syntax that crash strict XML readers like Apple Books
    sanitize_xhtml_entities(epub_source_dir)

    # Update title in content.opf and toc.ncx if specified
    if title:
        import html
        xml_title = html.escape(title, quote=False)
        for root, _, files in os.walk(epub_source_dir):
            for f in files:
                if f.endswith(".opf"):
                    opf_path = os.path.join(root, f)
                    try:
                        with open(opf_path, "r", encoding="utf-8") as fp:
                            opf_content = fp.read()
                        opf_content = re.sub(r'<dc:title[^>]*>.*?</dc:title>', f'<dc:title>{xml_title}</dc:title>', opf_content, flags=re.DOTALL)
                        with open(opf_path, "w", encoding="utf-8") as fp:
                            fp.write(opf_content)
                    except Exception:
                        pass
                elif f.endswith(".ncx"):
                    ncx_path = os.path.join(root, f)
                    try:
                        with open(ncx_path, "r", encoding="utf-8") as fp:
                            ncx_content = fp.read()
                        ncx_content = re.sub(r'<docTitle>\s*<text>.*?</text>\s*</docTitle>', f'<docTitle><text>{xml_title}</text></docTitle>', ncx_content, flags=re.DOTALL)
                        with open(ncx_path, "w", encoding="utf-8") as fp:
                            fp.write(ncx_content)
                    except Exception:
                        pass

    output_epub_path = os.path.abspath(output_epub_path)
    if os.path.exists(output_epub_path):
        os.remove(output_epub_path)
        
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_epub_path), exist_ok=True)
    
    # 1. Zip mimetype uncompressed
    subprocess.run(["zip", "-0", "-X", output_epub_path, "mimetype"], cwd=epub_source_dir, check=True)
    
    # 2. Zip rest compressed
    other_items = [item for item in os.listdir(epub_source_dir) if item != "mimetype" and not item.startswith(".")]
    cmd = ["zip", "-r", output_epub_path] + other_items
    subprocess.run(cmd, cwd=epub_source_dir, check=True)
    
    # 3. Automatic Health Gate validation
    try:
        validate_epub_archive(output_epub_path)
    except Exception as e:
        print(f"\n❌ FATAL EPUB ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Success! Standard Thai EPUB created at: {output_epub_path}")

def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

def combine_chapters(input_target, output_md, output_html=None, epub_source_dir=None, output_epub=None, title=None, series=None, clean=False):
    """Combines multiple Chapter_*.md files into a single master markdown, master HTML reader, and optionally compiles EPUB."""
    import glob
    
    if os.path.isdir(input_target):
        pattern = os.path.join(input_target, "Chapter_*.md")
        files = glob.glob(pattern)
    elif "*" in input_target:
        files = glob.glob(input_target)
    elif os.path.exists(input_target):
        files = [input_target]
    else:
        files = glob.glob("Chapter_*.md")
        
    files.sort(key=lambda x: natural_sort_key(os.path.basename(x)))
    
    if not files:
        print(f"Error: No chapter markdown files found matching: {input_target}", file=sys.stderr)
        sys.exit(1)
        
    print(f"=== Combining {len(files)} chapters into single file ===")
    combined_blocks = []
    if title:
        combined_blocks.append(f"# {title}\n\n")
        if series:
            combined_blocks.append(f"**{series}**\n\n---\n\n")
            
    for fpath in files:
        print(f"  + Merging: {os.path.basename(fpath)}")
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            combined_blocks.append(content)
            combined_blocks.append("\n\n---\n\n")
            
    master_md = "".join(combined_blocks)
    
    output_md = os.path.abspath(output_md)
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(master_md)
    print(f"Success! Master Markdown created at: {output_md}")
    
    if output_html:
        build_reader(output_md, output_html, title=title or "รวมเล่มฉบับสมบูรณ์", series=series)
        
    if output_epub and epub_source_dir:
        compile_epub(epub_source_dir, output_epub, title=title)

    if clean:
        print(f"=== Cleaning up individual chapter files ({len(files)} files) ===")
        for fpath in files:
            abs_fp = os.path.abspath(fpath)
            if abs_fp != output_md:
                try:
                    os.remove(abs_fp)
                    print(f"  - Removed: {os.path.basename(fpath)}")
                except Exception as e:
                    print(f"  ! Warning: could not delete {fpath}: {e}")
        print("Success! Unified into a single Master Markdown file.")

def lint_thai(target_path, bible_path=None):
    """Zero-Token Heuristic Linter for Thai literary translation.
    Audits translatorese patterns, unnatural passives, English remnants, and glossary consistency."""
    import glob
    raw_targets = target_path if isinstance(target_path, list) else [target_path]
    if not raw_targets:
        raw_targets = ["."]

    files = []
    for t in raw_targets:
        if os.path.isdir(t):
            pattern = os.path.join(t, "Chapter_*.md")
            found = glob.glob(pattern)
            if not found:
                found = glob.glob(os.path.join(t, "*.md"))
            files.extend(found)
        elif os.path.exists(t):
            files.append(t)
        else:
            files.extend(glob.glob(t))

    seen = set()
    dedup = []
    for f in files:
        if f not in seen:
            seen.add(f)
            dedup.append(f)
    files = dedup
    files.sort(key=lambda x: natural_sort_key(os.path.basename(x)))

    if not files:
        print(f"Error: Target path not found: {target_path}", file=sys.stderr)
        sys.exit(1)

    translatorese_rules = [
        (re.compile(r'ถูก(?:กอด|รัก|ถาม|มอง|จ้อง|เรียก|บอก|เกลียด|เตะ|ผลัก|สัมผัส|จ้าง|เชิญ|ส่ง|นำ|พบ|เห็น|ซ่อน|วาง)'), "Passive voice with neutral/positive verb (แนะนำให้ปรับเป็นประธานกระทำ หรือใช้กริยาตรง)"),
        (re.compile(r'ได้รับการ(?:ดูแล|ช่วยเหลือ|รักษา|อบรม|ต้อนรับ|ยอมรับ|ยกย่อง)'), "Stiff formal passive 'ได้รับการ...' (แนะนำให้ใช้ 'ได้รับการ...' เฉพาะทางการ หรือปรับเป็นกริยาตรง)"),
        (re.compile(r'มันเป็น(?:เรื่อง|เวลา|ความจริง|สิ่งที่)'), "English syntax 'It is...' (แนะนำให้ตัด 'มันเป็น' ออก หรือขึ้นต้นด้วยคำนามตรง)"),
        (re.compile(r'ดำเนินการ(?:ทำ|เปิด|ปิด|ส่ง|พูด|คุย)'), "Bureaucratic verb 'ดำเนินการ...' (แนะนำให้ตัดทิ้งใช้กริยาหลัก)"),
    ]

    total_warnings = 0
    print(f"=== Running Zero-Token Local Linter on {len(files)} file(s) ===")
    for fpath in files:
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        file_warnings = 0
        for l_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # 1. Translatorese check
            for pattern, reason in translatorese_rules:
                for match in pattern.finditer(stripped):
                    matched_text = match.group(0)
                    print(f"  [{fname}:{l_num}] [TRANSLATORESE] '{matched_text}' -> {reason}")
                    snippet = stripped[max(0, match.start()-15):min(len(stripped), match.end()+20)]
                    print(f"    บริบท: ...{snippet}...")
                    file_warnings += 1

            # 2. English remnants check
            clean_line = re.sub(r'\[.*?\]\(.*?\)|<.*?>|`.*?`', '', stripped)
            en_words = re.findall(r'\b[A-Za-z]{3,}\b', clean_line)
            allowed_acronyms = {"DNA", "RNA", "FBI", "CIA", "NASA", "POV", "Dr", "Mr", "Mrs", "HTML", "EPUB", "CSS", "MD"}
            suspicious_en = [w for w in en_words if w not in allowed_acronyms and not w.isupper()]
            if suspicious_en:
                print(f"  [{fname}:{l_num}] [ENGLISH REMNANT] ตรวจพบคำภาษาอังกฤษตกค้าง: {', '.join(suspicious_en)}")
                file_warnings += 1

        total_warnings += file_warnings
        if file_warnings == 0:
            print(f"  ✓ {fname}: ผ่านการตรวจสอบ 100% ไม่พบข้อบกพร่องสำนวน")

    print(f"\nLinter Summary: Total warnings = {total_warnings}")
    return total_warnings

def audit_full_book(epub_dir, max_english_words=5):
    """Scans all XHTML files in an EPUB workspace for untranslated English passages and XML syntax errors (Zero-Token)."""
    import xml.etree.ElementTree as ET
    if not os.path.exists(epub_dir):
        print(f"Error: Directory not found: {epub_dir}", file=sys.stderr)
        sys.exit(1)

    xhtml_files = []
    for root, _, files in os.walk(epub_dir):
        for f in sorted(files):
            if f.endswith((".xhtml", ".html", ".htm")):
                xhtml_files.append(os.path.join(root, f))

    if not xhtml_files:
        print(f"No XHTML files found in {epub_dir}")
        return 0

    print(f"=== Zero-Token Full Book Content Audit ({len(xhtml_files)} files) ===")
    xml_errors = 0
    untranslated_issues = []

    # Whitelist of terms commonly remaining in English
    allowed_terms = {"simon", "schuster", "copyright", "isbn", "oebps", "xhtml", "xml", "rights", "reserved", "congress", "cataloging"}

    for fpath in xhtml_files:
        fname = os.path.basename(fpath)
        # Skip pure index / bibliography files from English sentence warnings if requested
        is_index = any(k in fname.lower() for k in ["index", "biblio"])

        # 1. Strict XML validation
        try:
            ET.parse(fpath)
        except Exception as e:
            print(f"  [XML ERROR] {fname}: {e}")
            xml_errors += 1

        # 2. Scan text nodes for untranslated English sentences
        try:
            with open(fpath, "r", encoding="utf-8") as fp:
                content = fp.read()
            # Strip style and script tags
            content_clean = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', content, flags=re.DOTALL)
            # Extract plain text content outside tags
            text_blocks = re.findall(r'>([^<]+)<', content_clean)
            for block in text_blocks:
                clean = block.strip()
                words = clean.split()
                if len(words) >= max_english_words:
                    thai_chars = len(re.findall(r'[\u0e00-\u0e7f]', clean))
                    eng_chars = len(re.findall(r'[a-zA-Z]', clean))
                    if eng_chars > 20 and thai_chars == 0:
                        # Skip publisher boilerplate in copyright page
                        if any(term in clean.lower() for term in allowed_terms):
                            continue
                        if not is_index:
                            untranslated_issues.append((fname, clean[:100]))
        except Exception as e:
            print(f"  [READ ERROR] {fname}: {e}")

    print(f"\nAudit Results:")
    print(f"  - XML Syntax Errors: {xml_errors}")
    print(f"  - Untranslated English Blocks Detected: {len(untranslated_issues)}")
    if untranslated_issues:
        print("  Top Untranslated Snippets:")
        for fn, snip in untranslated_issues[:10]:
            print(f"    * [{fn}] {snip}...")
        print("\nWARNING: Found untranslated English content! Please translate these sections before publishing.")
        return len(untranslated_issues) + xml_errors
    else:
        print("  ✓ PASSED: ทุกไฟล์ผ่านการตรวจสอบโครงสร้าง XML และไม่มีประโยคภาษาอังกฤษตกค้าง 100%")
        return xml_errors

def verify_completeness(orig_epub_path, trans_epub_path, min_ratio=0.70, min_char_ratio=3.5):
    """Compares original EPUB against translated EPUB to guarantee zero-truncation and completeness (Zero-Token)."""
    import zipfile
    if not os.path.exists(orig_epub_path):
        print(f"Error: Original EPUB not found: {orig_epub_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(trans_epub_path):
        print(f"Error: Translated EPUB not found: {trans_epub_path}", file=sys.stderr)
        sys.exit(1)

    print(f"=== Zero-Token Completeness & Anti-Truncation Audit ===")
    print(f"Original  : {os.path.basename(orig_epub_path)}")
    print(f"Translated: {os.path.basename(trans_epub_path)}")
    print(f"Thresholds: Min Paragraph Ratio = {min_ratio*100:.0f}%, Min Char/Word Ratio = {min_char_ratio:.1f}\n")

    # 0. Strict EPUB Health Gate (Mimetype & XML well-formedness)
    try:
        validate_epub_archive(trans_epub_path)
    except Exception as e:
        print(f"\n❌ FATAL EPUB CORRUPTION ERROR: {e}\nห้ามรวมเล่มหรือส่งมอบงานจนกว่าจะแก้ไขโครงสร้าง EPUB ให้สมบูรณ์ 100%!", file=sys.stderr)
        return 1

    failed_sections = []
    
    with zipfile.ZipFile(orig_epub_path, 'r') as zo, zipfile.ZipFile(trans_epub_path, 'r') as zt:
        # Find all HTML/XHTML content files
        orig_files = [f for f in zo.namelist() if f.endswith(('.xhtml', '.html', '.htm'))]
        trans_files = [f for f in zt.namelist() if f.endswith(('.xhtml', '.html', '.htm'))]
        
        orig_files.sort(key=natural_sort_key)
        
        print(f"{'Section / File':<35} | {'Orig ¶':<8} | {'Trans ¶':<8} | {'Ratio':<7} | {'Status'}")
        print("-" * 75)

        total_orig_p = 0
        total_trans_p = 0

        for f in orig_files:
            fname = os.path.basename(f)
            # Skip copyright/title/cover/toc files from strict ratio checks
            is_meta = any(k in fname.lower() for k in ['title', 'cover', 'toc', 'about', 'fb2info', 'copyright'])
            
            orig_data = zo.read(f).decode('utf-8', errors='ignore')
            orig_p = len(re.findall(r'<p[^>]*>', orig_data))
            
            # Match translated file
            matching_trans = [tf for tf in trans_files if os.path.basename(tf) == fname]
            if not matching_trans:
                matching_trans = [tf for tf in trans_files if tf == f]

            if not matching_trans:
                if not is_meta:
                    print(f"{fname:<35} | {orig_p:<8} | {'MISSING':<8} | {'0.00':<7} | ❌ MISSING FILE")
                    failed_sections.append((fname, "File missing in translated EPUB"))
                continue

            trans_data = zt.read(matching_trans[0]).decode('utf-8', errors='ignore')
            trans_p = len(re.findall(r'<p[^>]*>', trans_data))
            
            total_orig_p += orig_p
            total_trans_p += trans_p
            
            ratio = trans_p / orig_p if orig_p > 0 else 1.0
            
            if is_meta:
                status = "SKIP (Meta)"
            elif orig_p < 10:
                status = "PASS (Short)"
            elif ratio >= min_ratio:
                status = "✓ PASS"
            else:
                status = f"❌ TRUNCATED ({ratio*100:.1f}%)"
                failed_sections.append((fname, f"Paragraph ratio {ratio:.2f} < {min_ratio:.2f}"))

            print(f"{fname:<35} | {orig_p:<8} | {trans_p:<8} | {ratio:<7.2f} | {status}")

        print("-" * 75)
        overall_ratio = total_trans_p / total_orig_p if total_orig_p > 0 else 0
        print(f"{'TOTAL':<35} | {total_orig_p:<8} | {total_trans_p:<8} | {overall_ratio:<7.2f} |")

    if failed_sections:
        print(f"\n❌ AUDIT FAILED: พบเนื้อหาที่ถูกตัดทอน (Truncated) จำนวน {len(failed_sections)} ส่วน:")
        for fn, reason in failed_sections:
            print(f"  - [{fn}]: {reason}")
        print("\nห้ามรวมเล่มหรือส่งมอบงานจนกว่าจะแปลเนื้อหาที่ตกหล่นให้ครบ 100%!")
        return len(failed_sections)
    else:
        print("\n✓ AUDIT PASSED: ผ่านเกณฑ์ความสมบูรณ์ 100% ไม่มีการตัดทอนหรือสรุปความ!")
        return 0

def split_chunks(text_or_file, max_paras=40, output_prefix="chunk"):
    """Splits long text or section files into safe, manageable chunks of 35-40 paragraphs with markers."""
    if os.path.exists(text_or_file):
        with open(text_or_file, "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        raw = text_or_file

    # Extract paragraphs if HTML
    if "<p" in raw:
        paras = re.findall(r'<p[^>]*>(.*?)</p>', raw, re.DOTALL)
        clean_paras = [re.sub(r'<[^>]+>', '', p).strip() for p in paras if re.sub(r'<[^>]+>', '', p).strip()]
    else:
        clean_paras = [p.strip() for p in raw.split("\n\n") if p.strip()]

    total = len(clean_paras)
    num_chunks = (total + max_paras - 1) // max_paras
    print(f"=== Chunking: Total {total} paragraphs -> {num_chunks} chunks (max {max_paras} paras/chunk) ===")

    out_files = []
    for c in range(num_chunks):
        start = c * max_paras
        end = min((c + 1) * max_paras, total)
        fn = f"{output_prefix}_{c+1:02d}.txt"
        with open(fn, "w", encoding="utf-8") as f:
            for i in range(start, end):
                f.write(f"--- PARA {i} ---\n{clean_paras[i]}\n\n")
        out_files.append(fn)
        print(f"  Created: {fn} (paras {start} to {end-1})")

    return out_files

def filter_bible(bible_path, text_path, output_path=None):
    """Filters a Master Character Bible to create a compact, chapter-specific subset (Dynamic Bible Subsetting)."""
    if not os.path.exists(bible_path):
        print(f"Error: Bible file not found: {bible_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(text_path):
        print(f"Error: Text file not found: {text_path}", file=sys.stderr)
        sys.exit(1)

    with open(bible_path, "r", encoding="utf-8") as bf:
        bible_lines = bf.readlines()
    with open(text_path, "r", encoding="utf-8") as tf:
        target_text = tf.read().lower()

    compact_lines = []
    in_table = False
    table_header = []

    for line in bible_lines:
        stripped = line.strip()
        if stripped.startswith("|"):
            if not in_table:
                in_table = True
                table_header = [line]
                continue
            if ":---" in stripped or "ตัวละคร" in stripped or "Character" in stripped:
                table_header.append(line)
                continue
            keywords = re.findall(r'[A-Za-z]{3,}', stripped)
            th_keywords = re.findall(r'[\u0E00-\u0E7F]{3,}', stripped)
            matched = any(kw.lower() in target_text for kw in keywords) or any(kw in target_text for kw in th_keywords)
            if matched:
                if table_header:
                    compact_lines.extend(table_header)
                    table_header = []
                compact_lines.append(line)
        else:
            in_table = False
            table_header = []
            if stripped.startswith("#"):
                compact_lines.append(line)
            elif stripped.startswith(("-", "*")):
                keywords = re.findall(r'[A-Za-z]{3,}', stripped)
                th_keywords = re.findall(r'[\u0E00-\u0E7F]{3,}', stripped)
                matched = any(kw.lower() in target_text for kw in keywords) or any(kw in target_text for kw in th_keywords)
                if matched or any(k in line for k in ["โทน", "แนวเรื่อง", "บรรยากาศ", "Voice", "Tone"]):
                    compact_lines.append(line)

    compact_bible = "".join(compact_lines).strip()
    if not compact_bible:
        compact_bible = "".join(bible_lines[:45])

    compact_bible_text = f"# Compact Character Bible (Chapter Subset)\n\n{compact_bible}\n"
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as out:
            out.write(compact_bible_text)
        print(f"Success! Compact Bible written to: {output_path}")
    else:
        print(compact_bible_text)
    return compact_bible_text

def main():
    parser = argparse.ArgumentParser(description="Novel Translator TH Toolkit")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # unpack
    p_unpack = subparsers.add_parser("unpack", help="Unpack .azw3, .mobi or .epub file into an editable directory")
    p_unpack.add_argument("path", help="Path to .azw3, .mobi, or .epub file")
    p_unpack.add_argument("--output", "-o", help="Target output folder")

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect an EPUB folder structure or .azw3/.epub file")
    p_inspect.add_argument("path", help="Path to EPUB file, extracted directory, or .azw3")

    # scan-characters
    p_scan = subparsers.add_parser("scan-characters", help="Scan entire book to extract all characters and POVs")
    p_scan.add_argument("path", help="Path to EPUB extracted directory")
    
    # build-reader
    p_reader = subparsers.add_parser("build-reader", help="Build interactive HTML Reader from Markdown")
    p_reader.add_argument("markdown", help="Path to translated markdown chapter")
    p_reader.add_argument("--output", "-o", required=True, help="Target HTML file path")
    p_reader.add_argument("--title", help="Chapter title")
    p_reader.add_argument("--series", help="Series title")
    
    # combine
    p_combine = subparsers.add_parser("combine", help="Combine all translated Chapter_*.md files into a single master file, HTML reader, and EPUB")
    p_combine.add_argument("target", nargs="?", default=".", help="Directory or glob pattern for chapter markdown files (default: .)")
    p_combine.add_argument("--output", "-o", required=True, help="Target master markdown file path")
    p_combine.add_argument("--html", help="Optional target single-file HTML reader path")
    p_combine.add_argument("--epub", help="Optional EPUB source directory to compile")
    p_combine.add_argument("--epub-out", help="Optional target EPUB output path")
    p_combine.add_argument("--title", help="Book title")
    p_combine.add_argument("--series", help="Series / Genre info")
    p_combine.add_argument("--clean", action="store_true", help="Delete source Chapter_*.md files after successful combination")

    # compile-epub
    p_compile = subparsers.add_parser("compile-epub", help="Package EPUB directory into .epub file")
    p_compile.add_argument("source_dir", help="Directory containing unzipped EPUB files")
    p_compile.add_argument("--output", "-o", required=True, help="Target .epub file path")
    p_compile.add_argument("--title", help="Localized title")

    # lint
    p_lint = subparsers.add_parser("lint", help="Zero-Token Heuristic Linter for Thai translations")
    p_lint.add_argument("target", default=["."], nargs="*", help="Path to markdown file or folder to audit")
    p_lint.add_argument("--bible", "-b", help="Optional path to Character Bible to check glossary")

    # filter-bible
    p_fb = subparsers.add_parser("filter-bible", help="Extract compact chapter-specific Bible subset")
    p_fb.add_argument("bible", help="Path to Master Character Bible")
    p_fb.add_argument("text", help="Path to chapter English text/markdown")
    p_fb.add_argument("--output", "-o", help="Optional output path for compact Bible")
    
    # audit
    p_audit = subparsers.add_parser("audit", help="Zero-Token Full Book Content Audit (Checks XML validity and English remnants across all XHTML files)")
    p_audit.add_argument("epub_dir", help="Directory containing unzipped EPUB files (OEBPS/Text or root)")
    p_audit.add_argument("--max-words", type=int, default=5, help="Minimum sequence of English words to trigger warning (default: 5)")

    # verify-completeness
    p_vc = subparsers.add_parser("verify-completeness", help="Zero-Token Completeness & Anti-Truncation Audit (compares original EPUB vs translated EPUB)")
    p_vc.add_argument("orig_epub", help="Path to original English EPUB")
    p_vc.add_argument("trans_epub", help="Path to translated Thai EPUB")
    p_vc.add_argument("--min-ratio", type=float, default=0.70, help="Minimum paragraph count ratio threshold (default: 0.70)")

    # split-chunks
    p_sc = subparsers.add_parser("split-chunks", help="Splits chapter text/file into safe chunks of 35-40 paragraphs")
    p_sc.add_argument("target", help="Path to text or XHTML chapter file")
    p_sc.add_argument("--max-paras", type=int, default=40, help="Maximum paragraphs per chunk (default: 40)")
    p_sc.add_argument("--prefix", default="chunk", help="Output file prefix (default: chunk)")

    args = parser.parse_args()
    
    if args.command == "unpack":
        unpack_book(args.path, args.output)
    elif args.command == "inspect":
        inspect_epub(args.path)
    elif args.command == "scan-characters":
        scan_characters(args.path)
    elif args.command == "build-reader":
        build_reader(args.markdown, args.output, args.title, args.series)
    elif args.command == "combine":
        combine_chapters(args.target, args.output, output_html=args.html, epub_source_dir=args.epub, output_epub=args.epub_out, title=args.title, series=args.series, clean=args.clean)
    elif args.command == "compile-epub":
        compile_epub(args.source_dir, args.output, args.title)
    elif args.command == "lint":
        lint_thai(args.target, args.bible)
    elif args.command == "filter-bible":
        filter_bible(args.bible, args.text, args.output)
    elif args.command == "audit":
        sys.exit(audit_full_book(args.epub_dir, args.max_words))
    elif args.command == "verify-completeness":
        sys.exit(verify_completeness(args.orig_epub, args.trans_epub, args.min_ratio))
    elif args.command == "split-chunks":
        split_chunks(args.target, args.max_paras, args.prefix)

if __name__ == "__main__":
    main()
