"""
Myanmar Astrology Chatbot — Flask Backend

Provides a ChatGPT-style conversational interface for Mahabote astrology readings.
All responses are in Myanmar language.
"""

import os
import re
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, flash

from mahabote_engine import MahaboteEngine, MahaboteReading
from pdf_generator import generate_pdf
from sheets_sync import sync_new_booking, sync_status_update
from translations import CHAT, PROMO, HINTS

app = Flask(__name__)
app.secret_key = "astrology_chatbot_super_secret_key_2024_v2"  # Required for sessions

# Cookie security — set Secure flag when deployed to HTTPS (Modal)
import os as _os
_on_modal = _os.path.exists("/data") or _os.path.exists("/root/fonts")
app.config["SESSION_COOKIE_SECURE"] = _on_modal      # Only send cookie over HTTPS
app.config["SESSION_COOKIE_HTTPONLY"] = True          # Block JS access to cookie
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"        # Allow redirects to send cookie

engine = MahaboteEngine()

# In-memory session store (for simplicity)
sessions = {}

# Bookings storage (JSON file)
# Use Modal persistent Volum if /data exists, otherwise use local dir
if os.path.exists("/data"):
    BOOKINGS_FILE = "/data/bookings.json"
else:
    BOOKINGS_FILE = os.path.join(os.path.dirname(__file__), "bookings.json")


import fcntl
import tempfile

def load_bookings():
    """Load bookings from JSON file with file locking."""
    if not os.path.exists(BOOKINGS_FILE):
        return []
    try:
        with open(BOOKINGS_FILE, "r", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                data = f.read()
                if not data.strip():
                    return []
                return json.loads(data)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except Exception as e:
        print(f"Error reading bookings.json: {e}")
        return []

def save_bookings(bookings):
    """Save bookings to JSON file atomically."""
    temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(BOOKINGS_FILE)), text=True)
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(bookings, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, BOOKINGS_FILE)
    except Exception as e:
        print(f"Error saving bookings.json: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)


import threading

db_lock = threading.Lock()

def _update_bookings(modifier_func):
    """
    Safely update bookings using an exclusive thread lock.
    The modifier_func should take the bookings list and return (new_bookings_list, return_value).
    If new_bookings_list is None, nothing gets saved.
    """
    with db_lock:
        bookings = load_bookings()
        updated_bookings, ret_val = modifier_func(bookings)
        if updated_bookings is not None:
            save_bookings(updated_bookings)
        return ret_val


def get_session_data():
    """Get or create session data."""
    sid = session.get("sid")
    if not sid or sid not in sessions:
        sid = str(uuid.uuid4())
        session["sid"] = sid
        sessions[sid] = {
            "state": "greeting",
            "name": None,
            "dob": None,
            "is_wednesday_pm": False,
            "reading": None,
            "history": [],
            "lang": "my",  # default language
        }
    return sessions[sid]


@app.route("/")
def index():
    """Serve the chatbot frontend."""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """Process a chat message and return the bot response."""
    data = request.get_json()
    user_msg = data.get("message", "").strip()

    sess = get_session_data()
    # Allow language override per message
    if data.get("lang") in ("my", "en"):
        sess["lang"] = data["lang"]

    sess["history"].append({"role": "user", "content": user_msg})

    response = process_message(sess, user_msg)

    sess["history"].append({"role": "bot", "content": response})

    return jsonify({
        "response": response,
        "state": sess["state"],
        "has_reading": sess["reading"] is not None,
        "lang": sess["lang"],
    })


@app.route("/api/init", methods=["GET"])
def init_chat():
    """Initialize a new chat session and return the greeting."""
    sess = get_session_data()
    lang = request.args.get("lang", sess.get("lang", "my"))
    if lang in ("my", "en"):
        sess["lang"] = lang
    greeting = engine.get_greeting_message(lang=sess["lang"])
    sess["history"].append({"role": "bot", "content": greeting})
    return jsonify({
        "response": greeting,
        "state": "greeting",
        "lang": sess["lang"],
        "hints": HINTS.get(sess["lang"], HINTS["my"]),
    })


@app.route("/api/set_lang", methods=["POST"])
def set_lang():
    """Switch the chatbot language."""
    data = request.get_json()
    lang = data.get("lang", "my")
    if lang not in ("my", "en"):
        lang = "my"
    sess = get_session_data()
    sess["lang"] = lang
    return jsonify({"lang": lang, "hints": HINTS.get(lang, HINTS["my"])})




# ── Booking Routes ───────────────────────────────────────────

@app.route("/booking")
def booking_page():
    """Serve the appointment booking page."""
    sess = get_session_data()
    lang = sess.get("lang", "my")
    
    # Booking page translations
    T = {
        "my": {
            "title": "ရက်ချိန်း ယူရန် | Dr.Tarot Tarot",
            "back_btn": "← Chat သို့ ပြန်သွားရန်",
            "header_title": "Tarot ရက်ချိန်း ယူရန်",
            "header_desc": "Dr.Tarot နှင့် ဗေဒင် ရက်ချိန်း စီစဉ်ရန်",
            "form_title": "📝 ရက်ချိန်းအသစ် ယူရန်",
            "label_name": "အမည် *",
            "placeholder_name": "သင့်အမည် ရိုက်ထည့်ပါ",
            "label_phone": "Viber ဖုန်းနံပါတ် (Viber ရှိသော နံပါတ်သာ) *",
            "placeholder_phone": "09xxxxxxxxx သို့မဟုတ် +959xxxxxxxxx",
            "warning_phone": "⚠️ Viber ဖြင့် အတည်ပြုနိုင်ခြင်း မရှိပါက ရက်ချိန်း ပျက်ပြယ်ပါမည်။",
            "label_date": "ရက်စွဲ ရွေးချယ်ပါ *",
            "label_time": "အချိန် ရွေးချယ်ပါ *",
            "label_topic": "အကြောင်းအရာ (ရွေးချယ်ပါ)",
            "topic_general": "အထွေထွေ ဗေဒင်",
            "topic_love": "အချစ်ရေး",
            "topic_career": "အလုပ်အကိုင်",
            "topic_finance": "ငွေကြေးရေးရာ",
            "topic_health": "ကျန်းမာရေး",
            "topic_family": "မိသားစု",
            "topic_tarot": "Tarot Card Reading",
            "label_note": "မှတ်ချက် (မလိုအပ်ပါ)",
            "placeholder_note": "ထပ်မံ ပြောကြားလိုသည်များ...",
            "btn_submit": "📅 ရက်ချိန်း အတည်ပြုရန်",
            "btn_loading": "⏳ စောင့်ပါ...",
            "success_title": "ရက်ချိန်း တောင်းဆိုမှု အောင်မြင်ပါသည်!",
            "ref_text": "ရက်ချိန်း ရည်ညွှန်းအမှတ်:",
            "payment_title": "ငွေပေးချေရန် လိုအပ်ပါသည် 💰",
            "payment_desc1": "ရက်ချိန်းကို အပြီးသတ် အတည်ပြုနိုင်ရန် အောက်ပါ KPay အကောင့်သို့",
            "payment_amt": "၃၀,၀၀၀ ကျပ်",
            "payment_desc2": "လွှဲပြောင်းပေးပါ:",
            "payment_note": "ငွေလွှဲပြေစာ (Screenshot) ကို <strong>ရက်ချိန်း ရည်ညွှန်းအမှတ်</strong> နှင့်တကွ Viber မှတစ်ဆင့် ပေးပို့ပေးပါ။ ငွေလွှဲပြေစာ ရရှိမှသာ ရက်ချိန်း အတည်ပြုပေးပါမည်။",
            "history_title": "📋 ရက်ချိန်း မှတ်တမ်း",
            "empty_history": "ရက်ချိန်း မရှိသေးပါ။",
            "alert_phone": "Viber ဖုန်းနံပါတ် အမှန်ကိုသာ ထည့်သွင်းပေးပါ။ (ဥပမာ - 09123456789)",
            "alert_time": "ကျေးဇူးပြု၍ အချိန် ရွေးချယ်ပါ။",
            "alert_error": "ရက်ချိန်း ယူရာတွင် အမှားရှိပါသည်။",
            "alert_server": "ဆာဗာနှင့် ချိတ်ဆက်၍ မရပါ။",
            "status_confirmed": "အတည်ပြုပြီး",
            "status_completed": "ပြီးဆုံးပြီး",
            "status_pending": "စောင့်ဆိုင်းနေဆဲ"
        },
        "en": {
            "title": "Book Appointment | Dr.Tarot",
            "back_btn": "← Back to Chat",
            "header_title": "Book Tarot Appointment",
            "header_desc": "Schedule a session with Dr.Tarot",
            "form_title": "📝 Request New Appointment",
            "label_name": "Name *",
            "placeholder_name": "Enter your name",
            "label_phone": "Viber Phone Number (Viber only) *",
            "placeholder_phone": "09xxxxxxxxx or +959xxxxxxxxx",
            "warning_phone": "⚠️ Appointment will be cancelled if unable to confirm via Viber.",
            "label_date": "Select Date *",
            "label_time": "Select Time *",
            "label_topic": "Topic (Optional)",
            "topic_general": "General Astrology",
            "topic_love": "Love & Relationship",
            "topic_career": "Career",
            "topic_finance": "Finance",
            "topic_health": "Health",
            "topic_family": "Family",
            "topic_tarot": "Tarot Card Reading",
            "label_note": "Note (Optional)",
            "placeholder_note": "Any additional requests...",
            "btn_submit": "📅 Confirm Appointment",
            "btn_loading": "⏳ Please wait...",
            "success_title": "Appointment Requested Successfully!",
            "ref_text": "Booking Reference:",
            "payment_title": "Payment Required 💰",
            "payment_desc1": "To finalize your appointment, please transfer",
            "payment_amt": "30,000 MMK",
            "payment_desc2": "to the following KPay account:",
            "payment_note": "Please send the payment screenshot along with your <strong>Booking Reference</strong> via Viber. Your appointment will only be confirmed upon receiving the receipt.",
            "history_title": "📋 Booking History",
            "empty_history": "No bookings yet.",
            "alert_phone": "Please enter a valid Viber number. (e.g. 09123456789)",
            "alert_time": "Please select a time.",
            "alert_error": "Error processing booking request.",
            "alert_server": "Unable to connect to server.",
            "status_confirmed": "Confirmed",
            "status_completed": "Completed",
            "status_pending": "Pending"
        }
    }
    
    return render_template("booking.html", lang=lang, t=T[lang], t_json=json.dumps(T[lang]))


@app.route("/admin")
def admin_page():
    """Serve the admin dashboard."""
    if not session.get("admin_logged_in"):
        return redirect(url_for("login_page"))
    return render_template("admin.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    """Admin login page."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username == "kyawzin" and password == "Kyawzin@123456":
            session["admin_logged_in"] = True
            session.permanent = False
            return redirect(url_for("admin_page"), 303)  # 303 forces GET after POST
        else:
            flash("Invalid credentials. Please try again.")
            
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log out the admin."""
    session.pop("admin_logged_in", None)
    return redirect(url_for("login_page"))


@app.route("/api/admin/generate_pdf", methods=["POST"])
def admin_generate_pdf():
    """Generate Mahabote PDF for admin only."""
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    name = data.get("name")
    dob_str = data.get("dob")
    is_pm = data.get("is_wednesday_pm")

    if not name or not dob_str:
        return jsonify({"error": "Missing name or date of birth"}), 400

    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    try:
        reading = engine.calculate(
            name=name,
            birth_year=dob.year,
            birth_month=dob.month,
            birth_day=dob.day,
            is_wednesday_pm=is_pm
        )
        pdf_path = generate_pdf(reading, engine)

        filename = os.path.basename(pdf_path)

        # On Modal, PDFs are in /data/reports (persistent volume)
        # Serve via a dedicated route; locally, serve from static/reports
        if os.path.exists("/data"):
            pdf_url = f"/api/admin/pdf/{filename}"
        else:
            pdf_url = url_for('static', filename=f'reports/{filename}')


        return jsonify({"message": "PDF generated successfully", "url": pdf_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/pdf/<filename>")
def serve_admin_pdf(filename):
    """Serve a generated PDF from the persistent volume (Modal) or static dir."""
    if not session.get("admin_logged_in"):
        print(f"[PDF Serve] Unauthorized access attempt for {filename}")
        return jsonify({"error": "Unauthorized"}), 401
    
    # Sanitize filename
    filename = os.path.basename(filename)
    
    if os.path.exists("/data"):
        directory = "/data/reports"
    else:
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "reports")
        
    pdf_path = os.path.join(directory, filename)
    print(f"[PDF Serve] Request for {filename} -> {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"[PDF Serve] File not found: {pdf_path}")
        return jsonify({"error": "PDF not found"}), 404
        
    try:
        # Get actual file size
        filesize = os.path.getsize(pdf_path)
        print(f"[PDF Serve] Serving {filename} ({filesize} bytes)")

        from flask import send_from_directory, make_response
        response = make_response(send_from_directory(directory, filename, mimetype="application/pdf"))
        
        # Explicitly set headers to prevent unwanted transformations/encoding issues
        response.headers['Content-Length'] = filesize
        response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        # Prevent Modal/Cloudflare from gzipping/zstding if that's causing issues
        response.headers['Content-Encoding'] = 'identity'
        
        return response
    except Exception as e:
        print(f"[PDF Serve] Error serving file: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/bookings/status", methods=["POST"])
def update_booking_status():
    """Update a booking's status (confirm/reject) and sync to Sheets."""
    data = request.get_json()
    booking_id = data.get("booking_id")
    new_status = data.get("status")

    if not booking_id or new_status not in ("confirmed", "rejected", "pending"):
        return jsonify({"error": "Invalid booking_id or status"}), 400

    def modify_status(bookings_list):
        for b in bookings_list:
            if b["booking_id"] == booking_id:
                b["status"] = new_status
                return bookings_list, b
        return None, None

    updated_booking = _update_bookings(modify_status)

    if not updated_booking:
        return jsonify({"error": "Booking not found"}), 404

    # Send status update to n8n → SMS + Sheets
    try:
        sync_status_update(updated_booking, new_status)
    except Exception as e:
        print(f"⚠️ n8n sync failed: {e}")

    return jsonify({"message": f"Booking {booking_id} → {new_status}"})

@app.route("/api/bookings", methods=["GET"])
def get_bookings():
    """Return all bookings."""
    bookings = load_bookings()
    return jsonify({"bookings": bookings})


@app.route("/api/bookings/<booking_id>", methods=["DELETE"])
def delete_booking(booking_id):
    """Delete a booking."""
    def remove_booking(bookings_list):
        initial_len = len(bookings_list)
        bookings_list = [b for b in bookings_list if b["booking_id"] != booking_id]
        if len(bookings_list) == initial_len:
            return None, False
        return bookings_list, True

    deleted = _update_bookings(remove_booking)

    if not deleted:
        return jsonify({"error": "Booking not found"}), 404

    return jsonify({"message": f"Booking {booking_id} deleted"}), 200


@app.route("/api/bookings", methods=["POST"])
def create_booking():
    """Create a new appointment booking."""
    data = request.get_json()

    # Validate required fields
    required = ["name", "phone", "date", "time"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    # Validate Viber format
    phone_val = data.get("phone", "").strip()
    if not re.match(r"^(09|\+959)\d{7,9}$", phone_val):
        return jsonify({"error": "Viber ဖုန်းနံပါတ် အမှန်ကိုသာ ထည့်သွင်းပေးပါ။ (ဥပမာ - 09123456789)"}), 400

    # Create booking
    booking_id = "BK-" + datetime.now().strftime("%Y%m%d") + "-" + str(uuid.uuid4())[:6].upper()
    booking = {
        "booking_id": booking_id,
        "name": data["name"],
        "phone": data["phone"],
        "date": data["date"],
        "time": data["time"],
        "topic": data.get("topic", "general"),
        "note": data.get("note", ""),
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    def add_booking(bookings_list):
        bookings_list.insert(0, booking)  # newest first
        return bookings_list, True

    _update_bookings(add_booking)

    # Send to n8n → Google Sheets
    try:
        sync_new_booking(booking)
    except Exception as e:
        print(f"⚠️ n8n sync failed: {e}")

    return jsonify({"booking_id": booking_id, "message": "Booking created successfully"}), 201




# ── Tarot vs Mahabote Promotion — now comes from translations.py ──
# PROMO_MSG kept for backward compat; actual promo is PROMO[lang]
PROMO_MSG = PROMO["my"]


def process_message(sess: dict, user_msg: str) -> str:
    """State machine for processing chat messages."""
    state = sess["state"]
    lang = sess.get("lang", "my")
    T = CHAT[lang]

    if state == "greeting":
        # User should provide their name
        if len(user_msg) < 1:
            return T["ask_name"]

        sess["name"] = user_msg
        sess["state"] = "ask_dob"
        return engine.get_dob_prompt(user_msg, lang=lang)

    elif state == "ask_dob":
        # Parse date of birth
        dob = parse_date(user_msg)
        if not dob:
            return T["invalid_date"]

        sess["dob"] = dob

        # Check if it's a Wednesday
        from myanmar_calendar import get_weekday_index, w2j
        jdn = w2j(dob.year, dob.month, dob.day, ct=1)
        wd = (jdn + 2) % 7  # 0=Sat, 4=Wed
        if wd == 4:
            sess["state"] = "ask_wednesday"
            return engine.get_wednesday_prompt(lang=lang)
        else:
            return compute_reading(sess)

    elif state == "ask_wednesday":
        # Parse Wednesday morning/afternoon
        msg_lower = user_msg.lower()
        if "ညနေ" in user_msg or "afternoon" in msg_lower or "pm" in msg_lower:
            sess["is_wednesday_pm"] = True
        elif "နံနက်" in user_msg or "morning" in msg_lower or "am" in msg_lower:
            sess["is_wednesday_pm"] = False
        else:
            return T["wednesday_invalid"]

        return compute_reading(sess)

    elif state == "reading_shown":
        # Check if user wants the 6-month forecast
        msg_lower = user_msg.lower()
        if any(kw in user_msg for kw in ["ဟုတ်", "ဟော", "ကဲ", "yes", "forecast", "ok"]):
            sess["state"] = "forecast_shown"
            return engine.format_forecast(sess["reading"], lang=lang) + PROMO[lang]
            
        # Any subsequent message can just reiterate the promo or answer general questions
        if any(kw in user_msg for kw in ["ကျေးဇူး", "thank", "ကောင်း"]):
            return T["thank_response"]
        else:
            return T["other_response"]

    elif state == "forecast_shown":
        return T["forecast_done"]

    # Handle booking keyword in any state
    if any(kw in user_msg for kw in ["ရက်ချိန်း", "appointment", "book"]):
        return T["booking_link"]

    return T["refresh"]


def compute_reading(sess: dict) -> str:
    """Compute the Mahabote reading and format the response."""
    dob = sess["dob"]
    lang = sess.get("lang", "my")
    try:
        reading = engine.calculate(
            name=sess["name"],
            birth_year=dob.year,
            birth_month=dob.month,
            birth_day=dob.day,
            is_wednesday_pm=sess["is_wednesday_pm"],
        )
        sess["reading"] = reading
        sess["state"] = "reading_shown"
        return engine.format_reading(reading, lang=lang) + PROMO[lang]
    except Exception as e:
        return CHAT[lang]["calc_error"].format(error=str(e))


def parse_date(text: str) -> datetime:
    """Parse a date from user text input."""
    text = text.strip()

    # Try common formats
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y.%m.%d",
        "%m-%d-%Y",
        "%m/%d/%Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(text, fmt)
            # Sanity check: reasonable birth year
            if 1900 <= dt.year <= datetime.now().year:
                return dt
        except ValueError:
            continue

    # Try to extract date from free text
    match = re.search(r'(\d{4})\s*[-/.]?\s*(\d{1,2})\s*[-/.]?\s*(\d{1,2})', text)
    if match:
        try:
            y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
            dt = datetime(y, m, d)
            if 1900 <= dt.year <= datetime.now().year:
                return dt
        except (ValueError, OverflowError):
            pass

    return None


if __name__ == "__main__":
    os.makedirs("static/reports", exist_ok=True)
    os.makedirs("fonts", exist_ok=True)
    print("🔮 Myanmar Astrology Chatbot starting...")
    print("   Open http://localhost:5050 in your browser")
    app.run(debug=True, host="0.0.0.0", port=5050)
