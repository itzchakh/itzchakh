#!/usr/bin/env python3
"""After a script revision: reuse recorded lines whose text is unchanged, and write AI Studio
sessions only for the new/changed lines.

  python retake.py --old script_v1.txt --old-audio audio_lines/ --out-audio audio_lines_v2/ --sessions-out tts_sessions_v2/
Record the session texts in AI Studio, save as downloads_v2/09.wav, 10.wav ... then:
  python split_sessions.py --in downloads_v2/ --out audio_lines_v2/ --sessions tts_sessions_v2/sessions.json
"""
import argparse, json, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gemini import parse_script
ap = argparse.ArgumentParser()
ap.add_argument("--old", required=True); ap.add_argument("--old-audio", required=True)
ap.add_argument("--out-audio", required=True); ap.add_argument("--sessions-out", required=True)
ap.add_argument("--first-session", type=int, default=9)
a = ap.parse_args()
cfg = json.load(open(os.path.join(HERE, "voices.json"), encoding="utf-8"))
def pron(t):
    for k, r in sorted(cfg["pron"].items(), key=lambda kv: -len(kv[0])): t = t.replace(k, r)
    return t
old = {(s, t): i for i, (s, t) in enumerate(parse_script(a.old), 1)}
new = parse_script(os.path.join(HERE, "script.txt"))
os.makedirs(a.out_audio, exist_ok=True); os.makedirs(a.sessions_out, exist_ok=True)
todo = {}
for i, (s, t) in enumerate(new, 1):
    if (s, t) in old:
        shutil.copy(os.path.join(a.old_audio, f"line_{old[(s, t)]:02d}.wav"), os.path.join(a.out_audio, f"line_{i:02d}.wav"))
    else:
        todo.setdefault(s, []).append((i, t))
sessions, n = [], a.first_session
for spk, items in todo.items():
    v = cfg["voices"][spk]; name = f"{n:02d}_{spk.replace(' ', '_')}_תיקון"
    body = f"{v['style']} Pause for a full two seconds between paragraphs.\n\n" + "\n\n".join(pron(t) for _, t in items) + "\n"
    open(os.path.join(a.sessions_out, name + ".txt"), "w", encoding="utf-8").write(body)
    sessions.append({"n": n, "file": name, "speaker": spk, "voice": v["voice"], "lines": [i for i, _ in items]})
    print(name, v["voice"], len(items), "lines"); n += 1
json.dump(sessions, open(os.path.join(a.sessions_out, "sessions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("reused", len(new) - sum(len(x) for x in todo.values()), "of", len(new))
