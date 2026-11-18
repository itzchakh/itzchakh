---
name: narration-to-timeline
description: Turn a Hebrew narration script plus its recorded TTS audio (Gemini voices like Charon, or any voice) into timeline.csv, shots.csv (6–10s sub-scenes, one lip-sync shot per dialogue line) and subtitles.srt. Use whenever Yitzchak has recorded or is about to record narration for an animated film or clip, asks for a timeline, timing, shot list by seconds, "timeline.csv", sub-scene split, subtitles for narration, or wants to know how long each act runs or what share of the film is dialogue — even if he only says "here are the audio files".
---

# קריינות ⟵ timeline

הסקיל הופך תסריט קריינות ואודיו מוקלט לשלושה קבצים שכל השלבים הבאים נשענים עליהם:

| קובץ | מה יש בו | מי משתמש בו |
|---|---|---|
| `timeline.csv` | כל שורה מדוברת: מזהה (L001), מערכה, דובר, התחלה, סוף, משך, טקסט | הסטוריבורד (שדה הנרציה), lipsync-shot-pack |
| `shots.csv` | תת־סצנות (S001): 6–10 שניות לקריינות, שוט נפרד לכל שורת דיאלוג (`type=lipsync`) | הסטוריבורד, rough-cut-assembler |
| `subtitles.srt` | כתוביות בשתי שורות מאוזנות | עריכה, גזירות אנכיות |
| `narration_master.wav` | (במצב clips) כל הקטעים מחוברים עם הפסקות | עריכה |

## פורמט התסריט

קובץ טקסט UTF-8, שורה מדוברת אחת בכל שורה, בדיוק לפי סדר ההקלטה:

```
# א. הממלכה המנגנת
בממלכה רחוקה, מעבר להרים ולעננים, היה הכול מנגן.
הנסיך: אבא! תשמע, המעיין למטה מנגן את השיר שלך!
# ג. מועצת הרופאים
הרופא הראשי: אדוני המלך… יש תרופה אחת.
```

- `# שם` פותח מערכה. שורה בלי `דובר:` (או עם `קריינות:`) היא קריינות.
- שם הדובר חייב להיות זהה לשם ב־characters.json של lipsync-shot-pack.
- שורות שמתחילות ב־`//` הן הערות.

## הרצה

**מצב מועדף: קובץ אודיו לכל שורה** (ככה מקליטים ב־TTS ממילא). התזמון מדויק לגמרי:

```bash
python3 scripts/make_timeline.py --script script.txt --clips audio_lines/ --out timeline/ \
    --gap 0.35 --act-gap 1.5 --lead 0.5
```
הקבצים ממוינים במיון טבעי (line_2 לפני line_10), ומספרם חייב להיות שווה למספר השורות.

**קובץ ארוך אחד:** הסקריפט מוצא את ההפסקות (silencedetect) ומתאים אותן לשורות לפי האורך:
```bash
python3 scripts/make_timeline.py --script script.txt --audio narration.wav --out timeline/
```
אם אין מספיק הפסקות (למשל כשיש מוזיקה מתחת לקול), הוא מתריע שהחלוקה גסה. במקרה כזה עדיף לייצא מחדש קטעים נפרדים.

## אחרי ההרצה

1. מדווחים למשתמש את מה שהסקריפט מדפיס: אורך כולל, אורך כל מערכה ו**אחוז הדיאלוג** (היעד בדרך כלל כ־15%).
2. אם מערכה ארוכה או קצרה מהתכנון, מציעים לקצר או להאריך טקסט **לפני** שיוצרים תמונות.
3. את `shots.csv` מעבירים לסטוריבורד (סקיל hebrew-storyboard): כל S### הוא תת־סצנה, ושדה הנרציה שלה הוא הטקסט של השורות שבה.
4. מעבירים את השוטים מסוג `lipsync` לסקיל lipsync-shot-pack.

## הערות

- גבולות השוטים נקבעים באמצע ההפסקה, כדי שהקאט לא ייפול על מילה.
- `--shot-min` / `--shot-max` משנים את טווח האורך של תת־סצנה (ברירת המחדל 6–10).
- שורת קריינות ארוכה מ־10 שניות מתפצלת לכמה שוטים שווים.
