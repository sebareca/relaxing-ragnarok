#!/usr/bin/env python3
"""Download all Ragnarok Online sprites from spriters-resource.com"""
import os, json, re, time, sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://www.spriters-resource.com"
SPRITES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def fetch(url):
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req, timeout=20) as r:
            return r.read()
    except Exception as e:
        return None

def safe_name(name):
    return re.sub(r'[^\w\s\-\(\)&,]', '', name).strip().replace(' ', '_')

def categorize(pos, sections):
    """Find the section a position falls under."""
    current = "Unknown"
    for spos, sname in sections:
        if spos > pos:
            break
        current = sname
    return current

print("=== Ragnarok Online Sprite Downloader ===")

# Step 1: Parse HTML
print("[1/3] Parsing asset listing...")
html_path = '/tmp/ro_sprites_page.html'
if not os.path.exists(html_path):
    print("Downloading page...")
    data = fetch(f"{BASE}/pc_computer/ragnarokonline/")
    if not data:
        print("ERROR: Could not fetch page"); sys.exit(1)
    with open(html_path, 'wb') as f:
        f.write(data)

with open(html_path, 'r', errors='replace') as f:
    html = f.read()

# Extract section headers (the site uses class="...section..." divs)
sections = []
for m in re.finditer(r'class="[^"]*section[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL):
    text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    # Clean up - remove counts like [9] and arrow_drop_down
    text = re.sub(r'arrow_drop_down\s*', '', text)
    text = re.sub(r'\[\d+\]\s*', '', text).strip()
    if text and len(text) > 2:
        sections.append((m.start(), text))
sections.sort()

# Extract assets using the actual HTML structure
assets = []
for m in re.finditer(
    r'<a\s+href="/pc_computer/ragnarokonline/asset/(\d+)/"[^>]*>\s*'
    r'<div[^>]*class="iconcontainer"[^>]*>\s*'
    r'<div[^>]*class="iconheader"[^>]*title="([^"]*)"',
    html, re.DOTALL
):
    aid = int(m.group(1))
    name = m.group(2)
    # Find folder from nearby img src
    ctx = html[m.start():m.start()+500]
    folder_m = re.search(r'asset_icons/(\d+)/', ctx)
    folder = int(folder_m.group(1)) if folder_m else 0
    category = categorize(m.start(), sections)
    assets.append({
        "id": aid,
        "name": name,
        "category": category,
        "folder": folder,
        "pos": m.start()
    })

print(f"Found {len(assets)} assets in {len(sections)} sections")

# Show categories
cats = {}
for a in assets:
    cats[a['category']] = cats.get(a['category'], 0) + 1
for c, n in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {c}: {n}")

# Step 2: Download all
print(f"\n[2/3] Downloading {len(assets)} assets...")

def get_subfolder(category):
    cl = category.lower()
    if 'head' in cl and ('male' in cl or 'female' in cl or 'original' in cl):
        return 'heads'
    elif 'class' in cl:
        return 'classes'
    elif 'weapon' in cl:
        return 'weapons'
    elif 'enem' in cl:
        return 'enemies'
    elif 'headgear' in cl:
        return 'headgear'
    elif 'non-play' in cl or 'npc' in cl:
        return 'npcs'
    elif 'mount' in cl or 'premium' in cl:
        return 'mounts'
    else:
        return 'other'

def download_one(asset):
    aid = asset['id']
    folder = asset['folder']
    name = safe_name(asset['name'])
    subfolder = get_subfolder(asset['category'])
    dest_dir = os.path.join(SPRITES_DIR, subfolder)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, f"{name}_{aid}.png")
    asset['file'] = f"sprites/{subfolder}/{name}_{aid}.png"
    asset['subfolder'] = subfolder

    if os.path.exists(dest):
        return True, asset

    url = f"{BASE}/media/assets/{folder}/{aid}.png"
    data = fetch(url)
    if data and len(data) > 100:
        with open(dest, 'wb') as f:
            f.write(data)
        return True, asset
    return False, asset

downloaded = 0
failed = 0
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(download_one, a): a for a in assets}
    for i, future in enumerate(as_completed(futures)):
        success, asset = future.result()
        if success:
            downloaded += 1
        else:
            failed += 1
            asset['file'] = None
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i+1}/{len(assets)} (downloaded: {downloaded}, failed: {failed})")
        time.sleep(0.05)  # Be polite

print(f"\nDownloaded: {downloaded}, Failed: {failed}")

# Step 3: Write manifest
print("\n[3/3] Writing manifest...")
manifest = []
for a in assets:
    manifest.append({
        "id": a["id"],
        "name": a["name"],
        "category": a["category"],
        "subfolder": a.get("subfolder", "other"),
        "file": a.get("file"),
    })

manifest_path = os.path.join(SPRITES_DIR, "manifest.json")
with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2)
print(f"Manifest written: {len(manifest)} entries")
print("Done!")
