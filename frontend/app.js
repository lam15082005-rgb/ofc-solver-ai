// OFC Solver AI - Frontend Application

// API URL - empty string means same origin
const API_URL = '';

// State
let authToken = localStorage.getItem('auth_token');
let currentUser = null;
let sessionId = null;

// DOM Elements
const loginPage = document.getElementById('login-page');
const chatPage = document.getElementById('chat-page');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const userDisplay = document.getElementById('user-display');
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (authToken) {
        validateToken();
    } else {
        showLoginPage();
    }
    
    setupEventListeners();
    initCardSelector();
});

// Event Listeners
function setupEventListeners() {
    loginForm.addEventListener('submit', handleLogin);
    logoutBtn.addEventListener('click', handleLogout);
    chatForm.addEventListener('submit', handleSendMessage);
    
    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 200) + 'px';
    });
    
    // Submit on Enter (Shift+Enter for new line)
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
    
    // Example query buttons
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('example-btn')) {
            const query = e.target.dataset.query;
            chatInput.value = query;
            chatInput.focus();
        }
    });
}

// XHR-based request helper (works with tunnel basic auth where fetch() is blocked)
function xhrRequest(url, method, headers, body) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open(method || 'GET', url, true);
        if (headers) {
            Object.keys(headers).forEach(k => xhr.setRequestHeader(k, headers[k]));
        }
        xhr.onload = function() {
            let jsonData = null;
            try { jsonData = JSON.parse(xhr.responseText); } catch(e) { /* not json */ }
            resolve({ status: xhr.status, ok: xhr.status >= 200 && xhr.status < 300, json: () => Promise.resolve(jsonData), text: () => Promise.resolve(xhr.responseText) });
        };
        xhr.onerror = function() { reject(new Error('Network error')); };
        xhr.send(body || null);
    });
}

// API Helpers
async function apiRequest(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (authToken) {
        headers['X-App-Auth'] = `Bearer ${authToken}`;
    }
    
    const response = await xhrRequest(`${API_URL}${endpoint}`, options.method || 'GET', headers, options.body);
    
    if (response.status === 401) {
        handleLogout();
        throw new Error('Session expired');
    }
    
    return response;
}

// Auth Functions
async function validateToken() {
    try {
        const response = await apiRequest('/auth/me');
        if (response.ok) {
            currentUser = await response.json();
            showChatPage();
        } else {
            handleLogout();
        }
    } catch (error) {
        handleLogout();
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    loginBtn.classList.add('loading');
    loginError.textContent = '';
    
    try {
        const response = await xhrRequest(`${API_URL}/auth/login`, 'POST', { 'Content-Type': 'application/json' }, JSON.stringify({ username, password }));
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('auth_token', authToken);
            currentUser = {
                username: data.username,
                display_name: data.display_name
            };
            showChatPage();
        } else {
            loginError.textContent = data.detail || 'Login failed';
        }
    } catch (error) {
        loginError.textContent = 'Connection error. Please try again.';
    } finally {
        loginBtn.classList.remove('loading');
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    sessionId = null;
    localStorage.removeItem('auth_token');
    showLoginPage();
}

// Page Navigation
function showLoginPage() {
    loginPage.classList.remove('hidden');
    chatPage.classList.add('hidden');
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
    loginError.textContent = '';
}

function showChatPage() {
    loginPage.classList.add('hidden');
    chatPage.classList.remove('hidden');
    userDisplay.textContent = currentUser?.display_name || currentUser?.username;
    chatInput.focus();
}

// Chat Functions
async function handleSendMessage(e) {
    e.preventDefault();
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Clear input
    chatInput.value = '';
    chatInput.style.height = 'auto';
    
    // Remove welcome message if present
    const welcome = chatMessages.querySelector('.welcome-message');
    if (welcome) welcome.remove();
    
    // Add user message
    addMessage('user', message);
    
    // Add thinking indicator
    const thinkingEl = addThinkingIndicator();
    
    // Disable input while processing
    sendBtn.disabled = true;
    
    try {
        const response = await apiRequest('/chat', {
            method: 'POST',
            body: JSON.stringify({ 
                message,
                session_id: sessionId 
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            sessionId = data.session_id;
            thinkingEl.remove();
            addMessage('assistant', data.response);
        } else {
            thinkingEl.remove();
            addMessage('assistant', `Error: ${data.detail || 'Something went wrong'}`);
        }
    } catch (error) {
        thinkingEl.remove();
        addMessage('assistant', `Error: ${error.message}`);
    } finally {
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

function addMessage(role, content) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${role}`;
    
    const avatar = role === 'user' ? '👤' : '🎴';
    const name = role === 'user' ? (currentUser?.display_name || 'You') : 'OFC Solver AI';
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageEl.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-name">${name}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-body">${formatMessage(content)}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageEl);
    scrollToBottom();
}

function addThinkingIndicator() {
    const el = document.createElement('div');
    el.className = 'message assistant thinking';
    el.innerHTML = `
        <div class="message-avatar">🎴</div>
        <div class="message-content">
            <div class="thinking">
                <div class="thinking-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <span>Thinking...</span>
            </div>
        </div>
    `;
    chatMessages.appendChild(el);
    scrollToBottom();
    return el;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Message Formatting
function formatMessage(content) {
    // Escape HTML
    let formatted = escapeHtml(content);
    
    // Format code blocks
    formatted = formatted.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre><code class="language-${lang}">${code.trim()}</code></pre>`;
    });
    
    // Format inline code
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Format bold
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Format headers
    formatted = formatted.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    formatted = formatted.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    
    // Format lists
    formatted = formatted.replace(/^\* (.+)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/^- (.+)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>');
    
    // Wrap consecutive list items
    formatted = formatted.replace(/(<li>.*<\/li>\n?)+/g, (match) => {
        return '<ul>' + match + '</ul>';
    });
    
    // Format card visualizations (ASCII art blocks)
    formatted = formatCardVisualizations(formatted);
    
    // Format paragraphs
    formatted = formatted.split('\n\n').map(para => {
        if (para.startsWith('<') || para.trim() === '') return para;
        return `<p>${para.replace(/\n/g, '<br>')}</p>`;
    }).join('\n');
    
    return formatted;
}

function formatCardVisualizations(content) {
    // Detect ASCII card visualizations (blocks with ┌───┐ patterns)
    const cardBlockRegex = /(═+[\s\S]*?═+)/g;
    
    return content.replace(cardBlockRegex, (match) => {
        if (match.includes('┌───┐') || match.includes('TOP') || match.includes('MIDDLE') || match.includes('BOTTOM')) {
            return `<pre class="card-visualization">${match}</pre>`;
        }
        return match;
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============== Card Selector ==============

const RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K'];
const SUITS = [
    { symbol: '♠', name: 'spades', color: 'black', char: 's' },
    { symbol: '♥', name: 'hearts', color: 'red', char: 'h' },
    { symbol: '♦', name: 'diamonds', color: 'red', char: 'd' },
    { symbol: '♣', name: 'clubs', color: 'black', char: 'c' }
];

let selectedCards = [];
const MAX_CARDS = 13;

// DOM Elements for card selector (will be initialized in initCardSelector)
let solverBtn, cardSelectorModal, closeModalBtn, cardGrid, selectedCountEl, selectedCardsDisplay, clearSelectionBtn, solveCardsBtn;

// Initialize card selector
function initCardSelector() {
    console.log('Initializing card selector...');
    
    // Get DOM elements
    solverBtn = document.getElementById('solver-btn');
    cardSelectorModal = document.getElementById('card-selector-modal');
    closeModalBtn = document.getElementById('close-modal');
    cardGrid = document.getElementById('card-grid');
    selectedCountEl = document.getElementById('selected-count');
    selectedCardsDisplay = document.getElementById('selected-cards-display');
    clearSelectionBtn = document.getElementById('clear-selection');
    solveCardsBtn = document.getElementById('solve-btn');
    
    console.log('Solver button found:', !!solverBtn);
    console.log('Modal found:', !!cardSelectorModal);
    
    if (!solverBtn || !cardSelectorModal) {
        console.error('Card selector elements not found');
        return;
    }
    
    // Generate all cards
    generateCardGrid();
    console.log('Card grid generated');
    
    // Event listeners
    solverBtn.addEventListener('click', () => {
        console.log('Solver button clicked!');
        openCardSelector();
    });
    closeModalBtn.addEventListener('click', closeCardSelector);
    clearSelectionBtn.addEventListener('click', clearSelection);
    solveCardsBtn.addEventListener('click', solveSelectedCards);
    
    // Close modal when clicking outside
    cardSelectorModal.addEventListener('click', (e) => {
        if (e.target === cardSelectorModal) {
            closeCardSelector();
        }
    });
}

function generateCardGrid() {
    if (!cardGrid) {
        console.error('Card grid element not found!');
        return;
    }
    
    console.log('Generating card grid...');
    cardGrid.innerHTML = '';
    
    // Add all 52 cards
    for (const rank of RANKS) {
        for (const suit of SUITS) {
            const card = createCard(rank, suit);
            cardGrid.appendChild(card);
        }
    }
    
    // Add 4 jokers
    for (let i = 1; i <= 4; i++) {
        const joker = createJoker(i);
        cardGrid.appendChild(joker);
    }
    
    console.log('Generated', cardGrid.children.length, 'cards');
}

function createCard(rank, suit) {
    const cardEl = document.createElement('div');
    cardEl.className = `playing-card ${suit.color}`;
    cardEl.dataset.card = `${rank}${suit.char}`;
    
    cardEl.innerHTML = `
        <div class="card-rank">${rank}</div>
        <div class="card-suit">${suit.symbol}</div>
    `;
    
    cardEl.addEventListener('click', () => toggleCard(cardEl, `${rank}${suit.char}`));
    
    return cardEl;
}

function createJoker(index) {
    const jokerEl = document.createElement('div');
    jokerEl.className = 'playing-card joker';
    jokerEl.dataset.card = `*${index}`;
    jokerEl.textContent = '🃏';
    
    // Pass the joker as a single "*" - solver handles multiple jokers
    jokerEl.addEventListener('click', () => toggleCard(jokerEl, `*`));
    
    return jokerEl;
}

function toggleCard(cardEl, cardValue) {
    if (cardEl.classList.contains('disabled')) return;
    
    if (cardEl.classList.contains('selected')) {
        // Deselect
        cardEl.classList.remove('selected');
        selectedCards = selectedCards.filter(c => c !== cardValue);
    } else {
        // Select
        if (selectedCards.length >= MAX_CARDS) {
            return; // Max cards reached
        }
        cardEl.classList.add('selected');
        selectedCards.push(cardValue);
    }
    
    updateSelectedDisplay();
    updateCardStates();
}

function updateSelectedDisplay() {
    selectedCountEl.textContent = selectedCards.length;
    
    // Update mini card display
    selectedCardsDisplay.innerHTML = '';
    selectedCards.forEach(cardStr => {
        const mini = createMiniCard(cardStr);
        selectedCardsDisplay.appendChild(mini);
    });
    
    // Enable/disable solve button
    solveCardsBtn.disabled = selectedCards.length !== MAX_CARDS;
}

function createMiniCard(cardStr) {
    const mini = document.createElement('div');
    
    if (cardStr === '*') {
        mini.className = 'selected-card-mini joker';
        mini.textContent = '🃏';
    } else {
        const rank = cardStr[0];
        const suitChar = cardStr[1];
        const suit = SUITS.find(s => s.char === suitChar);
        
        mini.className = `selected-card-mini ${suit.color}`;
        mini.innerHTML = `
            <div class="card-rank">${rank}</div>
            <div class="card-suit">${suit.symbol}</div>
        `;
    }
    
    return mini;
}

function updateCardStates() {
    const allCards = cardGrid.querySelectorAll('.playing-card');
    
    if (selectedCards.length >= MAX_CARDS) {
        // Disable all non-selected cards
        allCards.forEach(card => {
            if (!card.classList.contains('selected')) {
                card.classList.add('disabled');
            }
        });
    } else {
        // Enable all cards
        allCards.forEach(card => {
            card.classList.remove('disabled');
        });
    }
}

function clearSelection() {
    selectedCards = [];
    const allCards = cardGrid.querySelectorAll('.playing-card');
    allCards.forEach(card => {
        card.classList.remove('selected', 'disabled');
    });
    updateSelectedDisplay();
}

function openCardSelector() {
    console.log('Opening card selector modal...');
    cardSelectorModal.classList.remove('hidden');
    clearSelection(); // Start fresh each time
}

function closeCardSelector() {
    cardSelectorModal.classList.add('hidden');
}

async function solveSelectedCards() {
    if (selectedCards.length !== MAX_CARDS) {
        return;
    }
    
    // Close modal
    closeCardSelector();
    
    // Format cards as space-separated string
    const cardsString = selectedCards.join(' ');
    
    // Send solver request through chat agent so it has context for follow-ups
    const welcome = chatMessages.querySelector('.welcome-message');
    if (welcome) welcome.remove();
    
    // Send to chat agent with "Solve:" prefix
    const message = `Solve: ${cardsString}`;
    addMessage('user', message);
    
    // Add thinking indicator
    const thinkingEl = addThinkingIndicator();
    
    // Disable solver button while processing
    solverBtn.disabled = true;
    
    try {
        const response = await apiRequest('/chat', {
            method: 'POST',
            body: JSON.stringify({ 
                message: message,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        thinkingEl.remove();
        
        if (response.ok) {
            // Agent returns the formatted response
            addMessage('assistant', data.response);
            
            // Update session ID if provided
            if (data.session_id) {
                sessionId = data.session_id;
            }
        } else {
            addMessage('assistant', `Error: ${data.detail || 'Failed to solve'}`);
        }
    } catch (error) {
        thinkingEl.remove();
        addMessage('assistant', `Error: ${error.message}`);
    } finally {
        solverBtn.disabled = false;
    }
}
