---
name: lipsync-shot-pack
description: Build the lip-sync production pack for an animated Pixar-style film. For every dialogue line in timeline.csv it cuts the exact audio clip and writes an image prompt and an animation prompt with fixed screen side, visible mouth, closed-mouth listeners, plus a QC checklist and warnings. Use whenever Yitzchak's project reaches dialogue / lip-sync shots (Kling, Hedra, Veo, Flow, Grok lipsync), asks for "ליפסינק", dialogue shots, talking characters, cutting the dialogue audio, or prompts for speaking characters — even if he only says "now the dialogue shots".
---

# חבילת ליפסינק

הכללים שנלמדו בנרות באפלה, בחבילה אוטומטית אחת:
- **צד קבוע במסך לכל דמות** לאורך כל הסרט.
- **פה סגור למי שמקשיב.** זה נכתב בכל פרומפט הנפשה.
- **שפתיים גלויות:** שפם קצר מעל השפה, בלי ידיים, אביזרים או שיער מול הפה.
- **פנים עד 30 מעלות מהמצלמה**, בתקריב בינוני.
- שורה ארוכה מ־8 שניות מתפצלת לשני שוטים או לזווית נגדית.

## קלט

1. `timeline.csv`, `shots.csv` ו־`narration_master.wav` מהסקיל narration-to-timeline.
2. `characters.json`, שנבנה מהתנ"ך של הפרויקט:

```json
{
  "style": "[STYLE] ... (הפתיח הקבוע של הפרויקט)",
  "rules": "[RULES] ... (הסיומת הקבועה)",
  "scenes": {"ג. מועצת הרופאים": ["המלך", "הרופא הראשי", "היועץ"]},
  "characters": {
    "המלך": {"en": "the king", "side": "right", "voice": "Orus",
             "look": "about 50, tall, full rounded brown-gray beard, short moustache, deep-blue velvet robe ...",
             "ref": "REF_king_APPROVED.png"}
  }
}
```
- `side`: `right` או `left`. את הצד קובעים פעם אחת בתנ"ך.
- `scenes` (אופציונלי): מי נמצא בפריים בכל מערכה. כך גם דמות ששותקת מקבלת "פה סגור". בלי השדה הזה, המקשיבים נקבעים לפי הדוברים בשורות הסמוכות.
- `look`: התיאור באנגלית מהתנ"ך (פנים, זקן, בגדים).

## הרצה

```bash
python3 scripts/lipsync_pack.py --timeline timeline/timeline.csv --shots timeline/shots.csv \
    --audio timeline/narration_master.wav --characters characters.json --out lipsync/
```

## פלט

- `lipsync/audio/S012_המלך.wav`: האודיו של השורה, עם 0.15 שניות לפני ואחרי.
- `lipsync/lipsync_pack.md`: לכל שוט יש שורה, אודיו, רפרנס, צד, מקשיבים, פרומפט תמונה, פרומפט הנפשה וצ'קליסט. אזהרות מופיעות בראש הקובץ.
- `lipsync/lipsync_pack.csv`: אותו תוכן בטבלה.

## אחרי ההרצה

1. מוסרים למשתמש את האזהרות קודם (שורה ארוכה, צד שהתחלף, שני דוברים באותו צד).
2. את פרומפט התמונה מריצים עם דף הרפרנס המאושר של הדמות המדברת, וגם של המקשיבים אם הם בפריים.
3. מעבירים את התמונה שאושרה ואת קובץ האודיו למנוע הליפסינק. אם המנוע מקבל פרומפט, משתמשים בפרומפט ההנפשה.
4. שומרים את הקליפ המוכן בשם `S012...mp4` בתיקיית המדיה של rough-cut-assembler, והוא נכנס לגרסה הגסה אוטומטית.
5. הפרומפטים נכתבים באנגלית. **לעולם לא לבקש טקסט עברי בתמונה.**
