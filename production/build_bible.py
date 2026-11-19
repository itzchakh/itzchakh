# -*- coding: utf-8 -*-
"""Character / location / object bible for "Diamond in the Crown" (Pixar), with reference-sheet prompts.
Images found in production/refs_generated/<KEY>.png are embedded under their sheet."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from lib_docx import doc, para, h1, h2, bullet, table, code_box, image, page_break, NAVY, GOLD  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "refs_generated")
VERSION = sys.argv[1] if len(sys.argv) > 1 else "1"

STYLE = ("[STYLE] 3D animation movie still, rendered in authentic Disney Pixar style using Unreal Engine 5 / Octane Render with full ray tracing. "
         "Smooth stylized characters, soft clay materials, subsurface scattering (SSS) on skin, volumetric lighting, ray-traced soft shadows, "
         "rich cinematic color grade. Setting: a timeless fairy-tale kingdom where nature itself makes music: ringing springs, trees with strings "
         "of light, crystal wind chimes, tiny glowing musical notes drifting like fireflies. Backgrounds feel like a lush painterly matte painting "
         "with soft atmospheric perspective, while characters stay crisp clean Pixar 3D. Subtle turquoise and gold LED-neon glow inside water, "
         "crystals and light-strings only, never on the characters. 16:9.")
RULES = ("[RULES] Inside the kingdom all characters are men and boys in modest long clothing. In the modern-day finale each woman or man appears "
         "alone in the shot, women in modest dress with a headscarf or a wig, never touching anyone. The king's crown always matches the approved crown "
         "sheet: a tall gold crown of cresting water-wave arches cradling one huge diamond at the top; never a cross, orb, fleur-de-lis or any heraldic shape. "
         "No crosses, churches, stained-glass windows, steeples, onion domes, minarets, icons, idols, flags, coats of arms or heraldic symbols, not "
         "even tiny or blurred in the background. No halos or glowing rings around heads. No text, letters or labels anywhere. Mouths of speaking "
         "characters stay clearly visible; listeners keep their mouths closed. One consistent 3D Pixar render style.")
CROWN = ("the approved majestic crown from the attached crown sheet: a tall, heavy gold crown, its broad band engraved with flowing waves and set with "
         "turquoise and sapphire cabochons; six tall arches shaped like cresting water waves rise and curl inward like a fountain jet, tipped with "
         "pearls and tiny diamonds; at the top two waves lift and cradle one huge brilliant-cut diamond, the clear focal point, blazing with rainbow "
         "fire and a soft turquoise heart-glow that reflects on the gold")
SHEET = ("Character reference sheet on a clean white background, matching the layout and render style of the attached style sheet "
         "(style only, not the character): 4 close-ups on top, 6 full-body poses below. ")


PROMPTS = {}


# key -> approved file name in refs_generated
APPROVED = {"REF_crown": "REF_crown_v1.png", "REF_king": "REF_king_v2.png", "REF_prince": "REF_prince_v2.png", "REF_alter_rebbe": "REF_alter_rebbe_v2.png"}


def sheet(key, title, prompt, refs_note):
    PROMPTS[key] = prompt
    h2(title)
    para(f"**מצרפים:** {refs_note}", size=10)
    code_box(prompt)
    if key in APPROVED and os.path.exists(os.path.join(GEN, APPROVED[key])):
        image(os.path.join(GEN, APPROVED[key]), 16.5, f"{APPROVED[key]} · ✅ מאושר")
        return
    names = [f for f in os.listdir(GEN) if f.startswith(key + "_v") or f in (key + ".png", key + ".jpg")]
    for name in sorted(names, reverse=True):
        image(os.path.join(GEN, name), 16.5, f"{name} · נוצר אוטומטית, ממתין לאישור")
        break
    else:
        para("⏳ התמונה עוד לא נוצרה.", size=9, color=GOLD)


# ------------------------------------------------------------------ title
para('בס"ד', size=10)
para("היהלום שבכתר: תנ\"ך דמויות, לוקיישנים ואובייקטים, פיקסאר", bold=True, size=20, color=NAVY, center=True, space_after=2)
para(f"גרסה {VERSION} · 18.11.2026 · לפי תסריט v2", size=11, color=GOLD, center=True, space_after=10)
para("**הבסיס:** תוכנית השדרוג v3 וההחלטות שאושרו. **המבנה:** אותו מבנה של התנ\"ך של נרות באפלה: סגנון וכללים, דמויות, לוקיישנים, אובייקטים, "
     "ובסוף פרומפטים לדפי הרפרנס. **סדר העבודה:** מאשרים את הדפים, ורק אחריהם מייצרים את הפריימים של הסטוריבורד, כשכל פריים מקבל את דף הרפרנס של הדמות שבו.")

# ------------------------------------------------------------------ 1
h1("1. ההחלטות שאושרו")
table(["#", "נושא", "ההחלטה"], [
    ["1", "פורמט", "16:9, 1920×1080, 30fps, כ־5 דקות. כל קומפוזיציה עם הפעולה בשליש האמצעי, כדי שאפשר יהיה לגזור 9:16"],
    ["2", "סגנון", "פיקסאר תלת־ממדי כמו בנרות באפלה. הרקעים בסגנון ציור מאט ציורי, והדמויות פיקסאר נקי"],
    ["3", "המשל", "ממלכת אגדה בלי לאום ובלי סמלים. במשל אין כיפות ואין ציציות, כדי לא לערבב בינו לבין הנמשל"],
    ["4", "הכתר", "כתר מלכותי גבוה (REF_crown_v1, מאושר): קשתות של גלים מתנפצים, ושני גלים בראשן מרימים יהלום ענק. אף פעם לא צלב, כדור או פלר־דה־ליס"],
    ["5", "אדמו\"ר הזקן", "מוצג בנמשל, בנוי אחד לאחד מול הציור המסורתי. הגזמה מינימלית, בלי הילה ובלי דיאלוג"],
    ["6", "דיאלוג", "כ־15%. 5 דוברים: קריין (Charon), המלך (Orus), הנסיך (Puck), הרופא הראשי (Algenib), היועץ (Iapetus)"],
    ["7", "צד במסך", "המלך תמיד בצד ימין. הנסיך, הרופא והיועץ תמיד בצד שמאל"],
    ["8", "פסקול", "\"פדה בשלום\" כמוטיב שחוזר לאורך כל הסרט, בעיבודים שונים לכל מערכה. שיא כשהטיפה מגיעה לנסיך והמים זורמים לכל הממלכה, ושוב בשחרור בי\"ט כסלו"],
], widths=[0.8, 2.6, 13.6])

# ------------------------------------------------------------------ 2
h1("2. הסגנון והכללים")
para("**שלושה עולמות.** **הממלכה המנגנת:** זהב, טורקיז וירוק אחו, באור של שעת זהב. **הממלכה השותקת:** אפור־כחלחל, ערפל ואור שטוח. "
     "**הנמשל:** כחול לילה ונר ענבר, שמתחלפים בסוף בזהב שזורח מכל מקום. "
     "**הגשר בין העולמות הוא מי היהלום:** מים צלולים שבתוכם מנצנצת אבקת היהלום, נקודות אור לבנות־תכלת עם ניצוץ זהב. הטיפה הזוהרת נראית בדיוק אותו דבר במשל ובנמשל.")
h2("[STYLE] פתיח קבוע")
code_box(STYLE)
h2("[RULES] סיומת קבועה")
code_box(RULES)
h2("כללים שעוברים מהסרטים הקודמים")
bullet("**דמות אחת לכל אחד:** כל פריים שבו מופיעה דמות מקבל את דף הרפרנס המאושר שלה.")
bullet("**פה סגור למי שמקשיב**, וזה נכתב בכל פרומפט הנפשה.")
bullet("**צד קבוע בדיאלוג:** המלך בצד ימין, וכל השאר בצד שמאל.")
bullet("**שפתיים גלויות:** לכל הדמויות המדברות יש שפם קצר שלא מסתיר את השפה. לאדמו\"ר הזקן יש שפם מלא כמו בציור, והוא לא מדבר.")
bullet("**בלי טקסט בתמונה:** ספרים, מגילות ודפי תניא מופיעים עם קווים מטושטשים בלבד. כותרות מוסיפים בעריכה.")
bullet("**מי היהלום** נראים תמיד אותו דבר: מים צלולים עם נקודות אור קטנות בלבן־תכלת, ניצוץ זהב וזוהר טורקיז רך. אף פעם לא אותיות.")

# ------------------------------------------------------------------ 3
h1("3. הדמויות")


def char(title, rows):
    h2(title)
    table(["מאפיין", "הגדרה"], rows, widths=[3, 14])


char("3.1 המלך (Orus · צד ימין)", [
    ["גיל וגוף", "כבן 50. גבוה ורחב כתפיים, עומד זקוף. צללית של משולש הפוך: גלימה רחבה וכתפיים רחבות."],
    ["פנים", "פנים מלבניות וחמות, עיניים חומות וחמות עם קמטי עייפות, גבות עבות. אף ישר ומעט רחב."],
    ["זקן ושיער", "זקן מלא ומעוגל באורך בינוני, חום עם פסים אפורים. שפם קצר והשפתיים גלויות. שיער גלי חום־אפור עד האוזניים."],
    ["כתר", "לפי REF_crown_v1 (מאושר): כתר זהב גבוה וכבד. הטבעת עם חריטת גלים ואבני טורקיז וספיר, שש קשתות של גלים מתנפצים עם פנינים, ושני גלים בראשו שמרימים יהלום ענק. אחרי הכתישה הגלים נשארים פתוחים וריקים."],
    ["לבוש", "גלימת קטיפה בכחול עמוק עם רקמת גלי מים בזהב בשוליים, חולצת פשתן לבנה עם צווארון עומד ואבנט זהב. בלי סמלים ובלי תכשיטים."],
    ["הבעות מפתח", "גאווה ושמחה עם הבן · דאגה בלי שינה · הקשבה כבדה · היסוס מול הכתר · החלטה שקטה · דמעות של שמחה"],
    ["תנועה", "איטית ומלאת משקל. כשהוא מחליט, הוא מניח יד על לבו."],
    ["דיאלוג", "4 שורות: \"כתר אפשר לעשות מחדש\" · \"גם אם ספק שתגיע טיפה, וספק אם תעזור… בן, יש לי רק אחד\" · \"כתשו אותו\" · \"תנו להם להישפך. אפילו טיפה אחת…\""],
])
char("3.2 הנסיך (Puck · צד שמאל)", [
    ["גיל וגוף", "כבן 12. רזה וזריז, תמיד בתנועה כשהוא בריא."],
    ["פנים", "פנים עגולות, עיניים גדולות בצבע לוז, נמשים קלים. **בחולי נראה מסכן מאוד:** עור חיוור־אפרפר, לחיים שקועות, עיגולים כהים, שפתיים סדוקות, תלתלים לחים של זיעה ומטלית רטובה על המצח, ידיים דקות ורפויות, קטן מתחת לשמיכה. ובריפוי הלחיים ורודות."],
    ["שיער וכיסוי ראש", "תלתלים חומים כהים, קצרים ופרועים. **תמיד עם כיסוי ראש:** כובע קטיפה עגול בטורקיז עם רצועת זהב רקומה בגלים ופנינה קטנה מלפנים. במיטה כובע שינה רך מפשתן לבנה."],
    ["לבוש", "**בריא:** גלימה קצרה מקטיפת טורקיז עם רקמת גלים בזהב, מעל כתונת פשתן לבנה, חגורת עור עם אבזם זהב ומגפיים רכים. **חולה:** כותונת לילה לבנה ארוכה, מתחת לשמיכת טלאים בכחול וזהב."],
    ["אביזר", "חליל עץ קטן, שבו הוא \"עונה\" למעיין."],
    ["הבעות מפתח", "צחוק ופליאה · חולשה ועיניים עצומות · התעוררות איטית ולחישה · חיוך מלא אור"],
    ["דיאלוג", "2 שורות: \"אבא! תשמע…\" (בריא, צועק משמחה) · \"אבא… אני שומע מוזיקה\" (לחישה)"],
])
char("3.3 הרופא הראשי (Algenib · צד שמאל)", [
    ["גיל וגוף", "כבן 70. נמוך וכתפיים מעט שמוטות. זהיר ועדין."],
    ["פנים", "עיניים טובות ומודאגות מאחורי משקפיים עגולים עם מסגרת זהב, לחיים עגולות."],
    ["זקן", "זקן לבן ארוך ומסודר עד אמצע החזה. שפם קצר מעל השפה, והשפתיים גלויות."],
    ["לבוש", "גלימה ארוכה בירוק כהה וכובע רך ירוק בצורת כיפה רחבה. תיק עור חום על הכתף."],
    ["אביזרים", "מגילה ישנה **בלי טקסט קריא**, זכוכית מגדלת ובקבוקון זכוכית."],
    ["הבעות מפתח", "ריכוז על המגילה · גילוי והיסוס · צער כשהוא אומר \"היהלום שבכתר\""],
    ["דיאלוג", "2 שורות: \"אדוני המלך… יש תרופה אחת\" · \"היהלום שבכתר. לכתוש אותו לאבקה, להמיס במים, ולהשקות את הנסיך\""],
])
char("3.4 היועץ (Iapetus · צד שמאל)", [
    ["גיל וגוף", "כבן 45. גבוה ורזה, עומד מתוח."],
    ["פנים", "פנים צרות, גבות חדות ומכווצות, עיניים כהות ונבונות."],
    ["זקן", "זקן שחור קצר ומחודד. שפם קצר והשפתיים גלויות."],
    ["לבוש", "מעיל ארוך בבורדו עם כפתורי זהב, כובע שחור רך עם חלק עליון שטוח. מחזיק ספר חשבונות עבה **בלי טקסט**."],
    ["הבעות מפתח", "בהלה · מחאה נאמנה · השלמה שקטה (מרכין ראש)"],
    ["דיאלוג", "שורה אחת: \"את היהלום?! אדוני, זה לב הממלכה! ואם נכתוש, ורוב האבקה תישפך?\""],
])
char("3.5 הצורף (שותק)", [
    ["גיל וגוף", "כבן 60. רחב, עם אמות ידיים עבות."],
    ["פנים וזקן", "זקן אפור קצר ומלא, ועדשת מגדלת של צורף על עין אחת."],
    ["לבוש", "סינר עור חום מעל חולצה כהה, וכובע עור חום."],
    ["תפקיד", "כותש את היהלום במכתש זהב קטן, בעדינות ובדמעה, וממיס את האבקה בגביע מים. מופיע רק במערכה ה."],
])
char("3.6 אדמו\"ר הזקן (נמשל · בלי דיאלוג)", [
    ["רפרנס חובה", "הציור המסורתי (refs/alter_rebbe_traditional_chabadpedia.jpg). מצרפים אותו לכל פריים שבו הוא מופיע."],
    ["גיל", "לפי הציור, כבן 65 ומעלה."],
    ["תנוחה ומבט", "שלושה רבעים לשמאל המסך. מבט מהורהר הצידה, לא אל המצלמה."],
    ["פנים", "מצח גבוה עם קמטים אופקיים עמוקים, גבות לבנות עבות, עיניים בהירות ושקועות עם שקיות כבדות, אף ארוך ובולט, עור בהיר ולחיים ורדרדות."],
    ["זקן ושיער", "זקן לבן מלא, ארוך, רחב וגלי, עד אמצע החזה. שפם לבן מלא. שיער לבן מתולתל בולט מעל האוזניים, והפאות משתלבות בו."],
    ["כובע ולבוש", "כיפה שחורה רכה ועגולה, גדולה, מעט לאחור. בלי כובע מעליה. בגד שחור ארוך עם צווארון גבוה וסגור."],
    ["רמת הגזמה", "הכי נמוכה בסרט: פרופורציות כמעט ריאליסטיות וחומרים רכים."],
    ["סצנות", "כותב בלילה לאור נר · ליד חלון הכלא בפטרבורג באור ירח · יוצא בדלת אל השלג בי\"ט כסלו"],
])
char("3.7 אנשים בעולם של היום (סיום)", [
    ["עיקרון", "כל אחד לבד בשוט, ובכל שוט טיפת אור זוהרת יוצאת מהמסך. גיוון בגווני עור, בגילים ובערים."],
    ["1", "בחור כבן 20 עם כיפה סרוגה וזקן קצר, באוטובוס בירושלים"],
    ["2", "סבא עם זקן לבן ארוך ומגבעת שחורה, ליד חלון עם נוף גגות אבן"],
    ["3", "אישה כבת 35 עם מטפחת צבעונית, במטבח בבוקר"],
    ["4", "אישה כבת 45 עם פאה, ליד שולחן משרד בעיר גדולה"],
    ["5", "ילד כבן 9 עם כיפה וציציות, בחצר בית ספר"],
    ["6", "גבר בחליפה בלי זקן ובלי כיפה, ברכבת התחתית בניו יורק. הטיפה מגיעה גם אליו"],
])
char("3.8 קהל", [
    ["הרופאים", "5–6 רופאים בגילים שונים, עם זקנים בצבעים שונים וגלימות בגווני אדמה. כובעים רכים."],
    ["משרתי הארמון", "גברים צעירים במעילים טורקיז אחידים. הם מחזיקים את הגביע ומטים אותו אל שפתי הנסיך."],
    ["אנשי הממלכה", "בשוטים רחבים בלבד: איכרים, רועים ונערים בשדות, כולם גברים ונערים. רועה צעיר בכפר שבקצה הממלכה (S009, S031) מתואר בפרומפט, בלי דף נפרד."],
])

# ------------------------------------------------------------------ 4
h1("4. הלוקיישנים")
para("מייצרים את הלוקיישנים ריקים, בלי דמויות. לכל לוקיישן יש **שתי גרסאות תאורה: מנגן ושותק** (חוץ מ־L8–L9).")
LOCS = [
    ["L1", "עמק המעיינות", "עמק ירוק ורחב עם עשרות מעיינות קטנים, מפלים דקים, פרחים זוהרים ונחל מתפתל, ובאופק הרים כחולים",
     "מנגן: שעת זהב, גלי אור עגולים על המים · שותק: ערפל אפור, המים קפואים", "הוק, א, ב, ה"],
    ["L2", "יער הנבלים", "עצי ענק שענפיהם נמתחים כמו מיתרים של אור, ובין הענפים תווים זוהרים כגחליליות",
     "מנגן: קרני שמש אלכסוניות · שותק: מיתרים רפויים ואפורים", "א, ב"],
    ["L3", "הארמון על הצוק", "ארמון לבן־זהב עם גגות שטוחים, מרפסות וקשתות, מעל ים עננים. בלי צריחים מחודדים ובלי סמלים",
     "מנגן: שקיעה ורודה ופעמוני רוח קריסטליים · שותק: שמיים אפורים", "הוק, א, ה"],
    ["L4", "אולם הכתר", "אולם עגול עם רצפת שיש שמשקפת ועמודים בהירים. הכתר על כרית קטיפה בבורדו, על עמוד במרכז",
     "קרן אור אחת מלמעלה. אבק באוויר שרוטט בקצב", "א, ד"],
    ["L5", "חדר הנסיך", "מיטת אפריון עם וילונות טורקיז, חלון גבוה אל העמק, מדף עם כלי נגינה קטנים וספרים",
     "חולי: וילון כבד ואור אפור · ריפוי: החלון פתוח ואור זהב נשפך פנימה", "ב, ה"],
    ["L6", "חדר הרופאים", "שולחן עץ ארוך עם מגילות, צנצנות, מאזניים ונרות. חלונות עגולים בלבד, בלי ויטראז'",
     "אור נרות חם, צללים ארוכים, והאבק באוויר עומד", "ג"],
    ["L7", "מדרגות השיש", "גרם מדרגות לולייני ורחב משיש לבן, עם מעקה זהב בצורת גלים, שיורד מחדר הנסיך אל שער הארמון. מי היהלום זורמים עליו כמו מפל קטן וזוהר",
     "אור בוקר זהוב מחלונות קשת גבוהים, והמים זוהרים בטורקיז", "ה"],
    ["L8", "פטרבורג 1798 (נמשל)", "חדר עבודה צנוע עם שולחן עץ ונר · תא כלא עם חלון קטן מסורג · נהר נבה קפוא ושלג · דלת יציאה",
     "כחול לילה, קרן ירח, להבת נר ענברית. בסוף אור בוקר לבן", "ו"],
    ["L9", "העולם היום (נמשל)", "גגות ירושלים · מטבח · משרד · חצר בית ספר · רכבת תחתית בניו יורק · חלון עם נוף לעיר",
     "ערב, אורות עיר, ומסך טלפון שזוהר", "ו, סיום"],
]
table(["#", "לוקיישן", "מראה קבוע", "תאורה", "מערכות"], LOCS, widths=[0.9, 2.6, 6.8, 4.9, 1.8])

# ------------------------------------------------------------------ 5
h1("5. אובייקטים")
table(["אובייקט", "מראה קבוע", "איפה"], [
    ["הכתר", "לפי REF_crown_v1 (מאושר): כתר זהב גבוה. הטבעת עם חריטת גלים ואבני טורקיז וספיר, שש קשתות של גלים מתנפצים עם פנינים ויהלומים קטנים, ושני גלים בראשו שמרימים את היהלום. בלי צלב, בלי כדור ובלי פלר־דה־ליס", "א, ד, ה (גלים ריקים)"],
    ["היהלום", "יהלום ענק בליטוש קלאסי, בגודל אגרוף של ילד, והוא מוקד הכתר. שקוף לגמרי עם שבירות אור בצבעי הקשת, ומתוכו פועם זוהר תכלת־זהב רך בקצב המוזיקה", "הוק, א, ד, ה"],
    ["אבקה ומי היהלום", "אבקה דקה כמו אור, שנמסה במים צלולים. המים מנצנצים בנקודות לבנות־תכלת עם ניצוץ זהב וזוהר טורקיז רך, וכשהם נשפכים הם זורמים כשובל זוהר. **אותו מראה במשל ובנמשל**", "ה, ו, סיום"],
    ["מכתש ועלי", "מכתש זהב קטן ועלי מזהב, פשוטים וחלקים", "ה"],
    ["גביע", "גביע קריסטל פשוט עם מים צלולים, שהאבקה מנצנצת בתוכם. אובייקט מרכזי במערכה ה", "ה"],
    ["מגילות וספרים", "קלף ישן ועור חום. **בלי טקסט קריא**, רק קווים מטושטשים", "ג"],
    ["חליל הנסיך", "חליל עץ קטן ובהיר עם 6 חורים", "א, ה"],
    ["דפי התניא", "דפים בודדים בכתב יד, עם קווי כתב מטושטשים **בלי אותיות קריאות**, נוצה ודיו ונר חלב", "ו"],
    ["טלפונים", "טלפונים רגילים בלי לוגו. המסך זוהר, וטיפת אור יוצאת ממנו", "סיום"],
], widths=[2.6, 11, 3.4])
h2("אובייקטים מוזיקליים וזוהרים (שכבת הרקע)")
table(["אובייקט", "מראה", "מצב שותק"], [
    ["מעיין מצלצל", "בריכת מים קטנה עם טבעות אור שמתפשטות בכל טיפה, ואדי זהב קל", "קרח אפור, בלי טבעות"],
    ["עץ נבל", "ענפים מתוחים כמיתרים של אור בטורקיז, שרוטטים ברוח", "מיתרים רפויים ואפורים"],
    ["פעמוני רוח", "שרשראות קריסטל על קשתות הארמון, שמשאירות שובל של ניצוצות", "תלויים דוממים"],
    ["תווי גחליליות", "תווים קטנים וזוהרים שמרחפים בין העצים", "נופלים לעשב ונכבים"],
    ["פרחי פעמון", "פרחים שהכותרת שלהם נדלקת לפי הקצב", "סגורים ואפורים"],
], widths=[3, 8.5, 5.5])

# ------------------------------------------------------------------ 6
page_break()
h1("6. דפי הרפרנס: פרומפטים ותמונות")
sheet("REF_crown", "דף 0: הכתר (מאושר)", STYLE + " Hero prop reference sheet on a clean white background of " + CROWN +
      ". Views: front, three-quarter, side, top-down, a macro of the diamond, and the crown with the diamond removed, the two top waves open and empty. No labels. " + RULES,
      "שום דבר. זה דף הבסיס לכל פריים שיש בו כתר")
para("**הסדר:** קודם יוצרים את דף המלך ומאשרים אותו, והוא הופך לרפרנס הסגנון של כל שאר הדפים, כמו REF_rabbi_APPROVED במערה. "
     "כל פרומפט מתחיל ב־[STYLE] ונגמר ב־[RULES], כמו בפרקים 2–3.")

sheet("REF_king", "דף 1: המלך", STYLE + " " + SHEET +
      "A fairy-tale king about 50, tall and broad-shouldered, warm tired brown eyes, thick brows, full rounded medium-length brown beard with gray "
      "streaks, short moustache with clearly visible lips, wavy brown-gray hair to the ears. He wears " + CROWN + ". "
      "Deep-blue velvet robe with gold wave embroidery on the hems, white linen shirt with a standing collar, gold sash. "
      "Close-ups: proud loving smile; sleepless worry; grave listening; quiet resolve with tears in his eyes. Poses: front; three-quarter; back; "
      "standing with one hand on his heart; seated beside a bed, leaning forward; walking slowly. No labels. " + RULES,
      "את REF_crown_v1 (הכתר בדיוק), ואת REF_rabbi_APPROVED מהמערה כרפרנס לסגנון ולמבנה הדף בלבד")
sheet("REF_prince", "דף 2: הנסיך (בריא וחולה)", STYLE + " " + SHEET +
      "A prince about 12, slender and lively, round face, large hazel eyes, light freckles, short messy dark-brown curls. Healthy outfit: white linen "
      "shirt, turquoise vest with gold thread, dark trousers, soft brown boots, holding a small light-wood flute. Close-ups: laughing with wonder; pale "
      "and weak with eyes closed and shadows under the eyes (sick); eyes slowly opening, whispering; radiant smile with rosy cheeks. Poses: running; "
      "playing the flute; three-quarter; back; lying in bed in a long white nightgown under a blue-and-gold patchwork quilt; sitting up in bed. "
      "No labels. " + RULES,
      "את דף המלך המאושר (לסגנון)")
sheet("REF_doctor_counselor", "דף 3: הרופא הראשי והיועץ", STYLE + " " +
      "Character reference sheet on a clean white background in the render style of the attached sheet: two royal court men, each shown front, "
      "three-quarter and back, plus two close-ups each, with very different silhouettes. A, the chief physician, about 70: short with slightly "
      "rounded shoulders, kind worried eyes behind round gold-rimmed spectacles, round cheeks, long neat white beard to mid-chest, short moustache "
      "with clearly visible lips, long dark-green robe, soft wide green cap, brown leather satchel, an old parchment scroll with no readable text. "
      "Close-ups: focused reading; hesitant sad revelation. B, the counselor, about 45: tall and thin, narrow face, sharp furrowed brows, dark clever "
      "eyes, short pointed black beard, short moustache with clearly visible lips, long burgundy coat with gold buttons, soft black flat-topped hat, "
      "holding a thick ledger with no text. Close-ups: alarmed protest; quiet acceptance, head bowed. No labels. " + RULES,
      "את דף המלך המאושר")
sheet("REF_alter_rebbe", "דף 4: אדמו\"ר הזקן", STYLE + " " + SHEET +
      "The character must closely match the man in the attached traditional portrait, translated into a restrained, dignified, near-realistic Pixar "
      "style with minimal exaggeration: an elderly Chassidic Rebbe who looks about 65, three-quarter face turned to the left, high forehead with deep "
      "horizontal lines, thick white eyebrows slightly raised, large pale deep-set eyes with heavy lower lids and a pensive far-off gaze to the side, "
      "long straight prominent nose, fair skin with rosy cheeks. Very full, long, wide and wavy white beard with a little gray reaching mid-chest, full "
      "white moustache, thick curly white hair puffing out over and around the ears with the sidelocks blended into it. A large soft round black "
      "skullcap set slightly back on the head, no hat over it. Long black frock coat with a high closed collar. Close-ups: the exact pensive gaze of "
      "the portrait; writing by candlelight; quiet prayer with eyes closed; gentle serene relief. Poses: seated at a wooden desk writing with a quill "
      "on loose pages with no readable text; standing at a small barred window in moonlight; stepping out through a doorway into snow; three-quarter "
      "standing; back view; seated reading a manuscript. No labels. " + RULES,
      "**את הציור המסורתי** (לדמיון), ואת דף המלך המאושר (לסגנון בלבד)")
sheet("REF_lineup", "דף 5: השוואת גדלים", STYLE + " " +
      "Lineup of five figures standing side by side on a clean white background, full body, front view, same scale, using the exact characters from "
      "the attached sheets: from left to right the chief physician, the counselor, the prince, the king, the jeweler (about 60, broad, short full gray "
      "beard, jeweler's loupe on one eye, brown leather apron and cap). The king and the counselor are the tallest; the prince reaches the king's chest. "
      "No labels. " + RULES,
      "את הדפים 1–3 המאושרים")
sheet("REF_props", "דף 6: אובייקטים", STYLE + " " +
      "Prop reference sheet on a clean white background: the empty burgundy velvet crown cushion; a small plain gold mortar and pestle with "
      "fine diamond powder glowing like light; a simple crystal goblet of clear water with the powder dissolving into sparkling white-turquoise specks "
      "with gold glints; the same goblet tilted with glowing water spilling over its rim; a single glowing drop of that water, close-up; a thin "
      "stream of the glowing water trickling across a marble step; a small light-wood flute with six holes; an old parchment scroll with blurry lines and no readable text; loose handwritten pages with a quill, ink pot "
      "and a tallow candle, the writing only blurry lines with no readable letters. No labels. " + RULES,
      "את REF_crown_v1 ואת דף המלך המאושר")
sheet("REF_music", "דף 7: האובייקטים המוזיקליים (מנגן מול שותק)", STYLE + " " +
      "Environment element sheet on a clean white background, two rows. Top row, alive and singing: a small ringing spring pool with expanding rings "
      "of light and golden mist; a giant tree whose branches stretch like glowing turquoise harp strings; crystal wind chimes hanging from a white-gold "
      "arch leaving trails of sparkles; tiny glowing musical notes floating like fireflies; bell-shaped flowers glowing in rhythm. Bottom row, the same "
      "five elements silent: frozen gray ice, slack gray strings, still chimes, notes fallen dark in the grass, closed gray flowers. No text, no labels. "
      + RULES, "את דף המלך המאושר")

h2("לוקיישנים: פרומפט לכל אחד")
para("מייצרים כל לוקיישן כתמונה ריקה ברוחב 16:9. כל פרומפט נבנה מ־[STYLE], ואחריו \"Empty establishing shot, no characters:\", התיאור באנגלית ו־[RULES].", size=10)
LOC_EN = {
    "L1": "A wide green valley full of dozens of small ringing springs and thin waterfalls, glowing flowers, a winding stream and blue mountains on the horizon, golden hour, rings of light spreading on the water, tiny glowing notes in the air.",
    "L2": "A forest of giant trees whose branches stretch like glowing turquoise harp strings, firefly-like musical notes between them, slanted sun rays.",
    "L3": "A white-and-gold palace with flat roofs, terraces and arches on a cliff above a sea of clouds, crystal wind chimes on every arch, pink sunset. No pointed towers, no symbols.",
    "L4": "A round throne-less crown hall with a reflective marble floor and pale columns; on a central pedestal a burgundy velvet cushion holding the approved crown from the attached sheet with its huge glowing diamond; one beam of light from above, dust trembling in it.",
    "L5": "A prince's bedroom with a canopy bed and turquoise curtains, a tall window over the valley, shelves with small musical instruments and books; heavy curtain and gray light (sick version).",
    "L6": "A physicians' study with a long wooden table covered in scrolls with no readable text, jars, brass scales and candles, round windows only, warm candlelight and long shadows.",
    "L7": "A wide spiral staircase of white marble with a gold balustrade shaped like waves, winding down from the prince's room to the palace gate; tall arched windows pour golden morning light; a thin stream of glowing white-turquoise water flows down the steps like a small shining waterfall.",
    "L8": "A humble late-18th-century study with a wooden desk, a single tallow candle and loose pages with blurry lines; deep night blue, moonlight through a small barred window; snowy frozen river outside.",
    "L9": "Modern Jerusalem stone rooftops at dusk with warm window lights; a single smartphone screen glowing on a windowsill, tiny white-turquoise light specks rising from it.",
}
for k, v in LOC_EN.items():
    sheet(f"LOC_{k}", f"{k}", STYLE + " Empty establishing shot, no characters: " + v + " " + RULES,
          "את REF_crown_v1 ואת דף המלך המאושר" if k == "L4" else "את דף המלך המאושר (לסגנון)")

h1("7. הצעדים הבאים")
para("1) **אישור דפי הרפרנס:** אחרי שהתמונות נוצרות, עוברים עליהן יחד ומתקנים. כל דף שמאושר מקבל שם APPROVED. "
     "2) **הקריינות:** נוצרת לפי script.txt (שורה = קובץ), ואחר כך timeline.csv ו־shots.csv. "
     "3) **הסטוריבורד:** כל S### מ־shots.csv הופך לתת־סצנה בחמישה שדות, עם פרומפט תמונה שמצרף את הרפרנסים המאושרים.")

out = os.path.join(HERE, f"תנך_היהלום_שבכתר_פיקסאר_v{VERSION}.docx")
doc.save(out)
print(out)

json.dump(PROMPTS, open(os.path.join(HERE, "ref_prompts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"style": STYLE, "rules": RULES}, open(os.path.join(HERE, "style_rules.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
