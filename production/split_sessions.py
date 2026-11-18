#!/usr/bin/env python3
"""Cut the audio downloaded from each AI Studio session into one file per script line.

  python3 split_sessions.py --in downloads/ --out audio_lines/
Files in --in must start with the session number (01_..., 02_... or just 01.wav); any audio format.
Then:  make_timeline.py --script script.txt --clips audio_lines/ --out timeline/
"""
import argparse, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "narration-to-timeline", "scripts"))
sys.path.insert(0, HERE)
from make_timeline import speech_segments, align  # noqa: E402
from gemini import parse_script  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--noise-db", type=float, default=-38)
ap.add_argument("--sessions", default=os.path.join(HERE, "tts_sessions", "sessions.json"))
ap.add_argument("--script", default=os.path.join(HERE, "script.txt"))
a = ap.parse_args()
sessions = json.load(open(a.sessions, encoding="utf-8"))
lines = parse_script(a.script)
os.makedirs(a.out, exist_ok=True)
files = {}
for f in os.listdir(a.inp):
    m = re.match(r"^(\d{1,2})\D", f + ".")
    if m and f.lower().endswith((".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".webm")):
        files[int(m.group(1))] = os.path.join(a.inp, f)
ok = True
for n, s in ((s.get("n", k), s) for k, s in enumerate(sessions, 1)):
    if n not in files:
        print(f"MISSING session {n:02d} ({s['file']})"); ok = False; continue
    want = [{"text": lines[i - 1][1]} for i in s["lines"]]
    segs = []
    for d in (0.6, 0.45, 0.3, 0.2):  # prefer the long paragraph pauses
        segs, _ = speech_segments(files[n], a.noise_db, d)
        if len(segs) >= len(want):
            break
    if len(segs) < len(want):
        print(f"PROBLEM session {n:02d}: found {len(segs)} pauses-separated parts for {len(want)} lines"); ok = False; continue
    if len(want) == 1:
        want[0].update(start=segs[0][0], end=segs[-1][1])
    else:
        align(want, segs)
    for li, w in zip(s["lines"], want):
        out = os.path.join(a.out, f"line_{li:02d}.wav")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(0, w['start'] - 0.05):.3f}", "-to", f"{w['end'] + 0.1:.3f}",
                        "-i", files[n], "-ac", "1", "-ar", "48000", out], check=True)
    print(f"session {n:02d} {s['file']}: {len(want)} lines cut")
print("ALL GOOD" if ok else "fix the problems above")
