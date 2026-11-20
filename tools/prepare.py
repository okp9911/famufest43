"""Runs on GitHub after every upload (see .github/workflows/films.yml), or locally: python3 tools/prepare.py

- every video in films/ that would load badly is fixed: not an H.264 MP4 (e.g. an iPhone .mov), larger than
  5 MB, bigger than 1920x1080 or longer than 15 s is re-encoded (max 1280 px wide, 15 s, no sound);
  a good MP4 that only carries a sound track just has the sound removed
- every video gets a poster in posters/<same name>.jpg (the first thing the page loads):
  a still the organisers uploaded to posters/ under the video's name (jpg, png or webp, any size) is used
  and resized to 960 px; otherwise a frame is taken from the clip. Uploaded stills are never overwritten.
- every video or photo in films/ that is missing from films.csv gets a row (title = file name)
- automatic posters whose video is gone are removed (uploaded stills are kept)
Needs ffmpeg and ffprobe.
"""
import csv, hashlib, io, json, os, subprocess, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILMS, POSTERS, TABLE = (os.path.join(ROOT, x) for x in ("films", "posters", "films.csv"))
VIDEO = (".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi")
PHOTO = (".jpg", ".jpeg", ".png", ".webp", ".gif")
COLS = ["video", "title", "author", "duration"]
STILL = (".jpg", ".jpeg", ".png", ".webp")
LEDGER = os.path.join(ROOT, "posters", "made.txt")   # "<auto|still> <sha1> <file>" for every poster this script wrote
nfc = lambda s: unicodedata.normalize("NFC", s)

def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=codec_name,width,height:format=duration", "-of", "json", path],
                         capture_output=True, text=True).stdout or "{}"
    j = json.loads(out)
    st = (j.get("streams") or [{}])[0]
    return st.get("codec_name", ""), float((j.get("format") or {}).get("duration") or 0), int(st.get("height") or 0)

def has_audio(path):
    return bool(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                                "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip())

MAX_MB, MAX_S, MAX_H = 5, 15, 1080

def run(*args):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args], check=True)

def read_table():
    if not os.path.exists(TABLE):
        return ";", []
    text = open(TABLE, encoding="utf-8-sig").read()
    first = text.splitlines()[0] if text.strip() else ""
    delim = ";" if first.count(";") >= first.count(",") else ","
    rows = [{k.strip().lower(): (v or "").strip() for k, v in r.items() if k}
            for r in csv.DictReader(io.StringIO(text), delimiter=delim)]
    return delim, [r for r in rows if any(r.values())]

made = {}
def sha(p): return hashlib.sha1(open(p, "rb").read()).hexdigest()
def load_ledger():
    if os.path.exists(LEDGER):
        for line in open(LEDGER, encoding="utf-8"):
            parts = line.rstrip("\n").split(" ", 2)
            if len(parts) == 3: made[parts[2]] = (parts[0], parts[1])
def save_ledger():
    with open(LEDGER, "w", encoding="utf-8") as f:
        for name in sorted(made): f.write(f"{made[name][0]} {made[name][1]} {name}\n")

def make_poster(stem, video):
    target = os.path.join(POSTERS, stem + ".jpg")
    # a still uploaded by people: any image in posters/ with the video's name that this script did not write
    uploaded = None
    for p in sorted(os.listdir(POSTERS)):
        s, e = os.path.splitext(p)
        if e.lower() in STILL and nfc(s) == nfc(stem):
            full = os.path.join(POSTERS, p)
            if p in made and made[p][1] == sha(full): continue          # already prepared by this script
            uploaded = full; break
    if uploaded:
        tmp = target + ".tmp.jpg"
        run("-i", uploaded, "-vf", "scale='min(960,iw)':-2", "-q:v", "3", tmp)
        for p in os.listdir(POSTERS):                                     # drop other versions with this name
            s, e = os.path.splitext(p)
            if e.lower() in STILL and nfc(s) == nfc(stem): os.remove(os.path.join(POSTERS, p)); made.pop(p, None)
        os.replace(tmp, target); made[stem + ".jpg"] = ("still", sha(target))
        print("still", os.path.basename(uploaded), "->", stem + ".jpg", f"({os.path.getsize(target) // 1024} KB)"); return
    if not os.path.exists(target):
        _, dur, _ = probe(video)
        run("-ss", str(min(1.0, dur / 3 if dur else 0)), "-i", video, "-frames:v", "1", "-vf", "scale=640:-2", "-q:v", "4", target)
        made[stem + ".jpg"] = ("auto", sha(target)); print("poster", stem + ".jpg")

def main():
    os.makedirs(FILMS, exist_ok=True); os.makedirs(POSTERS, exist_ok=True)
    delim, rows = read_table(); load_ledger()
    renamed = {}
    for name in sorted(os.listdir(FILMS)):
        path = os.path.join(FILMS, name); stem, ext = os.path.splitext(name)
        if ext.lower() not in VIDEO:
            continue
        codec, dur, h = probe(path)
        heavy = os.path.getsize(path) > MAX_MB * 1024 * 1024 or dur > MAX_S + 0.5 or h > MAX_H
        target = os.path.join(FILMS, stem + ".mp4"); tmp = target + ".tmp.mp4"
        if ext.lower() != ".mp4" or codec != "h264" or heavy:
            run("-i", path, "-t", str(MAX_S), "-vf", "scale='min(1280,iw)':-2", "-c:v", "libx264", "-crf", "24",
                "-preset", "slow", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", tmp)
        elif has_audio(path):
            run("-i", path, "-c:v", "copy", "-an", "-movflags", "+faststart", tmp)
        if os.path.exists(tmp):
            os.remove(path); os.replace(tmp, target)
            if name != stem + ".mp4": renamed[nfc(name)] = stem + ".mp4"
            print("fixed", name, "->", stem + ".mp4", f"({os.path.getsize(target) / 1e6:.1f} MB)"); name = stem + ".mp4"; path = target
        make_poster(stem, path)
    for r in rows:                                    # keep the table pointing at converted files
        v = nfc(r.get("video", ""))
        if v in renamed: r["video"] = renamed[v]
    listed = {nfc(r.get("video", "")) for r in rows}
    for name in sorted(os.listdir(FILMS)):
        stem, ext = os.path.splitext(name)
        if ext.lower() in VIDEO + PHOTO and nfc(name) not in listed:
            rows.append({"video": name, "title": stem, "author": "", "duration": ""}); print("added to films.csv:", name)
    have = {nfc(os.path.splitext(n)[0]) for n in os.listdir(FILMS)}
    for p, (kind, _) in list(made.items()):
        if kind == "auto" and nfc(os.path.splitext(p)[0]) not in have:
            if os.path.exists(os.path.join(POSTERS, p)): os.remove(os.path.join(POSTERS, p))
            del made[p]; print("removed poster", p)
    save_ledger()
    extra = [k for r in rows for k in r if k not in COLS]
    cols = COLS + sorted(set(extra), key=extra.index)
    with open(TABLE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=delim, lineterminator="\n")
        w.writeheader(); [w.writerow({k: r.get(k, "") for k in cols}) for r in rows]

if __name__ == "__main__":
    main()
