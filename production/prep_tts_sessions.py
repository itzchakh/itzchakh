#!/usr/bin/env python3
"""Write one paste-ready text per AI Studio speech session (one voice per session; long narrator split in parts)."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gemini import parse_script
HERE = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(HERE, "voices.json"), encoding="utf-8"))
lines = parse_script(os.path.join(HERE, "script.txt"))
out = os.path.join(HERE, "tts_sessions"); os.makedirs(out, exist_ok=True)
for f in os.listdir(out): os.remove(os.path.join(out, f))
def pron(t):
    for k, r in sorted(cfg["pron"].items(), key=lambda kv: -len(kv[0])): t = t.replace(k, r)
    return t
by = {}
for i, (spk, text) in enumerate(lines, 1): by.setdefault(spk, []).append((i, text))
order = ["קריינות", "המלך", "הנסיך", "הרופא הראשי", "היועץ"]
sessions, n = [], 0
for spk in order:
    items = by[spk]
    k = -(-len(items) // 14)
    size = -(-len(items) // k)
    chunks = [items[i:i+size] for i in range(0, len(items), size)]
    if spk == "הנסיך":  # joyful line and whisper line need different deliveries
        chunks = [[it] for it in items]
    for ci, ch in enumerate(chunks, 1):
        n += 1
        part = f"_חלק{ci}" if len(chunks) > 1 else ""
        name = f"{n:02d}_{spk.replace(' ', '_')}{part}"
        v = dict(cfg["voices"][spk])
        if spk == "הנסיך":
            v["style"] = ("Read this in Hebrew as a 12-year-old boy, bright, excited and joyful, calling out to his father."
                          if ci == 1 else "Read this in Hebrew as a 12-year-old boy waking from a long illness, weak, slow, in a soft whisper full of wonder.")
        body = (f"{v['style']} Pause for a full two seconds between paragraphs.\n\n" +
                "\n\n".join(pron(t) for _, t in ch) + "\n")
        open(os.path.join(out, name + ".txt"), "w", encoding="utf-8").write(body)
        sessions.append({"file": name, "speaker": spk, "voice": v["voice"], "lines": [i for i, _ in ch]})
json.dump(sessions, open(os.path.join(out, "sessions.json"), "w"), ensure_ascii=False, indent=1)
for s in sessions: print(s["file"], s["voice"], len(s["lines"]), "lines")
