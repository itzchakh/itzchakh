#!/usr/bin/env python3
"""Turn a narration script + TTS audio into timeline.csv, shots.csv and subtitles.srt.

Two modes:
  --clips DIR   one audio file per script line (natural sort order). Exact timing; the
                clips are concatenated into narration_master.wav with pauses between them.
  --audio FILE  one long recording. Speech segments are found with ffmpeg silencedetect and
                matched to the script lines by length (dynamic programming).

Script format (UTF-8 text, one spoken line per row):
  # <act name>            starts a new act (e.g. "# א. הממלכה המנגנת")
  <speaker>: <text>       dialogue line (speaker is any name except the narrator names)
  <text>                  narrator line (or "קריינות: <text>" / "קריין: <text>")
  blank lines and lines starting with // are ignored.
"""
import argparse
import csv
import math
import os
import re
import subprocess
import sys

NARRATOR_NAMES = {"קריינות", "קריין", "מספר", "narrator", "narration"}
AUDIO_EXT = (".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def duration(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(r.stdout.strip())


def parse_script(path):
    lines, act = [], ""
    with open(path, encoding="utf-8") as f:
        for raw in f:
            s = raw.strip().lstrip("﻿")
            if not s or s.startswith("//"):
                continue
            if s.startswith("#"):
                act = s.lstrip("#").strip()
                continue
            speaker, text = "קריינות", s
            m = re.match(r"^\**([^:\"״,،]{1,30}?)\**\s*:\s*(.+)$", s)
            if m and len(m.group(1).split()) > 3:
                m = None
            if m:
                speaker, text = m.group(1).strip(), m.group(2).strip()
                if speaker.lower() in NARRATOR_NAMES:
                    speaker = "קריינות"
            text = text.strip().strip('"').strip("״").strip()
            lines.append({"act": act, "speaker": speaker, "text": text})
    if not lines:
        sys.exit("script has no spoken lines")
    return lines


def natural_key(name):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def from_clips(lines, clips_dir, out_dir, gap, act_gap, lead):
    files = sorted([f for f in os.listdir(clips_dir) if f.lower().endswith(AUDIO_EXT)], key=natural_key)
    if len(files) != len(lines):
        sys.exit(f"{len(files)} audio clips but {len(lines)} script lines; they must match one to one")
    t = lead
    concat_list = os.path.join(out_dir, "_concat.txt")
    sr = 48000
    parts = []
    silence_cache = {}

    def silence(sec):
        key = round(sec, 3)
        if key not in silence_cache:
            p = os.path.join(out_dir, f"_sil_{int(key*1000)}.wav")
            run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"anullsrc=r={sr}:cl=mono", "-t", str(key), p])
            silence_cache[key] = p
        return silence_cache[key]

    if lead > 0:
        parts.append(silence(lead))
    for i, (ln, fn) in enumerate(zip(lines, files)):
        src = os.path.join(clips_dir, fn)
        norm = os.path.join(out_dir, f"_clip_{i:03d}.wav")
        run(["ffmpeg", "-y", "-v", "error", "-i", src, "-ac", "1", "-ar", str(sr), norm])
        d = duration(norm)
        ln.update(start=t, end=t + d, source=fn)
        parts.append(norm)
        t += d
        if i < len(lines) - 1:
            g = act_gap if lines[i + 1]["act"] != ln["act"] else gap
            parts.append(silence(g))
            t += g
    with open(concat_list, "w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{os.path.abspath(p)}'\n")
    master = os.path.join(out_dir, "narration_master.wav")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", master])
    for p in parts + [concat_list]:
        if os.path.basename(p).startswith("_") and os.path.exists(p):
            os.remove(p)
    return master


def speech_segments(audio, noise_db, min_sil):
    r = run(["ffmpeg", "-hide_banner", "-i", audio, "-af", f"silencedetect=n={noise_db}dB:d={min_sil}", "-f", "null", "-"])
    total = duration(audio)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    segs, cur = [], 0.0
    for i, s in enumerate(starts):
        if s - cur > 0.08:
            segs.append([cur, s])
        cur = ends[i] if i < len(ends) else total
    if total - cur > 0.08:
        segs.append([cur, total])
    return segs, total


def align(lines, segs):
    """Partition the segment list into len(lines) contiguous groups, matching text length."""
    n, m = len(lines), len(segs)
    chars = [max(len(re.sub(r"\s", "", l["text"])), 1) for l in lines]
    speech = sum(e - s for s, e in segs)
    rate = speech / sum(chars)
    exp = [c * rate for c in chars]
    INF = float("inf")
    cost = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[0] * (m + 1) for _ in range(n + 1)]
    cost[0][0] = 0.0
    for i in range(1, n + 1):
        for j in range(i, m - (n - i) + 1):
            best, arg = INF, 0
            for k in range(i - 1, j):
                if cost[i - 1][k] == INF:
                    continue
                span = segs[j - 1][1] - segs[k][0]
                c = cost[i - 1][k] + ((span - exp[i - 1]) / max(exp[i - 1], 0.5)) ** 2
                if c < best:
                    best, arg = c, k
            cost[i][j], back[i][j] = best, arg
    j = m
    for i in range(n, 0, -1):
        k = back[i][j]
        lines[i - 1].update(start=segs[k][0], end=segs[j - 1][1])
        j = k


def from_audio(lines, audio, noise_db, min_sil):
    for d in (min_sil, 0.18, 0.12):
        segs, total = speech_segments(audio, noise_db, d)
        if len(segs) >= len(lines):
            align(lines, segs)
            return False
    # not enough pauses: proportional split of the whole file (rough)
    chars = [max(len(l["text"]), 1) for l in lines]
    t, scale = 0.0, total / sum(chars)
    for l, c in zip(lines, chars):
        l.update(start=t, end=t + c * scale)
        t += c * scale
    return True


def make_shots(lines, min_len, max_len):
    shots, cur = [], None

    def close():
        if cur:
            shots.append(cur)

    for i, l in enumerate(lines):
        is_dlg = l["speaker"] != "קריינות"
        d = l["end"] - l["start"]
        if is_dlg:
            close()
            cur = None
            shots.append({"act": l["act"], "type": "lipsync", "speaker": l["speaker"], "start": l["start"],
                          "end": l["end"], "lines": [l["id"]]})
            continue
        if d > max_len:  # long narrator line: split evenly
            close()
            cur = None
            k = math.ceil(d / ((min_len + max_len) / 2))
            for p in range(k):
                shots.append({"act": l["act"], "type": "narration", "speaker": "קריינות",
                              "start": l["start"] + d * p / k, "end": l["start"] + d * (p + 1) / k, "lines": [l["id"]]})
            continue
        if cur and (cur["act"] != l["act"] or (l["end"] - cur["start"] > max_len and cur["end"] - cur["start"] >= min_len)):
            close()
            cur = None
        if cur is None:
            cur = {"act": l["act"], "type": "narration", "speaker": "קריינות", "start": l["start"], "end": l["end"], "lines": [l["id"]]}
        else:
            cur["end"] = l["end"]
            cur["lines"].append(l["id"])
    close()
    # stretch shot boundaries so shots cover the gaps (cut lands mid-pause)
    for a, b in zip(shots, shots[1:]):
        mid = (a["end"] + b["start"]) / 2 if b["start"] > a["end"] else a["end"]
        a["end"], b["start"] = mid, mid
    if shots:
        shots[0]["start"] = 0.0
    for i, s in enumerate(shots, 1):
        s["id"] = f"S{i:03d}"
    return shots


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(lines, path, max_chars=42):
    with open(path, "w", encoding="utf-8") as f:
        n = 0
        for l in lines:
            words, chunks, cur = l["text"].split(), [], ""
            for w in words:
                if cur and len(cur) + 1 + len(w) > max_chars * 2:
                    chunks.append(cur)
                    cur = w
                else:
                    cur = f"{cur} {w}".strip()
            if cur:
                chunks.append(cur)
            d = (l["end"] - l["start"]) / len(chunks)
            for k, c in enumerate(chunks):
                n += 1
                ws = c.split()
                if len(c) > max_chars and len(ws) > 1:  # two balanced rows
                    best = min(range(1, len(ws)), key=lambda x: abs(len(" ".join(ws[:x])) - len(" ".join(ws[x:]))))
                    c = " ".join(ws[:best]) + "\n" + " ".join(ws[best:])
                f.write(f"{n}\n{srt_time(l['start'] + k*d)} --> {srt_time(l['start'] + (k+1)*d)}\n{c}\n\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--script", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--clips", help="folder with one audio file per script line")
    g.add_argument("--audio", help="one long narration file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--gap", type=float, default=0.35, help="pause between lines in --clips mode (s)")
    ap.add_argument("--act-gap", type=float, default=1.5, help="pause between acts in --clips mode (s)")
    ap.add_argument("--lead", type=float, default=0.0, help="silence before the first line in --clips mode (s)")
    ap.add_argument("--noise-db", type=float, default=-35)
    ap.add_argument("--min-silence", type=float, default=0.25)
    ap.add_argument("--shot-min", type=float, default=6)
    ap.add_argument("--shot-max", type=float, default=10)
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    lines = parse_script(a.script)
    for i, l in enumerate(lines, 1):
        l["id"] = f"L{i:03d}"
    rough = False
    if a.clips:
        audio = from_clips(lines, a.clips, a.out, a.gap, a.act_gap, a.lead)
    else:
        audio = os.path.abspath(a.audio)
        rough = from_audio(lines, a.audio, a.noise_db, a.min_silence)
    total = duration(audio)
    shots = make_shots(lines, a.shot_min, a.shot_max)
    if shots:
        shots[-1]["end"] = max(shots[-1]["end"], total)

    with open(os.path.join(a.out, "timeline.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["line_id", "act", "speaker", "start", "end", "dur", "text"])
        for l in lines:
            w.writerow([l["id"], l["act"], l["speaker"], f"{l['start']:.2f}", f"{l['end']:.2f}", f"{l['end']-l['start']:.2f}", l["text"]])
    with open(os.path.join(a.out, "shots.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["shot_id", "act", "type", "speaker", "start", "end", "dur", "lines"])
        for s in shots:
            w.writerow([s["id"], s["act"], s["type"], s["speaker"], f"{s['start']:.2f}", f"{s['end']:.2f}", f"{s['end']-s['start']:.2f}", " ".join(s["lines"])])
    write_srt(lines, os.path.join(a.out, "subtitles.srt"))

    dlg = sum(l["end"] - l["start"] for l in lines if l["speaker"] != "קריינות")
    acts = {}
    for l in lines:
        acts.setdefault(l["act"], [l["start"], l["end"]])[1] = l["end"]
    print(f"audio: {audio}")
    print(f"total {total:.1f}s | lines {len(lines)} | shots {len(shots)} | dialogue {dlg:.1f}s = {100*dlg/total:.0f}%")
    for name, (s, e) in acts.items():
        print(f"  act '{name}': {s:.1f}-{e:.1f} ({e-s:.1f}s)")
    if rough:
        print("WARNING: not enough pauses in the audio; timing is a rough proportional split. Prefer --clips.")


if __name__ == "__main__":
    main()
