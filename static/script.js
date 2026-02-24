/* ═══════════════════════════════════════════════════════════
   Myanmar Astrology Chatbot — Frontend Logic
   Multi-Language Support (my / en)
   ═══════════════════════════════════════════════════════════ */

const chatMessages = document.getElementById('chatMessages');
const chatArea = document.getElementById('chatArea');
const userInput = document.getElementById('userInput');
const btnSend = document.getElementById('btnSend');
const pdfDownloadArea = document.getElementById('pdfDownloadArea');
const inputHint = document.getElementById('inputHint');

let isProcessing = false;
let currentState = 'greeting';
let currentLang = 'my';  // default language
let currentHints = {};    // filled from server

// ── Initialize ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    createStars();
    initChat();
});

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// ── Stars Background ────────────────────────────────────────
function createStars() {
    const container = document.getElementById('starsContainer');
    const count = 80;
    for (let i = 0; i < count; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.setProperty('--duration', (2 + Math.random() * 4) + 's');
        star.style.setProperty('--max-opacity', (0.3 + Math.random() * 0.7).toString());
        star.style.animationDelay = Math.random() * 4 + 's';
        star.style.width = (1 + Math.random() * 2) + 'px';
        star.style.height = star.style.width;
        container.appendChild(star);
    }
}

// ── Language Toggle ─────────────────────────────────────────
async function toggleLanguage() {
    const newLang = currentLang === 'my' ? 'en' : 'my';
    try {
        const res = await fetch('/api/set_lang', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lang: newLang }),
        });
        const data = await res.json();
        currentLang = data.lang;
        currentHints = data.hints || {};
        updateLangUI();
        // Reset chat with new language
        resetChat();
    } catch (err) {
        console.error('Language switch failed:', err);
    }
}

function updateLangUI() {
    const flag = document.getElementById('langFlag');
    if (flag) {
        flag.textContent = currentLang === 'my' ? '🇲🇲' : '🇬🇧';
    }
    // Update input placeholder
    if (currentLang === 'en') {
        userInput.placeholder = 'Type a message...';
    } else {
        userInput.placeholder = 'မက်ဆေ့ချ် ရိုက်ထည့်ပါ...';
    }
    updateHint();
}

// ── Chat Initialization ─────────────────────────────────────
async function initChat() {
    showTyping();
    try {
        const res = await fetch(`/api/init?lang=${currentLang}`);
        const data = await res.json();
        removeTyping();
        addMessage('bot', data.response);
        currentState = data.state;
        if (data.lang) currentLang = data.lang;
        if (data.hints) currentHints = data.hints;
        updateLangUI();
    } catch (err) {
        removeTyping();
        const errMsg = currentLang === 'en'
            ? '❌ Cannot connect to server. Please try again.'
            : '❌ ဆာဗာနှင့် ချိတ်ဆက်၍ မရပါ။ ထပ်မံကြိုးစားပါ။';
        addMessage('bot', errMsg);
    }
}

// ── Send Message ────────────────────────────────────────────
async function sendMessage() {
    const msg = userInput.value.trim();
    if (!msg || isProcessing) return;

    isProcessing = true;
    btnSend.disabled = true;
    userInput.value = '';

    addMessage('user', msg);
    showTyping();

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg, lang: currentLang }),
        });
        const data = await res.json();

        // Simulate a slight delay for natural feel
        await new Promise(r => setTimeout(r, 400 + Math.random() * 600));

        removeTyping();
        addMessage('bot', data.response);
        currentState = data.state;
        if (data.lang) currentLang = data.lang;

        updateHint();
    } catch (err) {
        removeTyping();
        const errMsg = currentLang === 'en'
            ? '❌ Something went wrong. Please try again.'
            : '❌ တစ်စုံတစ်ခု မှားယွင်းနေပါသည်။ ထပ်မံကြိုးစားပါ။';
        addMessage('bot', errMsg);
    }

    isProcessing = false;
    btnSend.disabled = false;
    userInput.focus();
}

// ── Add Message ─────────────────────────────────────────────
function addMessage(role, content) {
    const msg = document.createElement('div');
    msg.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'bot' ? '🔮' : '👤';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = formatMessage(content);

    msg.appendChild(avatar);
    msg.appendChild(bubble);
    chatMessages.appendChild(msg);

    scrollToBottom();
}

// ── Format Message ──────────────────────────────────────────
function formatMessage(text) {
    // Escape HTML
    let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Bold: **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic: _text_
    html = html.replace(/_(.*?)_/g, '<em>$1</em>');

    // Links: [text](url)
    html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" style="color: var(--accent-gold); text-decoration: underline;">$1</a>');

    // Inline code: `text`
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');

    // Separator lines
    html = html.replace(/═{3,}/g, '<span class="msg-separator"></span>');

    return html;
}

// ── Typing Indicator ────────────────────────────────────────
function showTyping() {
    const msg = document.createElement('div');
    msg.className = 'message bot';
    msg.id = 'typingIndicator';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🔮';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = `
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;

    msg.appendChild(avatar);
    msg.appendChild(bubble);
    chatMessages.appendChild(msg);
    scrollToBottom();
}

function removeTyping() {
    const el = document.getElementById('typingIndicator');
    if (el) el.remove();
}

// ── Scroll ──────────────────────────────────────────────────
function scrollToBottom() {
    requestAnimationFrame(() => {
        chatArea.scrollTop = chatArea.scrollHeight;
    });
}

// ── Input Hint ──────────────────────────────────────────────
function updateHint() {
    // Use server-provided hints if available, else fallback
    if (currentHints && currentHints[currentState]) {
        inputHint.textContent = currentHints[currentState];
    } else {
        // Fallback hints
        const defaultHints = {
            'greeting': currentLang === 'en' ? 'Type your name' : 'သင့်ရဲ့ အမည်ကို ရိုက်ထည့်ပေးပါ',
            'ask_dob': currentLang === 'en' ? 'Enter date of birth (YYYY-MM-DD)' : 'မွေးနေ့ ရက်စွဲကို YYYY-MM-DD ပုံစံဖြင့် ရိုက်ထည့်ပါ',
            'ask_wednesday': currentLang === 'en' ? 'Type morning or afternoon' : 'နံနက် သို့မဟုတ် ညနေ ဟု ရိုက်ထည့်ပါ',
            'reading_shown': currentLang === 'en' ? 'Type yes to see the 6-month forecast' : 'ဟုတ်ကဲ့ (ဟောစာတမ်း) ဟု ရိုက်ထည့်ပါ',
            'forecast_shown': currentLang === 'en' ? 'Type appointment to book a session' : 'ရက်ချိန်း ဟု ရိုက်ထည့်၍ ရက်ချိန်း ယူပါ',
        };
        inputHint.textContent = defaultHints[currentState] || '';
    }
}

// ── PDF Download ────────────────────────────────────────────
async function downloadPDF() {
    try {
        const res = await fetch('/api/generate-pdf', { method: 'POST' });
        if (!res.ok) throw new Error('PDF generation failed');

        const arrayBuffer = await res.arrayBuffer();
        const blob = new Blob([arrayBuffer], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);

        // Extract filename from Content-Disposition header or use default
        const disposition = res.headers.get('Content-Disposition');
        let filename = 'mahabote_report.pdf';
        if (disposition) {
            const match = disposition.match(/filename\*?=(?:UTF-8'')?["']?([^"';\n]+)/i);
            if (match) filename = decodeURIComponent(match[1]);
        }

        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        addMessage('bot', '✅ PDF ဟောစာတမ်း ဒေါင်းလုဒ် အောင်မြင်ပါပြီ! 🎉');
    } catch (err) {
        addMessage('bot', '❌ PDF ဖန်တီးရာတွင် အမှားရှိပါသည်။ ထပ်မံကြိုးစားပါ။');
    }
}

// ── Reset Chat ──────────────────────────────────────────────
function resetChat() {
    chatMessages.innerHTML = '';
    currentState = 'greeting';
    // Clear server session with current language
    fetch(`/api/init?lang=${currentLang}`).then(res => res.json()).then(data => {
        addMessage('bot', data.response);
        currentState = data.state;
        if (data.lang) currentLang = data.lang;
        if (data.hints) currentHints = data.hints;
        updateLangUI();
    });
}

// ── Developer Modal ─────────────────────────────────────────
function toggleDevModal() {
    const modal = document.getElementById('devModal');
    if (modal) {
        modal.classList.toggle('active');
    }
}
