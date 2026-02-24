"""
Multi-Language Translation Module for Myanmar Astrology Chatbot.

Provides all UI strings and chat prompts in Myanmar (my) and English (en).
Only covers Maharbot astrology features — booking/admin/tarot remain Myanmar-only.
"""

SUPPORTED_LANGS = ["my", "en"]
DEFAULT_LANG = "my"


# ── Chat Prompts ─────────────────────────────────────────────
CHAT = {
    "my": {
        "greeting": (
            "🔮 မင်္ဂလာပါ! **Su Mon Myint Oo မဟာဘုတ် ဗေဒင် & Tarot** မှ ကြိုဆိုပါတယ်။\n\n"
            "သင့်ရဲ့ မွေးနေ့ ဗေဒင် ဟောစာတမ်း ပြုစုပေးပါမယ်။\n"
            "ကျေးဇူးပြု၍ သင့်ရဲ့ **အမည်** ကို ရိုက်ထည့်ပေးပါ။ 🙏"
        ),
        "ask_name": "ကျေးဇူးပြု၍ သင့်ရဲ့ အမည်ကို ရိုက်ထည့်ပေးပါ။ 🙏",
        "ask_dob": (
            "ကျေးဇူးတင်ပါတယ် **{name}** ရှင့်!\n\n"
            "သင့်ရဲ့ **မွေးနေ့ရက်စွဲ** ကို ပေးပါ။\n"
            "ဥပမာ - `1990-05-15` (နှစ်-လ-ရက်) ပုံစံဖြင့် ရိုက်ထည့်ပေးပါ။ 📅"
        ),
        "invalid_date": (
            "❌ ရက်စွဲ ပုံစံ မမှန်ပါ။\n\n"
            "ကျေးဇူးပြု၍ `YYYY-MM-DD` ပုံစံဖြင့် ထပ်မံ ရိုက်ထည့်ပေးပါ။\n"
            "ဥပမာ: `1990-05-15` 📅"
        ),
        "ask_wednesday": (
            "သင် **ဗုဒ္ဓဟူးနေ့** ဖွားဖြစ်ပါတယ်!\n\n"
            "မဟာဘုတ် ဗေဒင်တွင် ဗုဒ္ဓဟူးနေ့ကို နှစ်ပိုင်း ခွဲပါတယ်:\n"
            "• **နံနက်** (မွန်းတည့်မတိုင်မီ) = ဗုဒ္ဓဂြိုဟ်\n"
            "• **ညနေ** (မွန်းတည့်ပြီးနောက်) = ရာဟုဂြိုဟ်\n\n"
            "သင် **နံနက်** ဖွားလား၊ **ညနေ** ဖွားလား?\n"
            "(`နံနက်` သို့မဟုတ် `ညနေ` ဟု ရိုက်ထည့်ပေးပါ) ⏰"
        ),
        "wednesday_invalid": (
            "ကျေးဇူးပြု၍ `နံနက်` (morning) သို့မဟုတ် `ညနေ` (afternoon) "
            "ဟု ရိုက်ထည့်ပေးပါ။ ⏰"
        ),
        "calc_error": "❌ တွက်ချက်ရာတွင် အမှားရှိပါသည်: {error}\nကျေးဇူးပြု၍ ထပ်မံ ကြိုးစားပါ။",
        "forecast_done": (
            "၆ လ ဟောစာတမ်းကို ပြသပေးခဲ့ပြီး ဖြစ်ပါတယ်။\n\n"
            "ပိုမိုတိကျသော Tarot မေးခွန်းများ မေးမြန်းရန် ရက်ချိန်း ယူနိုင်ပါသည်:\n"
            "👉 **[Tarot ရက်ချိန်း ယူရန် နှိပ်ပါ](/booking)** 🙏"
        ),
        "thank_response": (
            "ရပါတယ်ရှင်၊ အချိန်မရွေး ထပ်မံ မေးမြန်းနိုင်ပါတယ်။\n\n"
            "👉 **[Tarot ရက်ချိန်း ယူရန် နှိပ်ပါ](/booking)** 🙏"
        ),
        "other_response": (
            "👉 **[Tarot ရက်ချိန်း ယူရန် နှိပ်ပါ](/booking)**\n\n"
            "အခြား မေးခွန်း ရှိပါက မေးမြန်းနိုင်ပါတယ်။ 🙏"
        ),
        "booking_link": (
            "📅 **Tarot ရက်ချိန်း** ယူရန် အောက်ပါ link ကို နှိပ်ပါ:\n\n"
            "👉 [ရက်ချိန်း ယူရန်](/booking)\n\n"
            "Su Mon Myint Oo နှင့် ဗေဒင် တိုက်ရိုက် ဆွေးနွေးနိုင်ပါမည်။ 🔮"
        ),
        "refresh": "🙏 ကျေးဇူးပြု၍ ထပ်မံ စတင်ရန် စာမျက်နှာကို refresh လုပ်ပါ။",
        "server_error": "❌ ဆာဗာနှင့် ချိတ်ဆက်၍ မရပါ။ ထပ်မံကြိုးစားပါ။",
        "generic_error": "❌ တစ်စုံတစ်ခု မှားယွင်းနေပါသည်။ ထပ်မံကြိုးစားပါ။",
    },
    "en": {
        "greeting": (
            "🔮 Welcome to **Su Mon Myint Oo Mahabote Astrology & Tarot**!\n\n"
            "I will prepare your birth-day astrology reading.\n"
            "Please type your **name** to begin. 🙏"
        ),
        "ask_name": "Please enter your name. 🙏",
        "ask_dob": (
            "Thank you, **{name}**!\n\n"
            "Please enter your **date of birth**.\n"
            "Example: `1990-05-15` (YYYY-MM-DD) 📅"
        ),
        "invalid_date": (
            "❌ Invalid date format.\n\n"
            "Please enter in `YYYY-MM-DD` format.\n"
            "Example: `1990-05-15` 📅"
        ),
        "ask_wednesday": (
            "You were born on a **Wednesday**!\n\n"
            "In Mahabote astrology, Wednesday is split into two parts:\n"
            "• **Morning** (before noon) = Mercury\n"
            "• **Afternoon** (after noon) = Rahu\n\n"
            "Were you born in the **morning** or **afternoon**?\n"
            "(Type `morning` or `afternoon`) ⏰"
        ),
        "wednesday_invalid": (
            "Please type `morning` or `afternoon`. ⏰"
        ),
        "calc_error": "❌ Calculation error: {error}\nPlease try again.",
        "forecast_done": (
            "Your 6-month forecast has been displayed.\n\n"
            "For more precise Tarot readings, book an appointment:\n"
            "👉 **[Book a Tarot Session](/booking)** 🙏"
        ),
        "thank_response": (
            "You're welcome! Feel free to ask anytime.\n\n"
            "👉 **[Book a Tarot Session](/booking)** 🙏"
        ),
        "other_response": (
            "👉 **[Book a Tarot Session](/booking)**\n\n"
            "If you have other questions, feel free to ask. 🙏"
        ),
        "booking_link": (
            "📅 To book a **Tarot session**, click the link below:\n\n"
            "👉 [Book Appointment](/booking)\n\n"
            "Consult directly with Su Mon Myint Oo. 🔮"
        ),
        "refresh": "🙏 Please refresh the page to start again.",
        "server_error": "❌ Cannot connect to server. Please try again.",
        "generic_error": "❌ Something went wrong. Please try again.",
    },
}


# ── Input Hints (for frontend) ───────────────────────────────
HINTS = {
    "my": {
        "greeting": "သင့်ရဲ့ အမည်ကို ရိုက်ထည့်ပေးပါ",
        "ask_dob": "မွေးနေ့ ရက်စွဲကို YYYY-MM-DD ပုံစံဖြင့် ရိုက်ထည့်ပါ",
        "ask_wednesday": "နံနက် သို့မဟုတ် ညနေ ဟု ရိုက်ထည့်ပါ",
        "reading_shown": "ဟုတ်ကဲ့ (ဟောစာတမ်း) ဟု ရိုက်ထည့်ပါ",
        "forecast_shown": "ရက်ချိန်း ဟု ရိုက်ထည့်၍ ရက်ချိန်း ယူပါ",
    },
    "en": {
        "greeting": "Type your name",
        "ask_dob": "Enter date of birth in YYYY-MM-DD format",
        "ask_wednesday": "Type morning or afternoon",
        "reading_shown": "Type yes to see the 6-month forecast",
        "forecast_shown": "Type appointment to book a session",
    },
}


# ── Forecast Rules — English Translations ────────────────────
FORECAST_EN = {
    0: {  # Binga
        "do_en": [
            "Meditate and seek inner peace",
            "Save money and be frugal",
            "Teach and share your knowledge",
            "Get a health checkup",
            "Make long-term investments",
            "Strengthen family bonds",
        ],
        "dont_en": [
            "Avoid short-term gambling",
            "Don't overspend",
            "Avoid long trips on Saturday",
            "Don't make impulsive decisions",
            "Avoid lending money",
            "Avoid arguments",
        ],
    },
    1: {  # Puti
        "do_en": [
            "Pay special attention to your health",
            "Live with integrity",
            "Perform religious merit",
            "Be humble in interactions",
            "Seek inner peace",
            "Pursue education",
        ],
        "dont_en": [
            "Avoid gossip and slander",
            "Avoid work that harms your health",
            "Avoid anger",
            "Avoid work driven by delusion",
            "Avoid deception",
            "Avoid conflict",
        ],
    },
    2: {  # Thike
        "do_en": [
            "Take care of family matters",
            "Start new savings plans",
            "Preserve heirlooms and heritage",
            "Make charitable donations",
            "Participate in religious activities",
            "Make home improvements",
        ],
        "dont_en": [
            "Avoid traveling west on Monday",
            "Don't sell heirlooms easily",
            "Avoid falling out with family",
            "Control hostility",
            "Avoid unnecessary expenses",
        ],
    },
    3: {  # Marana
        "do_en": [
            "Practice meditation and insight (Vipassana)",
            "Pay special attention to your health",
            "Accept life changes",
            "Perform many meritorious deeds",
            "Live peacefully",
            "Keep your mind steady",
        ],
        "dont_en": [
            "Avoid long trips on Friday",
            "Don't make extreme decisions",
            "Avoid dangerous activities",
            "Don't repeat past mistakes",
            "Avoid emotionally triggering situations",
        ],
    },
    4: {  # Adhipati
        "do_en": [
            "Take on new management roles",
            "Assume leadership positions",
            "Start new ventures",
            "Collaborate with others",
            "Make decisive choices",
            "Embrace your success",
        ],
        "dont_en": [
            "Avoid traveling south on Thursday",
            "Avoid arrogance",
            "Don't be overly strict",
            "Avoid being authoritarian",
            "Don't suppress others' rights",
        ],
    },
    5: {  # Yarza
        "do_en": [
            "Make bold decisions",
            "Exercise regularly",
            "Perform religious merit",
            "Make investments",
            "Handle real estate matters",
            "Strive for leadership",
        ],
        "dont_en": [
            "Avoid handling sharp weapons on Tuesday",
            "Avoid anger",
            "Avoid war and conflict",
            "Be cautious of fire hazards",
            "Avoid excessive risk-taking",
            "Control hostility",
        ],
    },
    6: {  # Ahtun
        "do_en": [
            "Develop your leadership abilities",
            "Make charitable donations",
            "Take care of your physical health",
            "Boldly pursue new ventures",
            "Make confident decisions",
            "Practice sports and exercise",
        ],
        "dont_en": [
            "Avoid traveling east on Sunday",
            "Avoid extreme decisions",
            "Control your desire for fame",
            "Don't make hasty decisions",
            "Avoid vanity",
        ],
    },
}


# ── Month Modifiers — English ────────────────────────────────
MONTH_MODIFIERS_EN = [
    "This month brings heightened enthusiasm",       # Month 1
    "Financial luck is bright this month",           # Month 2
    "Relationships grow stronger this month",        # Month 3
    "Career opportunities await this month",         # Month 4
    "Extra health care is needed this month",        # Month 5
    "Education and research luck is good this month",# Month 6
]


# ── Reading Format Labels ────────────────────────────────────
READING_LABELS = {
    "my": {
        "title": "🌟 **{name}** ၏ မဟာဘုတ် ဗေဒင် ဟောစာတမ်း 🌟",
        "birth_date": "📅 **မွေးနေ့**",
        "myanmar_date": "🗓️ **မြန်မာရက်စွဲ**",
        "myanmar_era": "📆 **မြန်မာသက္ကရာဇ်**",
        "era_suffix": "ခုနှစ် (ကြွင်း {r})",
        "current_age": "🎂 **လက်ရှိအသက်**",
        "age_format": "{age} နှစ် (မြန်မာသက္ကရာဇ် {year} အရ)",
        "current_fortune": "🔮 **ယခုနှစ်ကံကြမ္မာ (သက်ရောက်အိမ်)**",
        "moon_phase": "🌙 **လ အလင်း**",
        "house_label": "🏠 **မဟာဘုတ်အိမ်**",
        "house_index": "🔢 **အိမ်ညွှန်းကိန်း**",
        "nature_label": "📊 **သဘာဝ**",
        "birth_day_label": "☀️ **မွေးနေ့**",
        "planet_label": "🪐 **မွေးနေ့ဂြိုဟ်**",
        "animal_label": "🐾 **ရာသီတိရစ္ဆာန်**",
        "direction_label": "🧭 **ကံကောင်းသော ဦးတည်ရာ**",
        "personality": "**🧬 ကိုယ်ရည်ကိုယ်သွေး ဖတ်ခြင်း:**",
        "strengths": "**💪 အားသာချက်များ:**",
        "forecast_title": "📅 **{name}** ၏ ၆ လ ဟောစာတမ်း",
        "forecast_age": "🎂 **လက်ရှိအသက်**: {age} နှစ် (မြန်မာသက္ကရာဇ် {year} အရ)",
        "forecast_fortune": "🔮 **ယခုနှစ်ကံကြမ္မာ (သက်ရောက်အိမ်)**",
        "forecast_house": "🏠 မူလအိမ်",
        "do_label": "  ✅ လုပ်သင့်သည်",
        "dont_label": "  ❌ ရှောင်ကြဉ်ရန်",
    },
    "en": {
        "title": "🌟 Mahabote Astrology Reading for **{name}** 🌟",
        "birth_date": "📅 **Birth Date**",
        "myanmar_date": "🗓️ **Myanmar Date**",
        "myanmar_era": "📆 **Myanmar Era**",
        "era_suffix": "ME (remainder {r})",
        "current_age": "🎂 **Current Age**",
        "age_format": "{age} years (Myanmar Era {year})",
        "current_fortune": "🔮 **This Year's Fortune (Current House)**",
        "moon_phase": "🌙 **Moon Phase**",
        "house_label": "🏠 **Mahabote House**",
        "house_index": "🔢 **House Index**",
        "nature_label": "📊 **Nature**",
        "birth_day_label": "☀️ **Birth Day**",
        "planet_label": "🪐 **Birth Planet**",
        "animal_label": "🐾 **Zodiac Animal**",
        "direction_label": "🧭 **Lucky Direction**",
        "personality": "**🧬 Personality Reading:**",
        "strengths": "**💪 Strengths:**",
        "forecast_title": "📅 6-Month Forecast for **{name}**",
        "forecast_age": "🎂 **Current Age**: {age} years (Myanmar Era {year})",
        "forecast_fortune": "🔮 **This Year's Fortune (Current House)**",
        "forecast_house": "🏠 Birth House",
        "do_label": "  ✅ DO",
        "dont_label": "  ❌ DON'T",
    },
}


# ── Promotion Message ────────────────────────────────────────
PROMO = {
    "my": (
        "\n═══════════════════════════════════\n"
        "🔮 **Tarot vs မဟာဘုတ် — ဘာကွာလဲ?**\n"
        "═══════════════════════════════════\n\n"
        "📖 **မဟာဘုတ် ဗေဒင်** (အခမဲ့ — ယခု ရရှိပြီး)\n"
        "• မွေးနေ့ အခြေပြု ယေဘူယျ ဟောကိန်းများ\n"
        "• ၆ လ ခန့်မှန်းခြင်း (အထွေထွေ)\n"
        "• ကံကြမ္မာ လမ်းကြောင်း အကြမ်းဖျင်း\n\n"
        "🃏 **Tarot ကတ် ဖတ်ခြင်း** (30,000 ကျပ်)\n"
        "• သင့်ဘဝ အခြေအနေ တိတိပပ ဖတ်ခြင်း\n"
        "• အချစ်ရေး၊ အလုပ်၊ ငွေကြေး → တိကျသော အဖြေများ\n"
        "• ရှောင်ရန်/လုပ်ရန် အသေးစိတ် လမ်းညွှန်ချက်\n"
        "• Su Mon Myint Oo နှင့် တိုက်ရိုက် ဆွေးနွေး (၃၅ မိနစ်)\n\n"
        "💰 **အထူးစျေးနှုန်း: ၃၀,၀၀၀ ကျပ် (KPay ဖြင့် ပေးချေနိုင်ပါသည်)** 💰\n\n"
        "🎯 မဟာဘုတ်က ကံကြမ္မာ လမ်းကြောင်းကို ပြပါတယ်...\n"
        "🃏 Tarot က **ဘယ်လို ရွေးချယ်ရမလဲ** ကို ပြပါတယ်!\n\n"
        "👉 **[Tarot ရက်ချိန်း ယူရန် နှိပ်ပါ](/booking)**"
    ),
    "en": (
        "\n═══════════════════════════════════\n"
        "🔮 **Tarot vs Mahabote — What's the difference?**\n"
        "═══════════════════════════════════\n\n"
        "📖 **Mahabote Astrology** (Free — you just received it)\n"
        "• General predictions based on birth day\n"
        "• 6-month forecast (general guidance)\n"
        "• Rough destiny path overview\n\n"
        "🃏 **Tarot Card Reading** (30,000 MMK)\n"
        "• Precise reading of your current life situation\n"
        "• Love, career, finances → specific answers\n"
        "• Detailed do/don't guidance\n"
        "• Direct consultation with Su Mon Myint Oo (35 min)\n\n"
        "💰 **Special price: 30,000 MMK (Pay via KPay)** 💰\n\n"
        "🎯 Mahabote shows you the path of destiny...\n"
        "🃏 Tarot shows you **how to choose**!\n\n"
        "👉 **[Book a Tarot Session](/booking)**"
    ),
}


def t(lang: str, category: str, key: str, **kwargs) -> str:
    """Get a translated string. Falls back to Myanmar if key not found."""
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    
    store = globals().get(category.upper(), {})
    text = store.get(lang, {}).get(key, "")
    
    if not text:
        # Fallback to Myanmar
        text = store.get(DEFAULT_LANG, {}).get(key, "")
    
    if kwargs:
        text = text.format(**kwargs)
    
    return text
