---
name: rough-cut-assembler
description: Automatically assemble a rough cut / animatic of an animated film from shots.csv, a folder of shot images and clips (named by shot id), the narration audio, optional music with ducking and burned-in Hebrew subtitles, using ffmpeg. Missing shots become timed placeholder cards, so the full film can be watched from day one and re-rendered every time new shots arrive. Use whenever Yitzchak wants a rough cut, animatic, "גרסה גסה", to see the film so far, to check pacing, to drop new clips into the edit, or to render a range of shots — even if he just uploads a batch of new images or clips.
---

# הרכבת גרסה גסה

הגרסה הגסה נבנית מהיום הראשון שיש בו קריינות, ומתעדכנת בכל פעם שמגיעים שוטים חדשים. כך רואים מוקדם איפה הקצב נופל ואילו שוטים עוד חסרים.

## קלט

- `shots.csv` מ־narration-to-timeline.
- תיקיית מדיה. **שם הקובץ מתחיל במזהה השוט:** `S012.png`, `S012_v2.mp4`, `S012_kling.mov`. כשיש כמה קבצים לאותו שוט, נבחר החדש ביותר, ולכן מספיק לזרוק לתיקייה גרסה חדשה.
  - תמונה: מקבלת תנועת Ken Burns איטית (פעם פנימה, פעם החוצה).
  - וידאו: נחתך לאורך השוט. אם הוא קצר מדי, הפריים האחרון מוחזק.
  - חסר: כרטיס כהה עם מזהה, סוג ומשך, כך שהתזמון נשמר.
- `narration_master.wav`, ובאופן אופציונלי מוזיקה וכתוביות.

## הרצה

```bash
# מה יש ומה חסר
python3 scripts/assemble.py --shots timeline/shots.csv --media shots/ --audio timeline/narration_master.wav --out x.mp4 --report

# גרסה גסה מלאה
python3 scripts/assemble.py --shots timeline/shots.csv --media shots/ --audio timeline/narration_master.wav \
    --music score.mp3 --music-db -14 --duck --srt timeline/subtitles.srt --font Heebo --out rough_v3.mp4

# רק מערכה אחת
python3 scripts/assemble.py ... --only S020-S034 --out act3.mp4
```

- `--size 1920x1080` ו־`--fps 30` הם ברירת המחדל. לגרסה אנכית: `--size 1080x1920`. התמונה נחתכת מהמרכז, ולכן כדאי לצלם עם הפעולה בשליש האמצעי.
- `--duck` מנמיך את המוזיקה בכל פעם שהקול מדבר.
- הכתוביות נצרבות עם libass, ועברית מימין לשמאל מוצגת נכון. אם הפונט לא מותקן, משתמשים ב־`--font "DejaVu Sans"`.
- 5 דקות נבנות בכדקה וחצי בענן.

## אחרי ההרצה

1. מדווחים כמה שוטים הם וידאו, כמה סטילס וכמה חסרים, ושולחים את הקובץ למשתמש.
2. רושמים את ההערות שלו לפי מזהה שוט (S###), כדי שיהיה ברור מה לייצר מחדש.
3. זו **גרסת עבודה**: בלי מעברים מעוצבים, בלי תיקון צבע ובלי מיקס סופי. את הגרסה הסופית עורכים בתוכנת העריכה, על בסיס אותו shots.csv.
