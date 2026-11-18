#!/usr/bin/env python3
"""Assemble a rough cut from shots.csv + a media folder + narration (+ music, + subtitles).

Media matching: a file in --media whose name starts with the shot id (S012.png, S012_v2.mp4 ...).
If several match, the newest file wins (so dropping a new version in the folder replaces the old one).
  image  -> slow Ken Burns move (alternating push-in / pull-out)
  video  -> trimmed to the shot length; if shorter, the last frame is held
  none   -> a dark placeholder card with the shot id, so timing stays exact

Usage:
  assemble.py --shots shots.csv --media shots/ --audio narration_master.wav --out rough.mp4
              [--music score.mp3 --music-db -14 --duck] [--srt subtitles.srt] [--size 1920x1080] [--fps 30]
              [--only S010-S020] [--report]
"""
import argparse
import csv
import glob
import os
import shutil
import subprocess
import sys
import tempfile

IMG = (".png", ".jpg", ".jpeg", ".webp")
VID = (".mp4", ".mov", ".webm", ".mkv")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(" ".join(cmd) + "\n" + r.stderr[-2000:])
        sys.exit(f"ffmpeg failed ({r.returncode})")
    return r


def probe_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def find_media(media_dir, sid):
    c = [p for p in glob.glob(os.path.join(media_dir, f"{sid}*")) if p.lower().endswith(IMG + VID)]
    # S01 must not match S010: the char after the id must be non-digit
    c = [p for p in c if not os.path.basename(p)[len(sid):len(sid) + 1].isdigit()]
    return max(c, key=os.path.getmtime) if c else None


def in_range(sid, rng):
    if not rng:
        return True
    a, _, b = rng.partition("-")
    b = b or a
    return a <= sid <= b


def render_shot(i, s, media, W, H, fps, out):
    d = s["dur"]
    frames = max(1, round(d * fps))
    scale_fit = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1")
    if media and media.lower().endswith(IMG):
        z_in = i % 2 == 0
        z = f"'min(1+0.08*on/{frames},1.08)'" if z_in else f"'max(1.08-0.08*on/{frames},1.0)'"
        vf = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
              f"zoompan=z={z}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={fps},setsar=1")
        cmd = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", media, "-vf", vf, "-frames:v", str(frames)]
    elif media:
        vd = probe_dur(media)
        pad = max(0.0, d - vd) + 0.1
        vf = f"{scale_fit},fps={fps},tpad=stop_mode=clone:stop_duration={pad:.3f}"
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", media, "-an", "-vf", vf, "-frames:v", str(frames)]
    else:
        label = f"{s['id']}  |  {s['type']}  |  {d:.1f}s  |  MISSING"
        vf = (f"drawtext=fontfile={FONT}:text='{label}':fontcolor=0xC9A227:fontsize={H//22}:"
              f"x=(w-text_w)/2:y=(h-text_h)/2")
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x101826:s={W}x{H}:r={fps}",
               "-vf", vf, "-frames:v", str(frames)]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(fps), out]
    sh(cmd)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shots", required=True)
    ap.add_argument("--media", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--music")
    ap.add_argument("--music-db", type=float, default=-14, help="music level under the voice")
    ap.add_argument("--duck", action="store_true", help="duck the music further while the voice speaks")
    ap.add_argument("--srt", help="burn these subtitles in (libass, RTL handled by fribidi)")
    ap.add_argument("--font", default="Heebo", help="subtitle font family (must be installed)")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--only", help="render a range of shots, e.g. S010-S020 (audio is cut to match)")
    ap.add_argument("--report", action="store_true", help="only list which shots have media")
    a = ap.parse_args()
    W, H = map(int, a.size.lower().split("x"))

    with open(a.shots, encoding="utf-8-sig") as f:
        shots = [r for r in csv.DictReader(f)]
    for s in shots:
        s["id"], s["start"], s["end"] = s["shot_id"], float(s["start"]), float(s["end"])
        s["dur"] = s["end"] - s["start"]
    shots = [s for s in shots if in_range(s["id"], a.only)]
    if not shots:
        sys.exit("no shots in range")

    have = {s["id"]: find_media(a.media, s["id"]) for s in shots}
    n_img = sum(1 for v in have.values() if v and v.lower().endswith(IMG))
    n_vid = sum(1 for v in have.values() if v and v.lower().endswith(VID))
    n_miss = sum(1 for v in have.values() if not v)
    print(f"{len(shots)} shots: {n_vid} video, {n_img} still, {n_miss} missing")
    if a.report:
        for s in shots:
            print(f"  {s['id']} {s['dur']:5.1f}s {s['type']:9s} {os.path.basename(have[s['id']]) if have[s['id']] else '— MISSING'}")
        return

    tmp = tempfile.mkdtemp(prefix="rough_")
    try:
        parts = []
        for i, s in enumerate(shots):
            p = os.path.join(tmp, f"{i:04d}.mp4")
            render_shot(i, s, have[s["id"]], W, H, a.fps, p)
            parts.append(p)
            print(f"  {s['id']} done", end="\r")
        lst = os.path.join(tmp, "list.txt")
        with open(lst, "w") as f:
            f.writelines(f"file '{p}'\n" for p in parts)
        video = os.path.join(tmp, "video.mp4")
        sh(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])

        t0, t1 = shots[0]["start"], shots[-1]["end"]
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", video, "-ss", f"{t0:.3f}", "-to", f"{t1:.3f}", "-i", a.audio]
        if a.music:
            cmd += ["-stream_loop", "-1", "-ss", f"{t0:.3f}", "-i", a.music]
            if a.duck:
                af = (f"[1:a]aformat=channel_layouts=stereo,asplit=2[v][sc];"
                      f"[2:a]aformat=channel_layouts=stereo,volume={a.music_db}dB[m];"
                      f"[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md];"
                      f"[v][md]amix=inputs=2:duration=first:normalize=0[a]")
            else:
                af = (f"[2:a]aformat=channel_layouts=stereo,volume={a.music_db}dB[m];"
                      f"[1:a]aformat=channel_layouts=stereo[v];[v][m]amix=inputs=2:duration=first:normalize=0[a]")
            amap = "[a]"
        else:
            af, amap = None, "1:a"
        vmap = "0:v"
        if a.srt:
            srt = os.path.join(tmp, "subs.srt")
            shutil.copy(a.srt, srt)
            vf = (f"subtitles={srt}:force_style='FontName={a.font},FontSize=22,PrimaryColour=&H00FFFFFF,"
                  f"OutlineColour=&H00101010,BorderStyle=1,Outline=2,Shadow=1,MarginV=40'")
            if t0 > 0:
                vf = f"setpts=PTS+{t0}/TB,{vf},setpts=PTS-STARTPTS"
            cmd_v = ["-filter_complex", (af + ";" if af else "") + f"[0:v]{vf}[vo]"]
            vmap = "[vo]"
        else:
            cmd_v = ["-filter_complex", af] if af else []
        cmd += cmd_v + ["-map", vmap, "-map", amap, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", a.out]
        sh(cmd)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\nwrote {a.out} ({probe_dur(a.out):.1f}s)")


if __name__ == "__main__":
    main()
