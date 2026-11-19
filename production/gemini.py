#!/usr/bin/env python3
"""Small Gemini REST helper: TTS per script line, and image generation with reference images.

The API key is injected by the session's network proxy (network secret for
generativelanguage.googleapis.com, header x-goog-api-key); the placeholder below is replaced.

  python3 gemini.py models
  python3 gemini.py tts   --script script.txt --voices voices.json --out audio_lines/ [--only 3,7] [--takes 1]
  python3 gemini.py image --prompt-file p.txt --ref a.png --ref b.png --out out.png [--aspect 16:9]
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

API = "https://generativelanguage.googleapis.com/v1beta"
KEY = os.environ.get("GEMINI_API_KEY", "proxy-injected")
NARRATOR = "קריינות"


def call(method, path, body=None, timeout=300):
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(5):
        req = urllib.request.Request(f"{API}/{path}", data=data, method=method,
                                     headers={"x-goog-api-key": KEY, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:500]
            if e.code in (429, 500, 503) and attempt < 4:
                time.sleep(8 * (attempt + 1))
                continue
            sys.exit(f"HTTP {e.code}: {msg}")
    sys.exit("giving up")


def list_models():
    out, tok = [], ""
    while True:
        r = call("GET", "models?pageSize=200" + (f"&pageToken={tok}" if tok else ""))
        out += [m["name"].split("/")[-1] for m in r.get("models", [])]
        tok = r.get("nextPageToken")
        if not tok:
            return out


def pick(models, must, prefer=()):
    c = [m for m in models if all(k in m for k in must)]
    if not c:
        sys.exit(f"no model matching {must}: {models}")
    for p in prefer:
        for m in c:
            if p in m:
                return m
    return sorted(c)[-1]


def parse_script(path):
    lines = []
    for raw in open(path, encoding="utf-8"):
        s = raw.strip()
        if not s or s.startswith("//") or s.startswith("#"):
            continue
        spk, text = NARRATOR, s
        m = re.match(r"^\**([^:\"״,،]{1,30}?)\**\s*:\s*(.+)$", s)
        if m and len(m.group(1).split()) > 3:
            m = None
        if m:
            spk, text = m.group(1).strip(), m.group(2).strip()
        lines.append((spk, text))
    return lines


def tts(a):
    cfg = json.load(open(a.voices, encoding="utf-8"))
    model = a.model or pick(list_models(), ["tts"], prefer=("pro", "flash"))
    print("model:", model)
    os.makedirs(a.out, exist_ok=True)
    only = {int(x) for x in a.only.split(",")} if a.only else None
    for i, (spk, text) in enumerate(parse_script(a.script), 1):
        if only and i not in only:
            continue
        v = cfg["voices"][spk]
        t = text
        for k, rep in sorted(cfg.get("pron", {}).items(), key=lambda kv: -len(kv[0])):
            t = t.replace(k, rep)
        # keep direction separate so newer TTS models don't read it aloud
        prompt = (f"### DIRECTOR'S NOTES (do not read aloud)\n{v['style']}\n\n"
                  f"### TRANSCRIPT (read only this)\n{t}")
        for take in range(1, a.takes + 1):
            r = call("POST", f"models/{model}:generateContent", {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseModalities": ["AUDIO"],
                                     "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": v["voice"]}}}}})
            part = r["candidates"][0]["content"]["parts"][0]["inlineData"]
            pcm = base64.b64decode(part["data"])
            mime = part.get("mimeType", "")
            suffix = "" if a.takes == 1 else f"_t{take}"
            out = os.path.join(a.out, f"line_{i:02d}{suffix}.wav")
            raw = out + ".pcm"
            open(raw, "wb").write(pcm)
            m = re.search(r"rate=(\d+)", mime)
            if "wav" in mime:  # newer models return a WAV container
                inp = ["-i", raw]
            else:  # raw 16-bit PCM
                inp = ["-f", "s16le", "-ar", m.group(1) if m else "24000", "-ac", "1", "-i", raw]
            # trim leading/trailing silence, keep 80 ms
            subprocess.run(["ffmpeg", "-y", "-v", "error", *inp,
                            "-af", "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,"
                                   "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.12,areverse",
                            out], check=True)
            os.remove(raw)
            print(f"  line {i:02d} [{spk}/{v['voice']}] -> {os.path.basename(out)}")


def image(a):
    model = a.model or pick(list_models(), ["image"], prefer=("pro-image", "flash-image"))
    print("model:", model)
    parts = []
    for ref in a.ref or []:
        mime = "image/png" if ref.lower().endswith(".png") else "image/jpeg"
        parts.append({"inlineData": {"mimeType": mime, "data": base64.b64encode(open(ref, "rb").read()).decode()}})
    parts.append({"text": open(a.prompt_file, encoding="utf-8").read()})
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": a.aspect}}}
    r = call("POST", f"models/{model}:generateContent", body, timeout=600)
    for p in r["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            open(a.out, "wb").write(base64.b64decode(p["inlineData"]["data"]))
            print("wrote", a.out)
            return
    sys.exit("no image in response: " + json.dumps(r)[:800])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("models")
    t = sub.add_parser("tts")
    t.add_argument("--script", required=True)
    t.add_argument("--voices", required=True)
    t.add_argument("--out", required=True)
    t.add_argument("--only")
    t.add_argument("--takes", type=int, default=1)
    t.add_argument("--model")
    im = sub.add_parser("image")
    im.add_argument("--prompt-file", required=True)
    im.add_argument("--ref", action="append")
    im.add_argument("--out", required=True)
    im.add_argument("--aspect", default="16:9")
    im.add_argument("--model")
    a = ap.parse_args()
    if a.cmd == "models":
        print("\n".join(list_models()))
    elif a.cmd == "tts":
        tts(a)
    else:
        image(a)


if __name__ == "__main__":
    main()
