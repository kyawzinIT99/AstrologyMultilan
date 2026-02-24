"""
PDF Report Generator for Myanmar Astrology.

Generates professional PDF reports with Myanmar Unicode text
using fpdf2 and the Padauk font.
"""

import os
from datetime import datetime
from fpdf import FPDF
from mahabote_engine import MahaboteEngine, MahaboteReading
from translations import FORECAST_EN, MONTH_MODIFIERS_EN


# Path to fonts directory — try multiple locations for Modal compatibility
def _find_font_dir():
    candidates = [
        "/root/fonts",                                           # Modal mounted path
        os.path.join("/root", "fonts"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts"),  # local dev
        os.path.join(os.getcwd(), "fonts"),
    ]
    for p in candidates:
        if os.path.exists(p) and os.path.isdir(p):
            font_check = os.path.join(p, "Padauk-Regular.ttf")
            if os.path.exists(font_check):
                print(f"[PDF] ✅ Found Myanmar font at: {p}")
                return p
    print(f"[PDF] ⚠️ Myanmar font not found. Searched: {candidates}")
    return candidates[2] if len(candidates) > 2 else "fonts"  # fallback

FONT_DIR = _find_font_dir()

# Report directory — use Modal persistent volume if available, else local static/
if os.path.exists("/data"):
    REPORT_DIR = "/data/reports"
else:
    REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "reports")


class AstrologyPDF(FPDF):
    """Custom PDF class for astrology reports."""

    def __init__(self, reading: MahaboteReading, lang: str = "my"):
        super().__init__()
        self.reading = reading
        self.lang = lang
        self._setup_fonts()

    @property
    def _use_en(self):
        """Whether to render in English."""
        return self.lang == "en"

    def _setup_fonts(self):
        """Register Myanmar Unicode font."""
        font_path = os.path.join(FONT_DIR, "Padauk-Regular.ttf")
        font_bold_path = os.path.join(FONT_DIR, "Padauk-Bold.ttf")

        if os.path.exists(font_path):
            self.add_font("Padauk", "", font_path)
        if os.path.exists(font_bold_path):
            self.add_font("Padauk", "B", font_bold_path)

        self._has_myanmar_font = os.path.exists(font_path)

    def _set_font_safe(self, style="", size=12):
        """Set font with fallback."""
        if self._has_myanmar_font:
            self.set_font("Padauk", style, size)
        else:
            self.set_font("Helvetica", style, size)

    def header(self):
        """Page header with gradient bar."""
        # Purple gradient header bar
        self.set_fill_color(88, 28, 135)
        self.rect(0, 0, 210, 35, "F")
        self.set_fill_color(139, 92, 246)
        self.rect(0, 30, 210, 5, "F")

        # Title
        self.set_text_color(255, 255, 255)
        self._set_font_safe("B", 18)
        self.set_y(8)
        if self._has_myanmar_font:
            self.cell(0, 12, "Dr.Tarot မဟာဘုတ် ဗေဒင် & Tarot", align="C", new_x="LMARGIN", new_y="NEXT")
        else:
            self.cell(0, 12, "Dr.Tarot Mahabote Astrology & Tarot", align="C", new_x="LMARGIN", new_y="NEXT")

        self.set_text_color(0, 0, 0)
        self.ln(15)

    def footer(self):
        """Page footer."""
        self.set_y(-20)
        self.set_text_color(128, 128, 128)
        self._set_font_safe("", 8)
        if self._has_myanmar_font:
            self.cell(0, 10, f"စာမျက်နှာ {self.page_no()}", align="C")
        else:
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def add_section_header(self, text_mm: str, text_en: str):
        """Add a styled section header."""
        self.set_fill_color(139, 92, 246)
        self.set_text_color(255, 255, 255)
        self._set_font_safe("B", 14)
        label = text_en if self._use_en else (text_mm if self._has_myanmar_font else text_en)
        self.cell(0, 12, f"  {label}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def add_info_row(self, label_mm: str, label_en: str, value_mm: str, value_en: str):
        """Add an info row with label and value."""
        self._set_font_safe("B", 12)
        label = label_en if self._use_en else (label_mm if self._has_myanmar_font else label_en)
        self.cell(60, 9, label)
        self._set_font_safe("", 12)
        value = value_en if self._use_en else (value_mm if self._has_myanmar_font else value_en)
        self.cell(0, 9, value, new_x="LMARGIN", new_y="NEXT")

    def add_paragraph(self, text_mm: str, text_en: str):
        """Add a paragraph."""
        self._set_font_safe("", 11)
        text = text_en if self._use_en else (text_mm if self._has_myanmar_font else text_en)
        self.multi_cell(0, 9, text)
        self.ln(3)

    def add_bullet(self, text_mm: str, text_en: str, icon: str = "- "):
        """Add a bullet point."""
        self._set_font_safe("", 11)
        self.set_x(self.l_margin)
        text = text_en if self._use_en else (text_mm if self._has_myanmar_font else text_en)
        self.multi_cell(0, 9, f"  {icon}{text}")

    def generate_report(self, engine: MahaboteEngine):
        """Generates the content of the PDF report."""
        reading = self.reading
        lang = self.lang
        self.add_page()

        house = reading.house
        bd = reading.birth_day
        md = reading.myanmar_date

        # ── Personal Info Section ──
        self.add_section_header("ကိုယ်ရေးအချက်အလက်", "Personal Information")
        self.add_info_row("အမည်:", "Name:", reading.name, reading.name)
        self.add_info_row(
            "မွေးနေ့:", "Birth Date:",
            reading.birth_date.strftime("%Y-%m-%d"), reading.birth_date.strftime("%Y-%m-%d")
        )
        self.add_info_row(
            "မြန်မာရက်စွဲ:", "Myanmar Date:",
            md.display, f"ME {md.myanmar_year}, {md.month_name}"
        )
        self.add_info_row(
            "မွေးမြန်မာသက္ကရာဇ်:", "Birth Myanmar Era:",
            f"{reading.myanmar_year} ခုနှစ်", str(reading.myanmar_year)
        )
        self.add_info_row(
            "လက်ရှိအသက်:", "Current Age:",
            f"{reading.current_age} နှစ် (မြန်မာသက္ကရာဇ် {reading.current_myanmar_year} အရ)", f"{reading.current_age} Years Old"
        )
        self.add_info_row(
            "မွေးနေ့:", "Birth Day:",
            f"{bd['name_mm']} ({bd['planet_mm']})",
            f"{bd['name_en']} ({bd['planet_en']})"
        )
        self.add_info_row(
            "ရာသီတိရစ္ဆာန်:", "Zodiac Animal:",
            bd['animal_mm'], bd['animal_en']
        )
        self.add_info_row(
            "ကံကောင်းသောဦးတည်ရာ:", "Lucky Direction:",
            bd['direction_mm'], bd['direction_mm']
        )
        self.ln(5)

        # ── House Analysis Section ──
        self.add_section_header("မဟာဘုတ်အိမ် ဆန်းစစ်ခြင်း", "Mahabote House Analysis")
        self.add_info_row(
            "မူလ မဟာဘုတ်အိမ်:", "Birth House:",
            f"{house['name_mm']} ({house['name_en']})",
            f"{house['name_en']}"
        )
        nature_mm = "ကောင်းသောနှစ်/အိမ်" if "asset" in str(house['nature']).lower() or "nobility" in str(house['nature']).lower() or "treasure" in str(house['nature']).lower() or "supreme" in str(house['nature']).lower() or "brilliance" in str(house['nature']).lower() else "စိန်ခေါ်သောနှစ်/အိမ်"
        self.add_info_row(
            "သဘာဝ:", "Nature:",
            nature_mm, str(house['nature'])
        )
        self.add_info_row("မြန်မာသက္ကရာဇ် ကြွင်း:", "Year Remainder:", str(reading.year_remainder), str(reading.year_remainder))
        self.add_info_row("အိမ်ညွှန်းကိန်း:", "House Index:", str(reading.house_remainder), str(reading.house_remainder))
        self.ln(3)

        # Personality
        self.add_section_header("ကိုယ်ရည်ကိုယ်သွေး (မူလအိမ်)", "Personality Profile (Birth House)")
        self.add_paragraph(house['personality_mm'], house.get('personality_en', house['personality_mm']))
        self.ln(2)

        # Strengths
        self._set_font_safe("B", 11)
        if self._use_en:
            self.cell(0, 8, "Strengths:", new_x="LMARGIN", new_y="NEXT")
        elif self._has_myanmar_font:
            self.cell(0, 8, "အားသာချက်များ:", new_x="LMARGIN", new_y="NEXT")
        else:
            self.cell(0, 8, "Strengths:", new_x="LMARGIN", new_y="NEXT")
        for s in house.get("strengths_mm", []):
            self.add_bullet(s, s, "+ ")

        self.ln(2)

        # Weaknesses
        self._set_font_safe("B", 11)
        if self._use_en:
            self.cell(0, 8, "Caution:", new_x="LMARGIN", new_y="NEXT")
        elif self._has_myanmar_font:
            self.cell(0, 8, "သတိထားရန်:", new_x="LMARGIN", new_y="NEXT")
        else:
            self.cell(0, 8, "Caution:", new_x="LMARGIN", new_y="NEXT")
        for w in house.get("weaknesses_mm", []):
            self.add_bullet(w, w, "- ")

        # ── Current Year Prediction ──
        self.add_page()
        self.add_section_header("ယခုနှစ်ကံကြမ္မာ (သက်ရောက်အိမ်)", "Current Year Fortune (Thet-Yauk)")
        curr_house = reading.current_year_house
        self.add_info_row(
            "သက်ရောက်အိမ်:", "Current House:",
            f"{curr_house['name_mm']} ({curr_house['name_en']})",
            f"{curr_house['name_en']}"
        )
        curr_nature_mm = "ကောင်းသောနှစ်" if "asset" in str(curr_house['nature']).lower() or "nobility" in str(curr_house['nature']).lower() or "treasure" in str(curr_house['nature']).lower() or "supreme" in str(curr_house['nature']).lower() or "brilliance" in str(curr_house['nature']).lower() else "စိန်ခေါ်သောနှစ်"
        self.add_info_row(
            "နှစ်၏ သဘာဝ:", "Nature of Year:",
            curr_nature_mm, str(curr_house['nature'])
        )
        self.ln(3)
        self.add_paragraph(curr_house['personality_mm'], curr_house.get('personality_en', curr_house['personality_mm']))
        self.ln(5)

        # ── 6-Month Forecast Section ──
        self.add_section_header("၆ လ ဟောစာတမ်း", "6-Month Forecast")

        forecasts = engine.generate_6month_forecast(reading, lang=lang)
        for f in forecasts:
            # Month header
            self.set_fill_color(243, 232, 255)
            self._set_font_safe("B", 11)
            self.cell(0, 8, f"  {f['month_en']}", fill=True, new_x="LMARGIN", new_y="NEXT")
            self.ln(1)

            # Modifier
            self._set_font_safe("", 10)
            self.set_text_color(88, 28, 135)
            modifier_key = 'modifier_en' if self._use_en else 'modifier_mm'
            self.cell(0, 7, f"    {f[modifier_key]}", new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(0, 0, 0)

            # Do
            do_key = 'do_en' if self._use_en else 'do_mm'
            dont_key = 'dont_en' if self._use_en else 'dont_mm'
            do_label = "DO" if self._use_en else "လုပ်သင့်သည်"
            dont_label = "DON'T" if self._use_en else "ရှောင်ကြဉ်ရန်"

            self.set_text_color(22, 101, 52)
            self.add_bullet(f"{do_label}: {f.get(do_key, f['do_mm'])}", f"DO: {f.get('do_en', f['do_mm'])}", "[+] ")

            # Don't
            self.set_text_color(185, 28, 28)
            self.add_bullet(f"{dont_label}: {f.get(dont_key, f['dont_mm'])}", f"DON'T: {f.get('dont_en', f['dont_mm'])}", "[-] ")

            self.set_text_color(0, 0, 0)
            self.ln(3)

        # Footer note
        self.ln(10)
        self.set_text_color(128, 128, 128)
        self._set_font_safe("", 8)
        gen_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        if self._use_en:
            self.cell(0, 7, f"Generated on {gen_date}", align="C", new_x="LMARGIN", new_y="NEXT")
            self.cell(0, 7, "Based on traditional Myanmar Mahabote astrology calculations.", align="C")
        elif self._has_myanmar_font:
            self.cell(0, 7, f"ဤဟောစာတမ်းကို {gen_date} တွင် ထုတ်လုပ်ထားပါသည်။", align="C", new_x="LMARGIN", new_y="NEXT")
            self.cell(0, 7, "မြန်မာ မဟာဘုတ် ဗေဒင် အခြေခံ တွက်ချက်မှုများ ပါဝင်ပါသည်။", align="C")
        else:
            self.cell(0, 7, f"Generated on {gen_date}", align="C", new_x="LMARGIN", new_y="NEXT")
            self.cell(0, 7, "Based on traditional Myanmar Mahabote astrology calculations.", align="C")


def generate_pdf(reading: MahaboteReading, engine: MahaboteEngine, lang: str = "my") -> str:
    """Helper function to generate a PDF and return the file path."""
    pdf = AstrologyPDF(reading, lang=lang)
    pdf.generate_report(engine)

    # Use underscores instead of spaces for safer URLs
    safe_name = reading.name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_{timestamp}.pdf"

    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR, exist_ok=True)

    file_path = os.path.join(REPORT_DIR, filename)
    pdf.output(file_path)
    return file_path
