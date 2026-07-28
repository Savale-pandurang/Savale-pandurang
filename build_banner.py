#!/usr/bin/env python3
"""
Banner Generator for GitHub Profile
Generates theme-aware dark.svg and light.svg with:
- Terminal window chrome (1180x610)
- Left panel: Animated dot-matrix portrait (VISUAL.MAP)
- Right panel: SYSTEM.INFO readout with animated text, dotted leaders, and glowing badges
- Supports custom photo input or fallback high-density developer dot-art matrix
"""

import sys
import os
import math
import random
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

# Palette definitions matching arifhaxn theme
THEMES = {
    "dark": {
        "BG_OUTER": "#070B16",
        "PANEL_BG": "url(#panelGrad)",
        "PANEL_STOP1": "#0A101F",
        "PANEL_STOP2": "#0C1426",
        "HEADER_BG": "#0B1222",
        "BORDER_LINE": "rgba(255,255,255,0.10)",
        "TITLE_TEXT": "#94A3B8",
        "CYAN": "#22D3EE",
        "VIOLET": "#A78BFA",
        "VIOLET_PILL": "#7C3AED",
        "EMERALD": "#10B981",
        "TEXT": "#F8FAFC",
        "MUTED": "#94A3B8",
        "DIM": "#475569",
        "LEADER": "rgba(148,163,184,0.35)",
        "DOT_COLOR": "#A78BFA",
        "BOX_BG": "#0A101F",
        "BOX_STROKE": "rgba(34,211,238,0.35)",
        "GLOW_COLOR": "#22D3EE",
    },
    "light": {
        "BG_OUTER": "#F1F5F9",
        "PANEL_BG": "url(#panelGradLight)",
        "PANEL_STOP1": "#FFFFFF",
        "PANEL_STOP2": "#F8FAFC",
        "HEADER_BG": "#E2E8F0",
        "BORDER_LINE": "rgba(0,0,0,0.10)",
        "TITLE_TEXT": "#475569",
        "CYAN": "#0891B2",
        "VIOLET": "#7C3AED",
        "VIOLET_PILL": "#6D28D9",
        "EMERALD": "#059669",
        "TEXT": "#0F172A",
        "MUTED": "#475569",
        "DIM": "#94A3B8",
        "LEADER": "rgba(100,116,139,0.35)",
        "DOT_COLOR": "#6D28D9",
        "BOX_BG": "#FFFFFF",
        "BOX_STROKE": "rgba(8,145,178,0.35)",
        "GLOW_COLOR": "#0891B2",
    }
}

def generate_dots_from_image(image_path, target_w=300, target_h=340):
    """Processes an image into a dithered grid of dot coordinates."""
    try:
        img = Image.open(image_path).convert("L")
        img = ImageOps.fit(img, (target_w, target_h), Image.Resampling.LANCZOS)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.4)
        
        # Floyd-Steinberg dither
        dithered = img.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
        dots = []
        for y in range(target_h):
            for x in range(target_w):
                if dithered.getpixel((x, y)) == 0:  # Dark dot
                    dots.append((x, y))
        return dots
    except Exception as e:
        print(f"Warning: Could not process image {image_path}: {e}")
        return None

def generate_procedural_portrait(target_w=300, target_h=340):
    """Generates a procedural high-density developer particle silhouette."""
    random.seed(42)
    dots = []
    
    cx, cy = target_w / 2, 110
    head_rx, head_ry = 55, 70
    
    # Head and Face Contour
    for y in range(20, 200):
        for x in range(50, 250):
            dx = (x - cx) / head_rx
            dy = (y - cy) / head_ry
            dist = dx*dx + dy*dy
            
            # Hair top
            if y < 100 and dist <= 1.2:
                density = 0.85 - (y/200)*0.3
                if random.random() < density:
                    dots.append((x, y))
            # Face & Jaw structure
            elif dist <= 1.0:
                # Facial features (eyes, nose, mouth area variations)
                is_eye = (85 <= y <= 98) and ((cx-32 <= x <= cx-10) or (cx+10 <= x <= cx+32))
                is_mouth = (135 <= y <= 145) and (cx-20 <= x <= cx+20)
                is_glasses = (80 <= y <= 102) and (cx-42 <= x <= cx+42)
                
                if is_glasses:
                    density = 0.95
                elif is_eye:
                    density = 0.2
                elif is_mouth:
                    density = 0.3
                else:
                    density = 0.55 * (1 - dist*0.4)
                
                if random.random() < density:
                    dots.append((x, y))

    # Neck
    for y in range(170, 210):
        for x in range(int(cx-22), int(cx+22)):
            if random.random() < 0.6:
                dots.append((x, y))

    # Shoulders and Torso (Suit / Hoodie)
    for y in range(200, target_h):
        progress = (y - 200) / (target_h - 200)
        shoulder_w = 75 + progress * 85
        for x in range(int(cx - shoulder_w), int(cx + shoulder_w)):
            dx = abs(x - cx) / shoulder_w
            density = (1.0 - dx**2) * 0.75
            
            # V-neck / Collar cutout
            if y < 240 and abs(x - cx) < (y - 195) * 0.6:
                density *= 0.15
            
            if random.random() < density:
                dots.append((x, y))

    # Background ambient tech particles
    for _ in range(800):
        rx = random.randint(10, target_w - 10)
        ry = random.randint(10, target_h - 10)
        if random.random() < 0.12:
            dots.append((rx, ry))

    return dots

def build_svg(theme_name, dots, info_rows):
    t = THEMES[theme_name]
    
    # Group dots into staggered animation groups
    random.seed(101)
    random.shuffle(dots)
    num_groups = 50
    chunk_size = math.ceil(len(dots) / num_groups)
    dot_groups = [dots[i*chunk_size:(i+1)*chunk_size] for i in range(num_groups)]

    svg = []
    a = svg.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'Liberation Mono\',monospace" role="img" aria-label="Pandurang Savale — profile.sh --live">')
    
    # Definitions & Gradients
    a('<defs>')
    a(f'<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">')
    a(f'  <stop offset="0" stop-color="{t["VIOLET"]}"><animate attributeName="stop-color" values="{t["VIOLET"]};{t["CYAN"]};{t["EMERALD"]};{t["VIOLET"]}" dur="10s" repeatCount="indefinite"/></stop>')
    a(f'  <stop offset="0.5" stop-color="{t["CYAN"]}"><animate attributeName="stop-color" values="{t["CYAN"]};{t["EMERALD"]};{t["VIOLET"]};{t["CYAN"]}" dur="10s" repeatCount="indefinite"/></stop>')
    a(f'  <stop offset="1" stop-color="{t["EMERALD"]}"><animate attributeName="stop-color" values="{t["EMERALD"]};{t["VIOLET"]};{t["CYAN"]};{t["EMERALD"]}" dur="10s" repeatCount="indefinite"/></stop>')
    a('</linearGradient>')
    
    if theme_name == "dark":
        a(f'<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["PANEL_STOP1"]}"/><stop offset="1" stop-color="{t["PANEL_STOP2"]}"/></linearGradient>')
    else:
        a(f'<linearGradient id="panelGradLight" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["PANEL_STOP1"]}"/><stop offset="1" stop-color="{t["PANEL_STOP2"]}"/></linearGradient>')

    a('<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>')
    a('<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>')
    a('<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>')
    a('</defs>')

    # Outer Frame & Window
    a(f'<rect x="2" y="2" width="1176" height="606" rx="18" fill="{t["BG_OUTER"]}"/>')
    a('<g clip-path="url(#winClip)">')
    a(f'<rect x="2" y="2" width="1176" height="606" fill="{t["PANEL_BG"]}"/>')
    
    # Window Title Bar
    a(f'<rect x="2" y="2" width="1176" height="46" fill="{t["HEADER_BG"]}"/>')
    a(f'<line x1="2" y1="48" x2="1178" y2="48" stroke="{t["BORDER_LINE"]}"/>')
    a('<circle cx="30" cy="25.0" r="5.5" fill="#ff5f56"/>')
    a('<circle cx="50" cy="25.0" r="5.5" fill="#ffbd2e"/>')
    a('<circle cx="70" cy="25.0" r="5.5" fill="#27c93f"/>')
    a(f'<text x="590.0" y="29.0" text-anchor="middle" font-size="12" fill="{t["TITLE_TEXT"]}">pandusavale04@gmail.com - % ./profile.sh --live</text>')

    # LEFT PANEL — VISUAL.MAP
    a(f'<text x="38" y="74" font-size="10" letter-spacing="3" fill="{t["DIM"]}">VISUAL.MAP</text>')
    a(f'<rect x="36" y="84" width="400" height="492" rx="10" fill="none" stroke="{t["CYAN"]}" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>')
    a(f'<rect x="36" y="84" width="400" height="492" rx="10" fill="{t["BOX_BG"]}" stroke="{t["BOX_STROKE"]}"/>')

    # Portrait Particle Group Scale & Translation (50, 86)
    a(f'<g transform="translate(50,86) scale(1.24, 1.44)" fill="{t["DOT_COLOR"]}" shape-rendering="crispEdges">')
    
    # Render SMIL staggered fade-in groups
    start_delay = 0.20
    for idx, grp in enumerate(dot_groups):
        begin_t = start_delay + (idx * 0.05)
        path_data = []
        for x, y in grp:
            path_data.append(f"M{x} {y}h1v1h-1z")
        d_str = "".join(path_data)
        a(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.9s" begin="{begin_t:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/><path d="{d_str}"/></g>')
    
    a('</g>') # end portrait group

    # RIGHT PANEL — SYSTEM.INFO
    a(f'<text x="470" y="74" font-size="11" letter-spacing="3" fill="{t["CYAN"]}">SYSTEM.INFO</text>')
    a('<circle cx="1090" cy="71" r="4" fill="#ef4444"><animate attributeName="opacity" values="1;0.2;1" dur="1.5s" repeatCount="indefinite"/></circle>')
    a('<text x="1100" y="75" font-size="10" letter-spacing="1" fill="#ef4444" font-weight="700">LIVE</text>')

    # Contact Pill Badge
    a(f'<rect x="470" y="92" width="220" height="24" rx="6" fill="{t["VIOLET_PILL"]}"/>')
    a(f'<text x="580" y="108" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle">pandusavale04@gmail.com</text>')

    # Info Rows Animation
    row_y = 139
    begin_t = 0.8
    for item in info_rows:
        if item["type"] == "header":
            a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{begin_t:.2f}s" fill="freeze"/>')
            a(f'<text x="470" y="{row_y}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="{t["MUTED"]}">{item["label"]} </tspan><tspan fill="{t["LEADER"]}">---------------------------------------------------------------------</tspan></text></g>')
            row_y += 23
            begin_t += 0.12
        else:
            label = item["label"]
            val = item["value"]
            # Dots length calculation
            dots_str = "." * 60
            a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{begin_t:.2f}s" fill="freeze"/>')
            a(f'<animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="{begin_t:.2f}s" fill="freeze"/>')
            a(f'<text x="470" y="{row_y}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="{t["CYAN"]}">{label} </tspan><tspan fill="{t["LEADER"]}">{dots_str}</tspan><tspan fill="{t["TEXT"]}" font-weight="600"> {val}</tspan></text></g>')
            row_y += 23
            begin_t += 0.12

    # Footer note in right panel
    a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{begin_t+0.2:.2f}s" fill="freeze"/>')
    a(f'<text x="470" y="{row_y+10}" font-size="14" fill="{t["MUTED"]}">&#9656; More about me &amp; projects below in README &#8595; <tspan fill="{t["CYAN"]}">&#9608;<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text></g>')

    a('</g>') # end clip-path

    # Animated Gradient Border Accent
    a(f'<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="3" opacity="0.55" filter="url(#glow8)"/>')
    a(f'<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.6"/>')

    a('</svg>')
    return "\n".join(svg)

def main():
    img_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    dots = None
    if img_path and os.path.exists(img_path):
        print(f"Processing photo from {img_path}...")
        dots = generate_dots_from_image(img_path)
    
    if not dots:
        print("Generating procedural developer particle matrix...")
        dots = generate_procedural_portrait()

    info_rows = [
        {"type": "data", "label": "Subject", "value": "Pandurang Savale"},
        {"type": "data", "label": "Role", "value": "Data Scientist & ML Engineer"},
        {"type": "data", "label": "Origin", "value": "Karnataka, India"},
        {"type": "data", "label": "Education", "value": "B.E. in CSE (GPA: 8.5)"},
        {"type": "data", "label": "Status", "value": "Research Intern @ IIT Madras HTIC"},
        {"type": "data", "label": "ToolChain", "value": "Python, PyTorch, OpenCV, Git, Docker"},
        {"type": "data", "label": "Core.Lang", "value": "Python, SQL, C, Java, Solidity"},
        {"type": "data", "label": "Core.Frontend", "value": "HTML, CSS, TypeScript"},
        {"type": "data", "label": "Core.Backend", "value": "Python (FastAPI, Flask)"},
        {"type": "data", "label": "Core.Database", "value": "PostgreSQL, MongoDB"},
        {"type": "data", "label": "Core.Infra", "value": "AWS, Docker, Git"},
        {"type": "header", "label": "- Contact", "value": ""},
        {"type": "data", "label": "Grid.Mail", "value": "pandusavale04@gmail.com"},
        {"type": "data", "label": "Grid.Portfolio", "value": "github.com/Savale-pandurang"},
        {"type": "data", "label": "Grid.LinkedIn", "value": "pandurang-s-73596329a"},
        {"type": "data", "label": "Grid.GitHub", "value": "@Savale-pandurang"},
        {"type": "data", "label": "Grid.Phone", "value": "+91 9611573977"},
    ]

    out_dir = "/Users/pandu/Desktop/github/Savale-pandurang"
    
    dark_svg = build_svg("dark", dots, info_rows)
    with open(os.path.join(out_dir, "dark.svg"), "w") as f:
        f.write(dark_svg)
    print(f"Generated dark.svg ({len(dark_svg)//1024} KB)")

    light_svg = build_svg("light", dots, info_rows)
    with open(os.path.join(out_dir, "light.svg"), "w") as f:
        f.write(light_svg)
    print(f"Generated light.svg ({len(light_svg)//1024} KB)")

if __name__ == "__main__":
    main()
