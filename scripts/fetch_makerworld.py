import urllib.request
import re

urls = [
    "https://makerworld.com/en/models/14068",
    "https://makerworld.com/en/models/26079",
]

for url in urls:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            html = r.read().decode("utf-8", errors="ignore")
            # find og:image or makerworld cdn images
            og = re.findall(r'<meta property="og:image" content="([^"]+)"', html)
            imgs = re.findall(r'https://[^"\'<>]+\.(?:jpg|png|webp)', html)
            print(url)
            print("  OG image:", og)
            print("  Other imgs:", len(imgs))
            for im in imgs[:5]:
                print("   ", im)
    except Exception as e:
        print(url, "Error:", e)
