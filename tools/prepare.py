"""Runs on GitHub after every upload (see .github/workflows/films.yml), or locally: python3 tools/prepare.py

- every video in films/ that would load badly is fixed: not an H.264 MP4 (e.g. an iPhone .mov), larger than
  5 MB, bigger than 1920x1080 or longer than 15 s is re-encoded (max 1280 px wide, 15 s, no sound);
  a good MP4 that only carries a sound track just has the sound removed
- every video gets a poster in posters/<same name>.jpg (the first thing the page loads)
- every video or photo in films/ that is missing from films.csv gets a row (title = file name)
- posters whose video is gone are removed
Needs ffmpeg and ffprobe.
"""
import csv, io, json, os, subprocess, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILMS, POSTERS, TABLE = (os.path.join(ROOT, x) for x in ("films", "posters", "films.csv"))
VIDEO = (".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi")
PHOTO = (".jpg", ".jpeg", ".png", ".webp", ".gif")
COLS = ["video", "title", "author", "duration"]
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

def main():
    os.makedirs(FILMS, exist_ok=True); os.makedirs(POSTERS, exist_ok=True)
    delim, rows = read_table()
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
        poster = os.path.join(POSTERS, stem + ".jpg")
        if not os.path.exists(poster) or os.path.getmtime(poster) < os.path.getmtime(path):
            _, dur, _ = probe(path)
            run("-ss", str(min(1.0, dur / 3 if dur else 0)), "-i", path, "-frames:v", "1",
                "-vf", "scale=640:-2", "-q:v", "4", poster)
            print("poster", stem + ".jpg")
    for r in rows:                                    # keep the table pointing at converted files
        v = nfc(r.get("video", ""))
        if v in renamed: r["video"] = renamed[v]
    listed = {nfc(r.get("video", "")) for r in rows}
    for name in sorted(os.listdir(FILMS)):
        stem, ext = os.path.splitext(name)
        if ext.lower() in VIDEO + PHOTO and nfc(name) not in listed:
            rows.append({"video": name, "title": stem, "author": "", "duration": ""}); print("added to films.csv:", name)
    have = {nfc(os.path.splitext(n)[0]) for n in os.listdir(FILMS)}
    for p in os.listdir(POSTERS):
        if p.endswith(".jpg") and nfc(p[:-4]) not in have:
            os.remove(os.path.join(POSTERS, p)); print("removed poster", p)
    extra = [k for r in rows for k in r if k not in COLS]
    cols = COLS + sorted(set(extra), key=extra.index)
    with open(TABLE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=delim, lineterminator="\n")
        w.writeheader(); [w.writerow({k: r.get(k, "") for k in cols}) for r in rows]

if __name__ == "__main__":
    main()
