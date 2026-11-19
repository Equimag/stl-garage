import urllib.request
import re

def get_page_images(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    try:
        with urllib.request.urlopen(req, timeout=6) as r:
            html = r.read().decode("utf-8", errors="ignore")
            imgs = re.findall(r'https://[^"\'<>]+\.(?:jpg|png|webp)', html)
            return imgs
    except Exception as e:
        print(f"Error {url}: {e}")
        return []

if __name__ == "__main__":
    imgs = get_page_images("https://sgd3d.co.uk/")
    print(f"SGD3D count: {len(imgs)}")
    for im in imgs[:10]:
        print(" ", im)
