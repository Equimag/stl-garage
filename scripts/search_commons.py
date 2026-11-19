import urllib.request
import urllib.parse
import json

def search(q):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(q)}&gsrnamespace=6&prop=imageinfo&iiprop=url|size&format=json&gsrlimit=10"
    req = urllib.request.Request(url, headers={"User-Agent": "StlGarageBot/1.0 (https://github.com/Equimag/stl-garage; equimag@gmail.com)"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode())
            pages = data.get("query", {}).get("pages", {})
            print(f"Query: {q}, count: {len(pages)}")
            for pid, p in pages.items():
                title = p.get("title")
                url_img = p.get("imageinfo", [{}])[0].get("url")
                size = p.get("imageinfo", [{}])[0].get("size", 0)
                print(f"  [{size} B] {title} -> {url_img}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    search('"3D print" cable')
    search('"3D printed" bracket')
    search('"3D printed" part')
