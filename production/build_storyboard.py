# -*- coding: utf-8 -*-
"""Storyboard docx (5 fields per shot + image prompt) from timeline/shots.csv + storyboard_data.py.
  python build_storyboard.py 1   -> סטוריבורד_היהלום_שבכתר_v1.docx + storyboard_prompts.json"""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lib_docx import doc, para, h1, h2, table, code_box, page_break, NAVY, GOLD
from storyboard_data import SB
V = sys.argv[1] if len(sys.argv) > 1 else "1"
SR = json.load(open(os.path.join(HERE, "style_rules.json"), encoding="utf-8"))
rd = lambda f: list(csv.DictReader(open(os.path.join(HERE, "timeline", f), encoding="utf-8-sig")))
shots = {s["shot_id"]: s for s in rd("shots.csv")}
lines = {l["line_id"]: l for l in rd("timeline.csv")}
uses = {}
for s in shots.values():
    for lid in s["lines"].split(): uses.setdefault(lid, []).append(s["shot_id"])
def tc(t): return f"{int(t // 60)}:{t % 60:04.1f}"
covered, prompts, cur_act, offs = set(), {}, None, {}
para('בס"ד', size=10)
para("היהלום שבכתר: סטוריבורד, פיקסאר", bold=True, size=20, color=NAVY, center=True, space_after=2)
para(f"גרסה {V} · לפי script.txt v2 ו־timeline (4:58) · 18.11.2026 · לאישור", size=11, color=GOLD, center=True, space_after=10)
para("**איך לקרוא:** כל שוט מ־shots.csv מופיע עם חמשת השדות: נרציה, תיאור, פריים ראשון, תנועה ותאורה. אחריהם בא פרומפט התמונה לפריים הראשון "
     "(באנגלית, ובבנייה עוטפים אותו ב־[STYLE] וב־[RULES]), ורשימת דפי הרפרנס שמצרפים. שוטים ארוכים מ־10 שניות פוצלו ל־a/b. "
     "**צד המסך:** המלך תמיד מימין. הנסיך, הרופא והיועץ משמאל. בשוטי ליפסינק, מי שמקשיב שומר על פה סגור.")
for sid, part, scene, first, motion, light, prompt, refs in SB:
    base = sid[:4]; s = shots[base]
    if s["act"] != cur_act:
        cur_act = s["act"]; page_break(); h1(cur_act)
    st = float(s["start"]) + offs.get(base, 0)
    en = float(s["end"]) if part is None else min(float(s["end"]), st + part)
    offs[base] = en - float(s["start"])
    nar = []
    ls = s["lines"].split()
    if part is not None and len(ls) > 1: ls = [ls[min("ab".index(sid[4]), len(ls) - 1)]]
    for lid in ls:
        l = lines[lid]; mark = ""
        if len(uses[lid]) > 1: mark = f" (חלק {uses[lid].index(base) + 1}/{len(uses[lid])})"
        if part is not None and lid in covered: continue
        covered.add(lid)
        nar.append((f"**{l['speaker']}:** " if l["speaker"] != "קריינות" else "") + l["text"] + mark)
    if not nar: nar = ["(המשך השורה מהשוט הקודם)"]
    typ = "ליפסינק" if s["type"] == "lipsync" else "קריינות"
    h2(f"{sid} · {tc(st)}–{tc(en)} · {en - st:.1f} ש' · {typ}")
    table(["#", "שדה", "תוכן"], [
        ["1", "נרציה", "\n".join(nar)],
        ["2", "תיאור הסצנה", scene],
        ["3", "הפריים הראשון", first],
        ["4", "תנועה ואנימציה", motion],
        ["5", "תאורה", light],
        ["", "רפרנסים", " · ".join(refs) if refs else "בלי (שוט מעבר)"],
    ], widths=[0.7, 2.6, 13.7], ltr_cols=())
    full = f"{SR['style']} {prompt} {SR['rules']}"
    prompts[sid] = {"start": round(st, 2), "end": round(en, 2), "refs": refs, "prompt": full}
    code_box(prompt)
page_break(); h1("מה צריך לעדכן בתנ\"ך הדמויות בעקבות התסריט החדש")
for b in ["**L7 מצפה הרוח** כבר לא נחוץ, כי האבקה לא עפה ברוח. במקומו צריך **גרם מדרגות שיש לבן ומפותל** (S029). מציע לייצר אותו בתור LOC_L7 החדש.",
          "**שורות המלך** בדף המלך עודכנו בתסריט: \"גם אם ספק שתגיע טיפה, וספק אם תעזור…\" ו\"תנו להם להישפך…\".",
          "**הגביע** הופך לאובייקט מרכזי (S024–S025). הוא כבר נמצא ב־REF_props.",
          "**רועה צעיר בכפר שבקצה** (S009, S031) הוא דמות רקע חדשה. מספיק לתאר אותו בפרומפט, בלי דף נפרד."]:
    para("• " + b)
out = os.path.join(HERE, f"סטוריבורד_היהלום_שבכתר_v{V}.docx"); doc.save(out)
json.dump(prompts, open(os.path.join(HERE, "storyboard_prompts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(out, len(prompts), "shots")
