# -*- coding: utf-8 -*-
"""Extended review form (HTML) for "Diamond in the Crown": one card per storyboard shot with all data,
first/last frame thumbnails, a play button on the rough cut, and 3 reject segments (storyboard / narration / images).
Usage: python build_review_form.py 1   -> review/טופס_תיקונים_היהלום_שבכתר_v1.html"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import storyboard_data as SBD  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
V = sys.argv[1] if len(sys.argv) > 1 else "1"
VIDEO = sys.argv[2] if len(sys.argv) > 2 else "rough_v1.mp4"


def rd(p):
    return list(csv.DictReader(open(os.path.join(HERE, p), encoding="utf-8-sig")))


lines = rd("timeline/timeline.csv")
shots = {r["shot_id"]: r for r in rd("timeline/shots.csv")}
frames = {r["shot"]: r for r in rd("frames/frames_index.csv")}
prom = json.load(open(os.path.join(HERE, "storyboard_prompts.json"), encoding="utf-8"))
voices = json.load(open(os.path.join(HERE, "voices.json"), encoding="utf-8"))["voices"]
sb = {t[0]: t for t in SBD.SB}

# my own notes, pre-filled (status stays "ok" so Yitzchak decides)
NOTES = {
    ("S014", "img"): "הערה שלי: הפריים הקיים (הנוף האפור) הפך לפריים הסיום, ונוסף פריים פתיחה צבעוני.",
    ("S016b", "img"): "הערה שלי: הרופא יצא בלי המשקפיים העגולים.",
    ("S018b", "img"): "הערה שלי: הקווים על המגילה נראים קצת כמו כתב. אפשר לטשטש בעריכה או לייצר מחדש.",
    ("S029", "img"): "הערה שלי: בפריים הפתיחה המדרגות נראות עולות ולא יורדות. פריים הסיום נכון.",
    ("S034", "img"): "הערה שלי: אדמו\"ר הזקן מביט ימינה, והסטוריבורד הגדיר שמאלה.",
    ("S040", "img"): "הערה שלי: לפי התנ\"ך זה גבר בלי כיפה. יצא לא ברור אם יש לו כיפה כהה או שזה שיער.",
    ("S041b", "sb"): "הערה שלי: פיצלתי לשלושה שוטים, ובכל אחד אדם לבד.",
    ("S002", "img"): "הערה שלי: המלך בלי הכתר חובש כובע קטיפה כחול עם רצועת זהב. כך בכל השוטים שהכתר לא על ראשו.",
}

DATA = []
for sid, v in prom.items():
    t = sb[sid]
    base = sid[:4]
    sh = shots.get(base, {})
    st, en = v["start"], v["end"]
    mine = [l for l in lines if st - 0.05 <= (float(l["start"]) + float(l["end"])) / 2 <= en + 0.05]
    nar = [{"id": l["line_id"], "spk": l["speaker"], "voice": voices.get(l["speaker"], {}).get("voice", ""),
            "t": f'{float(l["start"]):.2f}–{float(l["end"]):.2f}', "text": l["text"]} for l in mine]
    if sid == "S041b":
        imgs = [["S041b1_v1.png", "S041b2_v1.png", "S041b3_v1.png"], []]
    else:
        fr = frames[sid]
        imgs = [[fr["first_frame"]], [fr["last_frame"]] if fr["last_frame"] else []]
    DATA.append({
        "id": sid, "act": sh.get("act", ""), "type": sh.get("type", ""), "start": st, "end": en,
        "lip": sh.get("type") == "dialogue", "speakers": sorted({n["spk"] for n in nar}),
        "nar": nar, "scene": t[2], "first": t[3], "motion": t[4], "light": t[5], "prompt": t[6],
        "refs": t[7], "first_img": imgs[0], "last_img": imgs[1],
        "notes": {k: NOTES.get((sid, k), "") for k in ("sb", "nar", "img")},
    })

# embed small thumbnails so the form works even when opened outside the project folder
import base64, io
from PIL import Image
THUMBS = {}
for d in DATA:
    for f in d["first_img"] + d["last_img"]:
        if f in THUMBS:
            continue
        im = Image.open(os.path.join(HERE, "frames", f)).convert("RGB")
        im.thumbnail((720, 405))
        b = io.BytesIO(); im.save(b, "JPEG", quality=78)
        THUMBS[f] = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
total = DATA[-1]["end"]
html = open(os.path.join(HERE, "review_form_template.html"), encoding="utf-8").read()
html = (html.replace("__THUMBS__", json.dumps(THUMBS))
            .replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
            .replace("__VIDEO__", VIDEO).replace("__V__", V)
            .replace("__TOTAL__", f"{int(total // 60)}:{total % 60:05.2f}")
            .replace("__N__", str(len(DATA))))
os.makedirs(os.path.join(HERE, "review"), exist_ok=True)
out = os.path.join(HERE, "review", f"טופס_תיקונים_היהלום_שבכתר_v{V}.html")
open(out, "w", encoding="utf-8").write(html)
print(out, len(DATA), "shots")
