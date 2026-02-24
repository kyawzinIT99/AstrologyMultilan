"""
Mahabote (မဟာဘုတ်) Astrology Engine

Implements the traditional Myanmar Mahabote astrology system:
- 7 Houses derived from Myanmar Era year
- 8-day weekday system (Wednesday split at noon)
- Planet assignments and personality profiles
- 6-month Do/Don't forecast generation

All interpretations are provided in Myanmar language.
"""

import math
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
from myanmar_calendar import gregorian_to_myanmar, get_myanmar_year, get_weekday_index, MyanmarDate
from translations import CHAT, READING_LABELS, PROMO, FORECAST_EN, MONTH_MODIFIERS_EN


# ─── 8-Day Weekday System ────────────────────────────────────────────────────
# Mahabote uses 8 days: Wednesday is split into morning (Mercury) and afternoon (Rahu)

EIGHT_DAY_WEEK = {
    # weekday_index (from myanmar_calendar): {name_mm, name_en, planet_mm, planet_en, animal_mm, direction_mm, planet_id}
    # myanmar_calendar weekday: 0=Sat, 1=Sun, 2=Mon, 3=Tue, 4=Wed, 5=Thu, 6=Fri
    # traditional planet IDs: Sun=1, Mon=2, Tue=3, Wed=4, Thu=5, Fri=6, Sat=0, Rahu=7
    0: {"name_mm": "စနေ", "name_en": "Saturday", "planet_mm": "စနေဂြိုဟ်", "planet_en": "Saturn",
        "animal_mm": "နဂါး", "animal_en": "Dragon/Naga", "direction_mm": "အနောက်တောင်", "direction_en": "Southwest", "planet_id": 0},
    1: {"name_mm": "တနင်္ဂနွေ", "name_en": "Sunday", "planet_mm": "နေဂြိုဟ်", "planet_en": "Sun",
        "animal_mm": "ဂဠုန်", "animal_en": "Garuda", "direction_mm": "အရှေ့မြောက်", "direction_en": "Northeast", "planet_id": 1},
    2: {"name_mm": "တနင်္လာ", "name_en": "Monday", "planet_mm": "လဂြိုဟ်", "planet_en": "Moon",
        "animal_mm": "ကျား", "animal_en": "Tiger", "direction_mm": "အရှေ့", "direction_en": "East", "planet_id": 2},
    3: {"name_mm": "အင်္ဂါ", "name_en": "Tuesday", "planet_mm": "အင်္ဂါဂြိုဟ်", "planet_en": "Mars",
        "animal_mm": "ခြင်္သေ့", "animal_en": "Lion", "direction_mm": "အရှေ့တောင်", "direction_en": "Southeast", "planet_id": 3},
    4: {"name_mm": "ဗုဒ္ဓဟူး", "name_en": "Wednesday", "planet_mm": "ဗုဒ္ဓဂြိုဟ်", "planet_en": "Mercury",
        "animal_mm": "ဆင်(အစွယ်ရှိ)", "animal_en": "Tusked Elephant", "direction_mm": "တောင်", "direction_en": "South", "planet_id": 4},
    5: {"name_mm": "ကြာသပတေး", "name_en": "Thursday", "planet_mm": "ကြာသပတေးဂြိုဟ်", "planet_en": "Jupiter",
        "animal_mm": "ကြွက်", "animal_en": "Rat", "direction_mm": "အနောက်", "direction_en": "West", "planet_id": 5},
    6: {"name_mm": "သောကြာ", "name_en": "Friday", "planet_mm": "သောကြာဂြိုဟ်", "planet_en": "Venus",
        "animal_mm": "ပူးဂဗ်", "animal_en": "Guinea Pig", "direction_mm": "မြောက်", "direction_en": "North", "planet_id": 6},
    # Rahu = Wednesday afternoon
    7: {"name_mm": "ရာဟု", "name_en": "Rahu (Wed PM)", "planet_mm": "ရာဟုဂြိုဟ်", "planet_en": "Rahu",
        "animal_mm": "ဆင်(အစွယ်မဲ့)", "animal_en": "Tuskless Elephant", "direction_mm": "အနောက်မြောက်", "direction_en": "Northwest", "planet_id": 7},
}


# ─── 7 Houses of Mahabote ────────────────────────────────────────────────────
# Traditional sequence: Binga, Puti, Yarza, Ahtun, Thike, Marana, Adhipati

HOUSES = {
    0: {
        "id": "binga",
        "name_mm": "ဘင်္ဂအိမ်",
        "name_en": "Binga",
        "nature": "Impermanence/Change",
        "personality_mm": (
            "ဗင်္ဂအိမ်ဖွား ပုဂ္ဂိုလ်များသည် လွတ်လပ်မှုကို နှစ်သက်ပြီး စိတ်ဓာတ်တွင် "
            "မတည်ငြိမ်မှုများ ရှိတတ်ပါသည်။ ကျန်းမာရေးနှင့် ချမ်းသာကြွယ်ဝမှု "
            "အတက်အကျ ရှိတတ်ပြီး ဘဝနောက်ပိုင်းတွင် ဆရာအတတ်ပညာဖြင့် "
            "အောင်မြင်တတ်ပါသည်။ စိတ်ရှည်သည်းခံမှုနှင့် တည်ငြိမ်မှုကို "
            "လေ့ကျင့်ရန် လိုအပ်ပါသည်။"
        ),
        "personality_en": (
            "People born in the House of Impermanence (Binga) value independence and may "
            "experience nervous tension. Health and wealth tend to fluctuate. Success often "
            "comes later in life, especially in teaching and mentoring roles."
        ),
        "strengths_mm": ["စိတ်ဓာတ်ကြံ့ခိုင်မှု", "အလုပ်ကြိုးစားမှု", "ဆရာအတတ်ပညာ"],
        "strengths_en": ["Mental Strength", "Hardworking", "Teaching"],
        "weaknesses_mm": ["စိတ်မတည်ငြိမ်မှု", "ငွေကြေးအတက်အကျ", "စိတ်ပူပန်မှု"],
    },
    1: {
        "id": "puti",
        "name_mm": "ပုတိအိမ်",
        "name_en": "Puti",
        "nature": "Decomposition/Impurity",
        "personality_mm": (
            "ပုတိအိမ်ဖွား ပုဂ္ဂိုလ်များသည် ကျန်းမာရေး စိန်ခေါ်မှုများ "
            "ကြုံတွေ့ရတတ်ပြီး ကိုယ်ခန္ဓာ၊ စိတ်ပိုင်း သို့မဟုတ် "
            "စိတ်ခံစားချက်ပိုင်း ဒုက္ခများ ရှိတတ်ပါသည်။ "
            "ဂုဏ်သိက္ခာကို ထိန်းသိမ်းရန် အထူးဂရုစိုက်ရန် လိုအပ်ပြီး "
            "သမာဓိရှိရှိ နေထိုင်ခြင်းဖြင့် အောင်မြင်နိုင်ပါသည်။"
        ),
        "personality_en": (
            "House of Reputation/Impurity (Puti) natives may face scrutiny or physical stress. "
            "Maintaining integrity and health is their primary life lesson. They have deep hidden wisdom."
        ),
        "strengths_mm": ["ခံနိုင်ရည်ရှိမှု", "နက်နဲသောဉာဏ်", "သမာဓိ"],
        "strengths_en": ["Endurance", "Deep Wisdom", "Integrity"],
        "weaknesses_mm": ["ကျန်းမာရေးပြဿနာ", "အတင်းအဖျင်းခံရမှု", "စိတ်ဖိစီးမှု"],
    },
    2: {
        "id": "thike",
        "name_mm": "သိုက်အိမ်",
        "name_en": "Thike",
        "nature": "Treasure/Wealth",
        "personality_mm": (
            "သိုက်အိမ်ဖွား ပုဂ္ဂိုလ်များသည် မိသားစုနှင့် ငွေရေးကြေးရေးကို "
            "တန်ဖိုးထားသူများ ဖြစ်ကြသည်။ လုံခြုံမှုကို နှစ်သက်ပြီး "
            "စုဆောင်းတတ်သော အလေ့အကျင့် ရှိပါသည်။ မိသားစု အမွေအနှစ်ကို ထိန်းသိမ်းသူများ ဖြစ်သည်။"
        ),
        "personality_en": (
            "Born in the House of Accumulation/Treasure (Thike), you value security and family. "
            "You are a natural steward of resources and deeply connected to your roots."
        ),
        "strengths_mm": ["ငွေစုဆောင်းနိုင်မှု", "မိသားစုကိုတန်ဖိုးထားမှု", "တည်ငြိမ်မှု"],
        "strengths_en": ["Saving Ability", "Family Values", "Stability"],
        "weaknesses_mm": ["စိုးရိမ်ပူပန်မှု", "အစွဲအလမ်းကြီးမှု"],
    },
    3: {
        "id": "marana",
        "name_mm": "မရဏအိမ်",
        "name_en": "Marana",
        "nature": "Death/Transformation",
        "personality_mm": (
            "မရဏအိမ်ဖွား ပုဂ္ဂိုလ်များသည် ဘဝတွင် စုန်ချီတက်ချီ "
            "အပြင်းအထန် ကြုံတွေ့ရတတ်သော်လည်း နက်နဲသော ဉာဏ်ပညာ "
            "ရရှိသူများ ဖြစ်သည်။ အစွန်းရောက်တတ်သော သဘောရှိပြီး "
            "ဝိညာဉ်ရေးရာတွင် ထူးချွန်တတ်ပါသည်။"
        ),
        "personality_en": (
            "House of Transformation/Death (Marana) natives face steep life lessons. They live "
            "on the edge but possess remarkable depth. Surviving challenges brings them unique wisdom."
        ),
        "strengths_mm": ["ခံနိုင်ရည်ရှိမှု", "နက်နဲသောအမြင်", "ဝိညာဉ်ရေး"],
        "strengths_en": ["Endurance", "Deep Insight", "Spirituality"],
        "weaknesses_mm": ["ကျန်းမာရေးအန္တရာယ်", "စိတ်ဖိစီးမှု", "ဆုံးရှုံးလွယ်မှု"],
    },
    4: {
        "id": "adhipati",
        "name_mm": "အဓိပတိအိမ်",
        "name_en": "Adhipati",
        "nature": "Supreme Ruler",
        "personality_mm": (
            "အဓိပတိအိမ်ဖွား ပုဂ္ဂိုလ်များသည် အာဏာနှင့် လုပ်ပိုင်ခွင့်ကို "
            "ရရှိတတ်သူများ ဖြစ်သည်။ တာဝန်ယူမှု မြင့်မားပြီး "
            "လူအများကို စီမံခန္ဓဲမှု အရည်အချင်းရှိသူများ ဖြစ်တတ်ပါသည်။"
        ),
        "personality_en": (
            "House of Supreme Power (Adhipati) natives are natural leaders and managers. "
            "They command respect and take on heavy responsibilities with ease, often reaching the top."
        ),
        "strengths_mm": ["အာဏာ", "စီမံခန့်ခွဲမှု", "ပြတ်သားမှု"],
        "strengths_en": ["Power", "Management", "Decisiveness"],
        "weaknesses_mm": ["မာနကြီးမှု", "တင်းကျပ်မှု"],
    },
    5: {
        "id": "yarza",
        "name_mm": "ရာဇအိမ်",
        "name_en": "Yarza",
        "nature": "Nobility/King",
        "personality_mm": (
            "ရာဇအိမ်ဖွား ပုဂ္ဂိုလ်များသည် ရိုသေလေးစားမှု ရှိပြီး "
            "ခေါင်းဆောင်မှု အရည်အချင်းရှိသူများ ဖြစ်တတ်ပါသည်။ "
            "ရက်ရောလောင်းလှဲမှုနှင့် ရည်မှန်းချက်မြင့်မားမှု ရှိပြီး "
            "ချမ်းသာကြွယ်ဝမှုကို ဆွဲဆောင်နိုင်စွမ်း ရှိပါသည်။"
        ),
        "personality_en": (
            "House of Wealth/Nobility (Yarza) natives are respected, logical, and often lead others. "
            "They attract success through dignity and exert a natural influence on their surroundings."
        ),
        "strengths_mm": ["ဂုဏ်သိက္ခာ", "ရက်ရောမှု", "ခေါင်းဆောင်မှု"],
        "strengths_en": ["Dignity", "Generosity", "Leadership"],
        "weaknesses_mm": ["မာနကြီးမှု", "လွှမ်းမိုးလိုမှု"],
    },
    6: {
        "id": "ahtun",
        "name_mm": "အထွန်းအိမ်",
        "name_en": "Ahtun",
        "nature": "Brilliance/Exaltation",
        "personality_mm": (
            "အထွန်းအိမ်ဖွား ပုဂ္ဂိုလ်များသည် စွန့်ဦးထွင်သူများ ဖြစ်တတ်ပြီး "
            "ဘဝတွင် အောင်မြင်မှုများကို လွယ်ကူစွာ ရရှိတတ်ပါသည်။ "
            "ထက်မြက်ဖျတ်လတ်ပြီး တီထွင်ဖန်တီးနိုင်စွမ်း ရှိပါသည်။"
        ),
        "personality_en": (
            "House of Success/Exaltation (Ahtun) natives are pioneers. They achieve brilliance "
            "through creativity and quick thinking, often rising rapidly in their chosen fields."
        ),
        "strengths_mm": ["တီထွင်ဖန်တီးနိုင်မှု", "အောင်မြင်မှု", "ထက်မြက်မှု"],
        "strengths_en": ["Creativity", "Success", "Intelligence"],
        "weaknesses_mm": ["စိတ်မြန်လက်မြန်ဖြစ်မှု", "ပေါ့ဆမှု"],
    },
}


# ─── 6-Month Forecast Rules ──────────────────────────────────────────────────
# Rules updated for traditional mapping indices

FORECAST_RULES = {
    0: {  # Binga
        "do_mm": [
            "တရားထိုင်ခြင်းနှင့် စိတ်ငြိမ်သက်မှု ရှာဖွေပါ",
            "ငွေကြေးစုဆောင်းပြီး ချွေတာပါ",
            "ပညာသင်ကြားပေးခြင်း လုပ်ပါ",
            "ကျန်းမာရေး စစ်ဆေးမှု ခံယူပါ",
            "ရေရှည် ရင်းနှီးမြှုပ်နှံမှု ပြုလုပ်ပါ",
            "မိသားစု ဆက်ဆံရေး ခိုင်မြဲအောင် ထိန်းသိမ်းပါ",
        ],
        "dont_mm": [
            "ရေတိုလောင်းကစားမှု ရှောင်ကြဉ်ပါ",
            "အလွန်အကျွံ သုံးစွဲခြင်း မပြုပါနှင့်",
            "စနေနေ့တွင် ခရီးအဝေးမသွားပါနှင့်",
            "စိတ်လိုက်မာန်ပါ ဆုံးဖြတ်ချက်များ မချပါနှင့်",
            "ငွေချေးခြင်း ရှောင်ကြဉ်ပါ",
            "အငြင်းအခုံ ရှောင်ကြဉ်ပါ",
        ],
    },
    1: {  # Puti
        "do_mm": [
            "ကျန်းမာရေးကို အထူးဂရုစိုက်ပါ",
            "သမာဓိရှိရှိ နေထိုင်ပါ",
            "ဘာသာရေး ကုသိုလ် ပြပါ",
            "နှိမ့်ချစွာ ဆက်ဆံပါ",
            "အတွင်းစိတ် ငြိမ်းချမ်းမှုကို ရှာပါ",
            "ပညာရှာမှီးပါ",
        ],
        "dont_mm": [
            "အတင်းအဖျင်း ပြောခြင်း ရှောင်ပါ",
            "ကျန်းမာရေး ထိခိုက်မည့် အလုပ်များ ရှောင်ပါ",
            "ဒေါသထွက်ခြင်း ရှောင်ပါ",
            "မောဟဖုံးလွှမ်းသော အလုပ်များ ရှောင်ပါ",
            "လိမ်လည်မှု ရှောင်ပါ",
            "ရန်ဖြစ်ခြင်း ရှောင်ပါ။",
        ],
    },
    2: {  # Thike
        "do_mm": [
            "မိသားစုရေးရာများ ဂရုစိုက်ပါ",
            "ငွေစုဆောင်းမှု အသစ်စတင်ပါ",
            "ရှေးဟောင်းပစ္စည်းများ သို့မဟုတ် အမွေအနှစ်များ ထိန်းသိမ်းပါ",
            "အလှူအတန်း ပြုလုပ်ပါ",
            "ဘာသာရေး လုပ်ငန်းများတွင် ပါဝင်ပါ",
            "နေအိမ် ပြင်ဆင်မှုများ လုပ်ပါ",
        ],
        "dont_mm": [
            "တနင်္လာနေ့တွင် အနောက်ဘက် ခရီးမသွားပါနှင့်",
            "အမွေအနှစ်များ အလွယ်တကူ မရောင်းပါနှင့်",
            "မိသားစုဝင်များနှင့် စိတ်ဝမ်းကွဲခြင်း ရှောင်ပါ",
            "ရန်လိုမှု ထိန်းချုပ်ပါ",
            "အဓိပ္ပာယ်မဲ့ အသုံးစရိတ်များ ရှောင်ပါ",
        ],
    },
    3: {  # Marana
        "do_mm": [
            "တရားထိုင်ခြင်းနှင့် ဝိပဿနာ ကျင့်ကြံပါ",
            "ကျန်းမာရေးကို အထူးဂရုစိုက်ပါ",
            "ဘဝအပြောင်းအလဲများကို လက်ခံပါ",
            "ကုသိုလ်ကောင်းမှု များများလုပ်ပါ",
            "အေးဆေးစွာ နေထိုင်ပါ",
            "စိတ်ကို တည်ငြိမ်အောင် ထားပါ",
        ],
        "dont_mm": [
            "သောကြာနေ့တွင် ခရီးအဝေးမသွားပါနှင့်",
            "အစွန်းရောက်သော ဆုံးဖြတ်ချက်များ မချပါနှင့်",
            "အန္တရာယ်ရှိသော အလုပ်များ ရှောင်ပါ",
            "အမှားဟောင်းများ ပြန်မလုပ်မိပါစေနှင့်",
            "စိတ်လှုပ်ရှားဖွယ်ရာများ ရှောင်ပါ",
        ],
    },
    4: {  # Adhipati
        "do_mm": [
            "စီမံခန့်ခွဲမှု အသစ်များ လုပ်ကိုင်ပါ",
            "ခေါင်းဆောင်မှု နေရာကို ရယူပါ",
            "လုပ်ငန်းသစ်များ စတင်ပါ",
            "လူအများနှင့် ပူးပေါင်း ဆောင်ရွက်ပါ",
            "ပြတ်သားစွာ ဆုံးဖြတ်ပါ",
            "အောင်မြင်မှုကို ခံစားပါ",
        ],
        "dont_mm": [
            "ကြာသပတေးနေ့တွင် တောင်ဘက် ခရီးမသွားပါနှင့်",
            "မာနထောင်လွှားခြင်း ရှောင်ပါ",
            "တင်းကျပ်လွန်းသော စည်းကမ်းများ မထားပါနှင့်",
            "အာဏာရှင်ဆန်မှု ရှောင်ပါ",
            "တပါးသူ၏ အခွင့်အရေးကို မပိတ်ပင်ပါနှင့်",
        ],
    },
    5: {  # Yarza
        "do_mm": [
            "ရဲရင့်စွာ ဆုံးဖြတ်ပါ",
            "ကိုယ်ကာယ လေ့ကျင့်ခန်း လုပ်ပါ",
            "ဘာသာရေး ကုသိုလ် ပြပါ",
            "ရင်းနှီးမြှုပ်နှံမှု လုပ်ကိုင်ပါ",
            "အိမ်ခြံမြေ ကိစ္စများ ဆောင်ရွက်ပါ",
            "ခေါင်းဆောင်ဖြစ်ရန် ကြိုးစားပါ",
        ],
        "dont_mm": [
            "အင်္ဂါနေ့တွင် ထက်ရှသော လက်နက် ကိုင်တွယ်ခြင်း ရှောင်ကြဉ်ပါ",
            "ဒေါသထွက်ခြင်း ရှောင်ကြဉ်ပါ",
            "စစ်ခင်းခြင်းနှင့် ပဋိပက္ခ ရှောင်ကြဉ်ပါ",
            "မီးဘေး သတိထားပါ",
            "အလွန်အကျွံ စွန့်စားခြင်း ရှောင်ကြဉ်ပါ",
            "ရန်လိုမှု ထိန်းချုပ်ပါ",
        ],
    },
    6: {  # Ahtun
        "do_mm": [
            "ခေါင်းဆောင်မှု စွမ်းရည်ကို ဖော်ထုတ်ပါ",
            "ပရဟိတ လှူဒါန်းပါ",
            "ကိုယ်ကာယ ကျန်းမာရေး ဂရုစိုက်ပါ",
            "အသစ်အဆန်း စွန့်စားလုပ်ကိုင်ပါ",
            "ယုံကြည်မှုရှိစွာ ဆုံးဖြတ်ပါ",
            "အားကစား လေ့ကျင့်ပါ",
        ],
        "dont_mm": [
            "တနင်္ဂနွေနေ့တွင် အရှေ့ဘက် ခရီးမသွားပါနှင့်",
            "အစွန်းရောက်သော ဆုံးဖြတ်ချက်များ ရှောင်ကြဉ်ပါ",
            "ကျော်ကြားလိုစိတ်ကို ထိန်းချုပ်ပါ",
            "အလျင်စလို ဆုံးဖြတ်ချက်များ မချပါနှင့်",
            "ဘဝင်မြင့်ခြင်း ရှောင်ပါ",
        ],
    },
}

# Monthly seasonal modifiers for forecast richness (kept here for backward compat)
# English versions are in translations.py
MONTH_MODIFIERS_MM = [
    "ဤလတွင် စိတ်အားထက်သန်မှု ပိုမိုရရှိမည်",      # Month 1
    "ဤလတွင် ငွေကြေးကံ ပွင့်လန်းမည်",               # Month 2
    "ဤလတွင် ဆက်ဆံရေး ပိုမိုခိုင်မြဲမည်",            # Month 3
    "ဤလတွင် အလုပ်အကိုင် အခွင့်အလမ်း ရရှိမည်",     # Month 4
    "ဤလတွင် ကျန်းမာရေး အထူးဂရုစိုက်ရန် လိုအပ်မည်", # Month 5
    "ဤလတွင် ပညာရေးနှင့် သုတေသန ကံကောင်းမည်",       # Month 6
]


# ─── Main Engine Class ────────────────────────────────────────────────────────
@dataclass
class MahaboteReading:
    """Complete Mahabote astrology reading for a person."""
    name: str
    birth_date: datetime
    is_wednesday_pm: bool
    myanmar_date: MyanmarDate
    myanmar_year: int
    house_index: int
    house: dict
    birth_day: dict
    forecast_rules: dict
    year_remainder: int = 0
    current_age: int = 0
    current_myanmar_year: int = 0
    current_year_house: dict = field(default_factory=dict)

    @property
    def house_remainder(self) -> int:
        return self.house_index


class MahaboteEngine:
    """Mahabote Astrology calculation engine."""

    def calculate(
        self,
        name: str,
        birth_year: int,
        birth_month: int,
        birth_day: int,
        is_wednesday_pm: bool = False,
    ) -> MahaboteReading:
        """
        Compute a full Mahabote reading for a person with correct traditional house placement.
        """
        # Get Myanmar calendar data
        mm_date = gregorian_to_myanmar(birth_year, birth_month, birth_day)
        my_year = mm_date.myanmar_year
        remainder = my_year % 7

        # 8-day weekday and Birth Planet
        wd = mm_date.weekday  # 0=Sat, 1=Sun, 2=Mon, 3=Tue, 4=Wed, 5=Thu, 6=Fri
        if wd == 4 and is_wednesday_pm:
            birth_day_info = EIGHT_DAY_WEEK[7]  # Rahu
        else:
            birth_day_info = EIGHT_DAY_WEEK[wd]
        
        # Traditional Chart Planet ID (Sat=0, Sun=1... Venus=6)
        # Rahu (7) behaves like Mercury (4) in the 7-house chart layout
        chart_planet = birth_day_info["planet_id"]
        chart_planet_for_layout = 4 if chart_planet == 7 else chart_planet

        # The 8-Planet cycle for Thet-Yauk rotation (Age movement)
        # 1: Sun, 2: Mon, 3: Tue, 4: Wed, 0: Sat, 5: Thu, 7: Rahu (Wed PM), 6: Fri
        planet_cycle = [1, 2, 3, 4, 0, 5, 7, 6]

        # Birth House Index (Traditional 7-house sequence: Binga=0... Adhipati=6)
        # Equation: (Planet - YearRemainder) % 7
        house_index = (chart_planet_for_layout - remainder) % 7
        house = HOUSES[house_index]

        # Age and Current Year (Thet-Yauk)
        now = datetime.now()
        current_mm_date = gregorian_to_myanmar(now.year, now.month, now.day)
        current_myanmar_year = current_mm_date.myanmar_year
        current_my_remainder = current_myanmar_year % 7
        
        # Current Age in traditional count (year inclusive)
        current_age = current_myanmar_year - my_year + 1
        
        # Current Year Planet (Rotates according to the 8-planet cycle)
        try:
            birth_planet_idx = planet_cycle.index(chart_planet)
            current_planet_idx = (birth_planet_idx + current_age - 1) % 8
            current_planet_id = planet_cycle[current_planet_idx]
            # In the 7-house chart layout, Rahu (7) behaves like Mercury (4)
            current_planet_for_chart = 4 if current_planet_id == 7 else current_planet_id
        except ValueError:
            current_planet_for_chart = chart_planet_for_layout
        
        # Current Year House Index (Relative to Current Year Chart)
        current_year_house_index = (current_planet_for_chart - current_my_remainder) % 7
        current_year_house = HOUSES[current_year_house_index]

        return MahaboteReading(
            name=name,
            birth_date=datetime(birth_year, birth_month, birth_day),
            is_wednesday_pm=is_wednesday_pm,
            myanmar_date=mm_date,
            myanmar_year=my_year,
            house_index=house_index,
            house=house,
            birth_day=birth_day_info,
            forecast_rules=FORECAST_RULES[current_year_house_index],
            year_remainder=remainder,
            current_age=current_age,
            current_myanmar_year=current_myanmar_year,
            current_year_house=current_year_house,
        )

    def generate_6month_forecast(self, reading: MahaboteReading, lang: str = "my") -> list:
        """
        Generate a 6-month forecast with Do/Don't guidance.
        Returns a list of monthly forecast dicts.
        """
        forecasts = []
        now = datetime.now()

        # Get the correct house index for forecast lookup
        house_idx = None
        for idx, house in HOUSES.items():
            if house == reading.current_year_house:
                house_idx = idx
                break
        if house_idx is None:
            house_idx = 0

        # Get English forecast rules from translations
        en_rules = FORECAST_EN.get(house_idx, {})
        en_do = en_rules.get("do_en", [])
        en_dont = en_rules.get("dont_en", [])

        for i in range(6):
            target_date = now + timedelta(days=i * 30)
            month_name = self._get_myanmar_month_name(target_date)
            year_str = str(target_date.year)

            # Rotate through Do/Don't items for variety
            do_idx = i % len(reading.forecast_rules["do_mm"])
            dont_idx = i % len(reading.forecast_rules["dont_mm"])

            entry = {
                "month_mm": month_name,
                "year": year_str,
                "month_en": target_date.strftime("%B %Y"),
                "do_mm": reading.forecast_rules["do_mm"][do_idx],
                "dont_mm": reading.forecast_rules["dont_mm"][dont_idx],
                "modifier_mm": MONTH_MODIFIERS_MM[i],
            }

            # Add English equivalents
            if en_do:
                entry["do_en"] = en_do[i % len(en_do)]
            else:
                entry["do_en"] = entry["do_mm"]
            if en_dont:
                entry["dont_en"] = en_dont[i % len(en_dont)]
            else:
                entry["dont_en"] = entry["dont_mm"]
            entry["modifier_en"] = MONTH_MODIFIERS_EN[i] if i < len(MONTH_MODIFIERS_EN) else ""

            forecasts.append(entry)

        return forecasts

    def get_greeting_message(self, lang: str = "my") -> str:
        """Bot greeting in selected language."""
        return CHAT[lang]["greeting"]

    def get_dob_prompt(self, name: str, lang: str = "my") -> str:
        """Ask for date of birth in selected language."""
        return CHAT[lang]["ask_dob"].format(name=name)

    def get_wednesday_prompt(self, lang: str = "my") -> str:
        """Ask about Wednesday birth time in selected language."""
        return CHAT[lang]["ask_wednesday"]

    def format_reading(self, reading: MahaboteReading, lang: str = "my") -> str:
        """Format a full Mahabote reading in the selected language."""
        house = reading.house
        bd = reading.birth_day
        md = reading.myanmar_date
        L = READING_LABELS[lang]

        # Choose name suffixes based on language
        if lang == "en":
            house_display = house['name_en']
            current_house_display = f"{reading.current_year_house['name_en']} ({reading.current_year_house['nature']})"
            day_display = f"{bd['name_en']} ({bd['planet_en']})"
            planet_display = f"{bd['planet_en']}"
            animal_display = f"{bd['animal_en']}"
            direction_display = bd.get('direction_en', bd['direction_mm'])
            personality = house.get('personality_en', house['personality_mm'])
            strengths = house.get('strengths_en', house.get('strengths_mm', []))
        else:
            house_display = f"{house['name_mm']} ({house['name_en']})"
            current_house_display = f"{reading.current_year_house['name_mm']} ({reading.current_year_house['name_en']})"
            day_display = f"{bd['name_mm']} ({bd['name_en']})"
            planet_display = f"{bd['planet_mm']} ({bd['planet_en']})"
            animal_display = f"{bd['animal_mm']} ({bd['animal_en']})"
            direction_display = bd['direction_mm']
            personality = house['personality_mm']
            strengths = house.get('strengths_mm', [])

        lines = [
            L["title"].format(name=reading.name),
            "",
            "═══════════════════════════════════════",
            f"{L['birth_date']}: {reading.birth_date.strftime('%Y-%m-%d')}",
            f"{L['myanmar_date']}: {md.display}",
            f"{L['myanmar_era']}: {reading.myanmar_year} {L['era_suffix'].format(r=reading.year_remainder)}",
            f"{L['current_age']}: {L['age_format'].format(age=reading.current_age, year=reading.current_myanmar_year)}",
            f"{L['current_fortune']}: {current_house_display}",
            f"{L['moon_phase']}: {md.moon_phase_name}",
            "",
            "═══════════════════════════════════════",
            f"{L['house_label']}: {house_display}",
            f"{L['house_index']}: {reading.house_remainder}",
            f"{L['nature_label']}: {house['nature']}",
            "",
            "═══════════════════════════════════════",
            f"{L['birth_day_label']}: {day_display}",
            f"{L['planet_label']}: {planet_display}",
            f"{L['animal_label']}: {animal_display}",
            f"{L['direction_label']}: {direction_display}",
            "",
            "═══════════════════════════════════════",
            L["personality"],
            "",
            personality,
            "",
            L["strengths"],
        ]
        for s in strengths:
            lines.append(f"  ✅ {s}")

        lines.append("")
        lines.append("═══════════════════════════════════════")

        return "\n".join(lines)

    def format_forecast(self, reading: MahaboteReading, lang: str = "my") -> str:
        """Format the 6-month forecast in the selected language."""
        forecasts = self.generate_6month_forecast(reading, lang=lang)
        L = READING_LABELS[lang]

        if lang == "en":
            current_house_display = f"{reading.current_year_house['name_en']} ({reading.current_year_house['nature']})"
            birth_house_display = f"{reading.house['name_en']} ({reading.house['nature']})"
        else:
            current_house_display = f"{reading.current_year_house['name_mm']} ({reading.current_year_house['name_en']})"
            birth_house_display = f"{reading.house['name_mm']} ({reading.house['name_en']})"

        lines = [
            L["forecast_title"].format(name=reading.name),
            L["forecast_age"].format(age=reading.current_age, year=reading.current_myanmar_year),
            f"{L['forecast_fortune']}: {current_house_display}",
            f"{L['forecast_house']}: {birth_house_display}",
            "",
            "═══════════════════════════════════════",
        ]

        suffix = "_en" if lang == "en" else "_mm"
        for f in forecasts:
            lines.extend([
                "",
                f"🗓️ **{f['month_en']}**",
                f"💫 {f['modifier' + suffix]}",
                f"{L['do_label']}: {f['do' + suffix]}",
                f"{L['dont_label']}: {f['dont' + suffix]}",
            ])

        lines.extend([
            "",
            "═══════════════════════════════════════",
        ])

        return "\n".join(lines)


    @staticmethod
    def _get_myanmar_month_name(dt: datetime) -> str:
        """Approximate Myanmar month name from Gregorian date."""
        names = [
            "ပြာသိုလ", "တပို့တွဲလ", "တပေါင်းလ", "တန်ခူးလ",
            "ကဆုန်လ", "နယုန်လ", "ဝါဆိုလ", "ဝါခေါင်လ",
            "တော်သလင်းလ", "သီတင်းကျွတ်လ", "တန်ဆောင်မုန်းလ", "နတ်တော်လ",
        ]
        # Offset is usually 3 months back (e.g. Apr is 1st month Tagu)
        idx = (dt.month - 1) % 12
        return names[idx]


# ─── Self-Test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    engine = MahaboteEngine()

    # Test with Su Mon Myint Oo known case
    # Oct 10, 1978 = Tuesday (3) in 1340 ME
    reading = engine.calculate("Su Mon Myint Oo", 1978, 10, 10)
    print(engine.format_reading(reading))
    print()
    print(engine.format_forecast(reading))
