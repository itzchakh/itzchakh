#!/usr/bin/env python3
"""Build a lip-sync shot pack from timeline.csv (output of narration-to-timeline).

For every dialogue line it writes:
  audio/<shot>_<speaker>.wav    the line cut from the master narration (with short handles)
  lipsync_pack.md               per shot: image prompt, animation prompt, checklist
  lipsync_pack.csv              the same, one row per shot (for spreadsheets / batch tools)

characters.json maps the Hebrew speaker name used in the script to its look and rules:
{
  "style":  "[STYLE] ...",                 # optional fixed prompt prefix
  "rules":  "[RULES] ...",                 # optional fixed prompt suffix
  "scenes": {"<act name>": ["המלך", "הרופא הראשי"]},   # optional: who is on screen per act
  "characters": {
    "המלך": {"en": "the king", "side": "right", "voice": "Orus",
             "look": "about 50, full rounded brown-gray beard ...",
             "ref": "REF_king_APPROVED.png"}
  }
}
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys

NARRATOR = "קריינות"


def slug(s):
    return re.sub(r"[^\w֐-׿]+", "_", s).strip("_")


def load_timeline(path):
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["start"], r["end"] = float(r["start"]), float(r["end"])
    return rows


def load_shots(path):
    if not path or not os.path.exists(path):
        return {}
    m = {}
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            for lid in r["lines"].split():
                m.setdefault(lid, r["shot_id"])
    return m


def listeners_for(rows, i, window=2):
    """Other speakers in neighbouring dialogue lines of the same act = who is in the scene listening."""
    me, act = rows[i]["speaker"], rows[i]["act"]
    found = []
    for j in range(max(0, i - window), min(len(rows), i + window + 1)):
        r = rows[j]
        if j != i and r["act"] == act and r["speaker"] not in (NARRATOR, me) and r["speaker"] not in found:
            found.append(r["speaker"])
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--timeline", required=True)
    ap.add_argument("--audio", required=True, help="narration_master.wav the timeline was made from")
    ap.add_argument("--characters", required=True)
    ap.add_argument("--shots", help="shots.csv, to reuse its shot ids")
    ap.add_argument("--out", required=True)
    ap.add_argument("--handle", type=float, default=0.15, help="seconds of room tone kept before/after each line")
    ap.add_argument("--max-len", type=float, default=8.0, help="warn when a line is longer than this")
    ap.add_argument("--engine", default="Kling / Hedra / Veo", help="name printed in the pack")
    a = ap.parse_args()

    cfg = json.load(open(a.characters, encoding="utf-8"))
    chars = cfg.get("characters", cfg)
    style, rules = cfg.get("style", ""), cfg.get("rules", "")
    rows = load_timeline(a.timeline)
    shot_of = load_shots(a.shots)
    os.makedirs(os.path.join(a.out, "audio"), exist_ok=True)

    missing = sorted({r["speaker"] for r in rows if r["speaker"] != NARRATOR and r["speaker"] not in chars})
    if missing:
        sys.exit("characters.json has no entry for: " + ", ".join(missing))

    md = [f"# חבילת ליפסינק\n\nמנוע: {a.engine}. לכל שוט מצרפים את דף הרפרנס המאושר של הדמות ואת קובץ האודיו.\n"]
    table = []
    warnings = []
    sides_seen = {}
    n = 0
    for i, r in enumerate(rows):
        if r["speaker"] == NARRATOR:
            continue
        n += 1
        c = chars[r["speaker"]]
        sid = shot_of.get(r["line_id"], f"D{n:02d}")
        dur = r["end"] - r["start"]
        s0 = max(0.0, r["start"] - a.handle)
        clip = os.path.join(a.out, "audio", f"{sid}_{slug(r['speaker'])}.wav")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{s0:.3f}", "-to", f"{r['end'] + a.handle:.3f}",
                        "-i", a.audio, "-ac", "1", "-ar", "48000", clip], check=True)

        lis = listeners_for(rows, i)
        for extra in cfg.get("scenes", {}).get(r["act"], []):  # explicit cast per act
            if extra not in (r["speaker"], NARRATOR) and extra not in lis:
                lis.append(extra)
        side = c.get("side", "center")
        other_side = {"right": "left", "left": "right"}.get(side, "background")
        lis_desc = "; ".join(f"{chars[l].get('en', l)} on the {chars[l].get('side', other_side)} side, "
                             f"listening with mouth firmly closed" for l in lis if l in chars)
        look = c.get("look", "")
        framing = (f"Medium close-up of {c.get('en', r['speaker'])} ({look}) on the {side} side of the frame, "
                   f"face turned no more than 30 degrees from camera, mouth and lips fully visible, "
                   + ("short moustache trimmed above the upper lip, " if re.search(r"beard|moustache|mustache", c.get("look", ""), re.I) else "")
                   + f"no hands, props or hair covering the mouth, "
                   f"mouth slightly open as if about to speak.")
        img = " ".join(x for x in [style, framing, (lis_desc + ".") if lis_desc else "", rules] if x)
        anim = (f"{c.get('en', r['speaker'])} speaks this line with natural, clear lip movement synced to the attached audio, "
                f"subtle head and eyebrow motion, blinking. "
                + (f"{lis_desc}, only small nods and blinks, no lip movement. " if lis_desc else "")
                + f"Camera: very slow push-in, no cuts. Duration {dur + 2*a.handle:.1f}s. Keep character design identical to the reference.")

        # checks
        if dur > a.max_len:
            warnings.append(f"{sid}: line is {dur:.1f}s (> {a.max_len}s); split it into two shots or a reverse angle.")
        if side not in ("left", "right"):
            warnings.append(f"{sid}: no fixed screen side for {r['speaker']}.")
        if side in ("left", "right"):
            prev = sides_seen.setdefault(r["speaker"], side)
            if prev != side:
                warnings.append(f"{sid}: {r['speaker']} changed screen side.")
        for l in lis:
            if l in chars and chars[l].get("side") == side:
                warnings.append(f"{sid}: {r['speaker']} and {l} are both on the {side} side; fine if both address someone on the other side, but if they talk to each other the eyeline breaks.")

        md.append(f"## {sid} · {r['speaker']} · {r['start']:.2f}–{r['end']:.2f} ({dur:.1f}s) · קול: {c.get('voice', '')}\n")
        md.append(f"**שורה:** {r['text']}\n")
        md.append(f"**אודיו:** `audio/{os.path.basename(clip)}`   **רפרנס:** `{c.get('ref', '')}`   "
                  f"**צד:** {side}   **מקשיבים:** {', '.join(lis) or '—'}\n")
        md.append(f"**פרומפט תמונה:**\n```\n{img}\n```\n")
        md.append(f"**פרומפט הנפשה:**\n```\n{anim}\n```\n")
        md.append("**צ'קליסט:** ☐ הפה גלוי בכל השוט ☐ המקשיב שותק ☐ אותו צד כמו בשוטים הקודמים ☐ פנים זהות לרפרנס ☐ בלי טקסט בתמונה\n")
        table.append([sid, r["line_id"], r["act"], r["speaker"], f"{r['start']:.2f}", f"{r['end']:.2f}", f"{dur:.2f}",
                      side, " ".join(lis), c.get("voice", ""), os.path.relpath(clip, a.out), r["text"], img, anim])

    if warnings:
        md.insert(1, "## אזהרות\n" + "\n".join(f"- {w}" for w in warnings) + "\n")
    with open(os.path.join(a.out, "lipsync_pack.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    with open(os.path.join(a.out, "lipsync_pack.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["shot_id", "line_id", "act", "speaker", "start", "end", "dur", "side", "listeners", "voice",
                    "audio", "text", "image_prompt", "animation_prompt"])
        w.writerows(table)
    total = sum(float(t[6]) for t in table)
    print(f"{len(table)} lip-sync shots, {total:.1f}s of dialogue -> {a.out}")
    for w_ in warnings:
        print("WARN", w_)


if __name__ == "__main__":
    main()
