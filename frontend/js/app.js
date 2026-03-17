/**
 * Shared Application Utilities
 * =============================
 * Dark mode toggle, auth token management, navigation, and shared helpers.
 */

// ──── Configuration ────
const API_BASE = window.location.origin;

// ──── Token Management ────
function getToken() {
    return localStorage.getItem('auth_token');
}

function setToken(token) {
    localStorage.setItem('auth_token', token);
}

function removeToken() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
}

function getUser() {
    const data = localStorage.getItem('user_data');
    return data ? JSON.parse(data) : null;
}

function setUser(user) {
    localStorage.setItem('user_data', JSON.stringify(user));
}

function isAuthenticated() {
    return !!getToken();
}

function logout() {
    removeToken();
    window.location.href = '/';
}

// ──── Auth Guard ────
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/';
        return false;
    }
    return true;
}

// ──── API Helper ────
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
        ...options.headers
    };

    // Add auth token if available
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Add Content-Type for JSON payloads
    if (options.body && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'Request failed');
    }

    return data;
}

// ──── Dark Mode ────
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeIcon(next);
}

function updateThemeIcon(theme) {
    const btn = document.getElementById('themeToggle');
    if (btn) {
        btn.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

// ──── Alert Messages ────
function showAlert(elementId, message, type = 'error') {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.className = `alert alert-${type} active`;
    el.textContent = message;

    // Auto-hide after 5 seconds
    setTimeout(() => {
        el.classList.remove('active');
    }, 5000);
}

function hideAlert(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.classList.remove('active');
}

// ──── Loading Overlay ────
function showLoading(text = 'Processing...') {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        const textEl = overlay.querySelector('.loading-text');
        if (textEl) textEl.textContent = text;
        overlay.classList.add('active');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.remove('active');
}

// ──── Navigation Active State ────
function setActiveNav() {
    const path = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === path) {
            link.classList.add('active');
        }
    });
}

// ──── User Info in Navbar ────
function displayUserInfo() {
    const user = getUser();
    const el = document.getElementById('userNameDisplay');
    if (el && user) {
        el.textContent = user.name || user.email;
    }
}

// ──── Format Date ────
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ──── Chatbot ────
const SKINCARE_TIPS = [
    "Always wear sunscreen with SPF 30+ when going outdoors.",
    "Keep your skin moisturized to maintain the skin barrier.",
    "Avoid touching or picking at skin lesions.",
    "Drink plenty of water — hydration helps skin health.",
    "Use gentle, fragrance-free cleansers for sensitive skin.",
    "See a dermatologist annually for full skin checks.",
    "Follow the ABCDE rule to monitor moles: Asymmetry, Border, Color, Diameter, Evolving.",
    "Eat foods rich in vitamins A, C, and E for healthier skin.",
    "Avoid excessive sun exposure between 10 AM and 4 PM.",
    "Clean makeup brushes regularly to prevent skin infections.",
    "Don't forget to apply sunscreen to your ears, neck, and hands.",
    "Use a humidifier in dry environments to prevent skin dryness.",
    "Exfoliate gently 1-2 times per week to remove dead skin cells.",
    "Wearing protective clothing reduces UV damage significantly."
];

function initChatbot() {
    const toggle = document.getElementById('chatbotToggle');
    const panel = document.getElementById('chatbotPanel');
    const input = document.getElementById('chatInput');
    const sendBtn = document.getElementById('chatSendBtn');
    const close = document.getElementById('chatClose');

    if (!toggle || !panel) return;

    toggle.addEventListener('click', () => {
        panel.classList.toggle('active');
    });

    if (close) {
        close.addEventListener('click', () => {
            panel.classList.remove('active');
        });
    }

    if (sendBtn && input) {
        sendBtn.addEventListener('click', () => sendChatMessage(input));
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendChatMessage(input);
        });
    }
}

function sendChatMessage(input) {
    const text = input.value.trim();
    if (!text) return;

    addChatMessage(text, 'user');
    input.value = '';

    // Simulate bot response
    setTimeout(() => {
        const tip = SKINCARE_TIPS[Math.floor(Math.random() * SKINCARE_TIPS.length)];
        const response = getBotResponse(text, tip);
        addChatMessage(response, 'bot');
    }, 500);
}

function getBotResponse(userMessage, tip) {
    const msg = userMessage.toLowerCase();

    if (msg.includes('hello') || msg.includes('hi') || msg.includes('hey')) {
        return "Hello! 👋 I'm your Skincare Assistant. Ask me about skin health, sun protection, or any skin concern!";
    }
    if (msg.includes('sunscreen') || msg.includes('sun') || msg.includes('spf')) {
        return "☀️ Sunscreen is crucial! Use SPF 30+ daily, reapply every 2 hours outdoors, and choose broad-spectrum protection against both UVA and UVB rays.";
    }
    if (msg.includes('acne') || msg.includes('pimple')) {
        return "For acne, try: 1) Gentle cleansing twice daily, 2) Non-comedogenic products, 3) Salicylic acid or benzoyl peroxide treatments, 4) Don't pick! Consult a dermatologist for persistent acne.";
    }
    if (msg.includes('melanoma') || msg.includes('cancer') || msg.includes('mole')) {
        return "⚠️ Skin cancer is serious. Use the ABCDE rule for moles: Asymmetry, Border irregularity, Color changes, Diameter >6mm, Evolving appearance. See a dermatologist immediately for any suspicious changes.";
    }
    if (msg.includes('dry') || msg.includes('moistur')) {
        return "💧 For dry skin: Use a gentle cleanser, apply moisturizer on damp skin, use a humidifier, drink enough water, and look for ingredients like hyaluronic acid and ceramides.";
    }
    if (msg.includes('thank')) {
        return "You're welcome! 😊 Take care of your skin and don't hesitate to consult a professional for any concerns.";
    }

    return `💡 Here's a skin health tip: ${tip}`;
}

function addChatMessage(text, sender) {
    const container = document.getElementById('chatMessages');
    if (!container) return;

    const msg = document.createElement('div');
    msg.className = `chat-message ${sender}`;
    msg.textContent = text;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
}

// ──── Initialize ────
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    setActiveNav();
    displayUserInfo();
    initChatbot();
});
