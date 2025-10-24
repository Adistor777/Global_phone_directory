// API Configuration
const API_URL = 'http://127.0.0.1:8000/api';

// Global state
let currentUser = null;

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('App initialized');
    
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
        currentUser = JSON.parse(user);
        console.log('User logged in:', currentUser);
        initializeApp();
    } else {
        console.log('No user logged in, showing auth page');
        showPage('authPage');
    }
    
    // Setup event listeners
    setupEventListeners();
    
    // Setup navigation
    setupNavigation();
    
    // Handle URL hash
    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);
});

// ============================================
// EVENT LISTENERS SETUP
// ============================================

function setupEventListeners() {
    // Auth form listeners
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
    
    // Tab switching
    const loginTab = document.getElementById('loginTab');
    const signupTab = document.getElementById('signupTab');
    
    if (loginTab) {
        loginTab.addEventListener('click', () => switchTab('login'));
    }
    
    if (signupTab) {
        signupTab.addEventListener('click', () => switchTab('signup'));
    }
    
    // Contact form
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleCreateContact);
    }
    
    // Spam form
    const spamForm = document.getElementById('spamForm');
    if (spamForm) {
        spamForm.addEventListener('submit', handleReportSpam);
    }
    
    // Search form
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
}

// ============================================
// NAVIGATION
// ============================================

function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('href').substring(1);
            window.location.hash = target;
        });
    });
}

function handleHashChange() {
    const hash = window.location.hash.substring(1) || 'dashboard';
    console.log('Hash changed to:', hash);
    
    const token = localStorage.getItem('access_token');
    
    // If not logged in, force to auth page
    if (!token && hash !== 'auth') {
        window.location.hash = 'auth';
        return;
    }
    
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${hash}`) {
            link.classList.add('active');
        }
    });
    
    // Route to appropriate page
    switch(hash) {
        case 'auth':
            showPage('authPage');
            break;
        case 'dashboard':
            showPage('dashboardPage');
            loadDashboard();
            break;
        case 'search':
            showPage('searchPage');
            break;
        case 'contacts':
            showPage('contactsPage');
            loadContacts();
            break;
        case 'spam':
            showPage('spamPage');
            loadSpamStats();
            break;
        default:
            showPage('dashboardPage');
            loadDashboard();
    }
}

function showPage(pageId) {
    console.log('Showing page:', pageId);
    
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
        page.style.display = 'none';
    });
    
    // Show requested page
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');
        targetPage.style.display = pageId === 'authPage' ? 'flex' : 'block';
    }
    
    // Show/hide navbar based on page
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.style.display = pageId === 'authPage' ? 'none' : 'block';
    }
}

// ============================================
// AUTHENTICATION
// ============================================

function switchTab(tab) {
    const loginTab = document.getElementById('loginTab');
    const signupTab = document.getElementById('signupTab');
    const loginView = document.getElementById('loginView');
    const signupView = document.getElementById('signupView');
    
    if (tab === 'login') {
        loginTab.classList.add('active');
        signupTab.classList.remove('active');
        loginView.classList.add('active');
        signupView.classList.remove('active');
    } else {
        signupTab.classList.add('active');
        loginTab.classList.remove('active');
        signupView.classList.add('active');
        loginView.classList.remove('active');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const submitBtn = document.getElementById('loginSubmit');
    const errorDiv = document.getElementById('loginError');
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';
    errorDiv.style.display = 'none';

    const data = {
        phone_number: document.getElementById('loginPhone').value.trim(),
        password: document.getElementById('loginPassword').value
    };

    // Basic validation
    if (!data.phone_number) {
        showError(errorDiv, 'Phone number is required');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
        return;
    }

    if (!data.password) {
        showError(errorDiv, 'Password is required');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
        return;
    }

    try {
        console.log('Sending login request for:', data.phone_number);
        
        const response = await fetch(`${API_URL}/user/login`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data)
        });

        console.log('Login response status:', response.status);
        const result = await response.json();
        console.log('Login response data:', result);

        if (response.ok) {
            // ✅ SUCCESS (200 or 201)
            console.log('✅ Login successful!');
            
            // Store tokens
            localStorage.setItem('access_token', result.access_token);
            localStorage.setItem('refresh_token', result.refresh_token);
            localStorage.setItem('user', JSON.stringify(result.user));
            currentUser = result.user;
            
            // Show success message
            const isNewUser = response.status === 201;
            showSuccessMessage(
                isNewUser ? '🎉 Account Created!' : '✅ Welcome Back!',
                isNewUser ? 'Your account has been created. Loading dashboard...' : 'Login successful! Loading dashboard...'
            );
            
            // Clear form
            document.getElementById('loginForm').reset();
            
            // Redirect after delay
            setTimeout(() => {
                window.location.hash = 'dashboard';
                initializeApp();
            }, 2000);
        } else {
            // ❌ ERROR
            console.error('❌ Login failed:', result);
            
            let errorMessage = 'Login failed. Please try again.';
            
            if (result.error) {
                errorMessage = result.error;
            } else if (result.phone_number) {
                errorMessage = Array.isArray(result.phone_number) 
                    ? result.phone_number[0] 
                    : result.phone_number;
            } else if (typeof result === 'object') {
                const firstError = Object.values(result)[0];
                errorMessage = Array.isArray(firstError) ? firstError[0] : firstError;
            }
            
            showError(errorDiv, errorMessage);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Login';
        }
    } catch (error) {
        console.error('❌ Network error:', error);
        showError(errorDiv, 'Network error. Please check your connection and try again.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
    }
}

async function handleSignup(e) {
    e.preventDefault();
    const submitBtn = document.getElementById('signupSubmit');
    const errorDiv = document.getElementById('signupError');
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating Account...';
    errorDiv.style.display = 'none';

    const data = {
        first_name: document.getElementById('signupFirstName').value.trim(),
        last_name: document.getElementById('signupLastName').value.trim(),
        phone_number: document.getElementById('signupPhone').value.trim(),
        email: document.getElementById('signupEmail').value.trim(),
        password: document.getElementById('signupPassword').value
    };

    // Basic validation
    if (!data.first_name) {
        showError(errorDiv, 'First name is required');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Account';
        return;
    }

    if (!data.phone_number) {
        showError(errorDiv, 'Phone number is required');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Account';
        return;
    }

    if (!data.password || data.password.length < 5) {
        showError(errorDiv, 'Password must be at least 5 characters');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Account';
        return;
    }

    try {
        console.log('Sending signup request:', { ...data, password: '***' });
        
        const response = await fetch(`${API_URL}/user/signup`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data)
        });

        console.log('Signup response status:', response.status);
        const result = await response.json();
        console.log('Signup response data:', result);

        if (response.ok) {
            // ✅ SUCCESS
            console.log('✅ Signup successful!');
            
            // Store tokens
            localStorage.setItem('access_token', result.access_token);
            localStorage.setItem('refresh_token', result.refresh_token);
            localStorage.setItem('user', JSON.stringify(result.user));
            currentUser = result.user;
            
            // Show success message
            showSuccessMessage('🎉 Account Created!', 'Welcome! Redirecting to your dashboard...');
            
            // Clear form
            document.getElementById('signupForm').reset();
            
            // Redirect after delay
            setTimeout(() => {
                window.location.hash = 'dashboard';
                initializeApp();
            }, 2000);
        } else {
            // ❌ ERROR
            console.error('❌ Signup failed:', result);
            
            // Handle different error formats
            let errorMessage = 'Signup failed. Please try again.';
            
            if (result.error) {
                errorMessage = result.error;
            } else if (result.phone_number) {
                errorMessage = Array.isArray(result.phone_number) 
                    ? result.phone_number[0] 
                    : result.phone_number;
            } else if (typeof result === 'object') {
                // Extract first error from object
                const firstError = Object.values(result)[0];
                errorMessage = Array.isArray(firstError) ? firstError[0] : firstError;
            }
            
            showError(errorDiv, errorMessage);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Create Account';
        }
    } catch (error) {
        console.error('❌ Network error:', error);
        showError(errorDiv, 'Network error. Please check your connection and try again.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Account';
    }
}

function logout() {
    console.log('Logging out...');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    currentUser = null;
    window.location.hash = 'auth';
    showPage('authPage');
}

// ============================================
// HELPER FUNCTIONS
// ============================================

function showError(errorDiv, message) {
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    errorDiv.classList.add('show');
}

function showSuccessMessage(title, message) {
    // Remove any existing success overlay
    const existing = document.querySelector('.success-overlay');
    if (existing) existing.remove();
    
    // Create success overlay
    const overlay = document.createElement('div');
    overlay.className = 'success-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.85);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        animation: fadeIn 0.3s ease;
    `;
    
    const successBox = document.createElement('div');
    successBox.style.cssText = `
        background: white;
        padding: 50px 40px;
        border-radius: 20px;
        text-align: center;
        max-width: 400px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        animation: slideUp 0.4s ease;
    `;
    
    successBox.innerHTML = `
        <div style="font-size: 80px; margin-bottom: 20px; animation: bounce 0.6s ease;">✅</div>
        <h2 style="color: #2e7d32; margin-bottom: 15px; font-size: 28px;">${title}</h2>
        <p style="color: #666; font-size: 16px; line-height: 1.5;">${message}</p>
        <div style="margin-top: 25px;">
            <div class="spinner" style="
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            "></div>
        </div>
    `;
    
    overlay.appendChild(successBox);
    document.body.appendChild(overlay);
    
    // Auto-remove after 2 seconds
    setTimeout(() => {
        overlay.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => overlay.remove(), 300);
    }, 2000);
}

async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        throw new Error('No authentication token found');
    }
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    const response = await fetch(url, mergedOptions);
    
    if (response.status === 401) {
        // Token expired or invalid
        logout();
        throw new Error('Authentication failed');
    }
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Request failed');
    }
    
    return response.json();
}

function initializeApp() {
    console.log('Initializing app...');
    showPage('dashboardPage');
    loadDashboard();
}

// ============================================
// DASHBOARD
// ============================================

async function loadDashboard() {
    console.log('Loading dashboard...');
    
    const token = localStorage.getItem('access_token');
    if (!token) {
        console.log('No token, redirecting to auth');
        window.location.hash = 'auth';
        return;
    }
    
    try {
        const data = await fetchWithAuth(`${API_URL}/dashboard`);
        console.log('Dashboard data:', data);
        displayDashboardData(data);
    } catch (error) {
        console.error('Dashboard error:', error);
        if (error.message.includes('Authentication failed')) {
            // Already logged out by fetchWithAuth
            return;
        }
        showDashboardError('Failed to load dashboard. Please try again.');
    }
}

function displayDashboardData(data) {
    // Update user info in navbar
    const userNameEl = document.querySelector('.user-name');
    const userPhoneEl = document.querySelector('.user-phone');
    
    if (userNameEl && data.user) {
        userNameEl.textContent = data.user.full_name || data.user.first_name;
    }
    
    if (userPhoneEl && data.user) {
        userPhoneEl.textContent = data.user.phone_number;
    }
    
    // Update stats
    document.getElementById('totalInteractions').textContent = data.total_interactions || 0;
    document.getElementById('totalCalls').textContent = data.interaction_stats?.calls || 0;
    document.getElementById('totalMessages').textContent = data.interaction_stats?.messages || 0;
    document.getElementById('totalSpamReports').textContent = data.interaction_stats?.spam_reports || 0;
    document.getElementById('timesReported').textContent = data.times_reported || 0;
    document.getElementById('reportsMade').textContent = data.reports_made || 0;
    
    // Display recent interactions
    displayRecentInteractions(data.recent_interactions || []);
}

function displayRecentInteractions(interactions) {
    const container = document.getElementById('recentInteractionsList');
    
    if (!interactions || interactions.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No recent interactions</p></div>';
        return;
    }
    
    container.innerHTML = interactions.map(interaction => {
        const icon = getInteractionIcon(interaction.interaction_type);
        const time = formatDate(interaction.created_at);
        
        return `
            <div class="interaction-item">
                <div class="rank-badge">${icon}</div>
                <div class="interaction-info">
                    <div class="interaction-type">${formatInteractionType(interaction.interaction_type)}</div>
                    <div class="interaction-details">
                        ${interaction.receiver_name || interaction.receiver_phone}
                    </div>
                </div>
                <div class="interaction-time">${time}</div>
            </div>
        `;
    }).join('');
}

function getInteractionIcon(type) {
    switch(type) {
        case 'call': return '📞';
        case 'message': return '💬';
        case 'spam_report': return '🚫';
        case 'contact_added': return '➕';
        default: return '📋';
    }
}

function formatInteractionType(type) {
    switch(type) {
        case 'call': return 'Call';
        case 'message': return 'Message';
        case 'spam_report': return 'Spam Report';
        case 'contact_added': return 'Contact Added';
        default: return type;
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    return date.toLocaleDateString();
}

function showDashboardError(message) {
    const container = document.querySelector('.container');
    if (container) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>Error Loading Dashboard</h3>
                <p>${message}</p>
            </div>
        `;
    }
}

// ============================================
// SEARCH
// ============================================

async function handleSearch(e) {
    e.preventDefault();
    
    const query = document.getElementById('searchQuery').value.trim();
    const submitBtn = document.getElementById('searchSubmit');
    const resultsContainer = document.getElementById('searchResults');
    
    if (!query) {
        resultsContainer.innerHTML = '<div class="empty-state"><p>Please enter a search term</p></div>';
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Searching...';
    resultsContainer.innerHTML = '<div class="loading"><div class="spinner"></div><p>Searching...</p></div>';
    
    try {
        const data = await fetchWithAuth(`${API_URL}/search?q=${encodeURIComponent(query)}`);
        console.log('Search results:', data);
        displaySearchResults(data.results || [], query);
    } catch (error) {
        console.error('Search error:', error);
        resultsContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>Search Failed</h3>
                <p>${error.message}</p>
            </div>
        `;
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Search';
    }
}

function displaySearchResults(results, query) {
    const container = document.getElementById('searchResults');
    
    if (!results || results.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <h3>No Results Found</h3>
                <p>No results found for "${query}"</p>
                <ul>
                    <li>Try a different search term</li>
                    <li>Check spelling</li>
                    <li>Try searching by phone number</li>
                </ul>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="results-header">
            <h3>Search Results</h3>
            <p class="results-count">${results.length} result${results.length !== 1 ? 's' : ''} found</p>
        </div>
        ${results.map((result, index) => `
            <div class="result-item">
                <div class="result-number">#${index + 1}</div>
                <div class="result-info">
                    <h4>${result.name}</h4>
                    <div class="result-phone">${result.phone_number}</div>
                    <div class="result-meta">
                        ${result.is_registered ? '<span class="badge badge-registered">✓ Registered User</span>' : '<span class="badge badge-contact">📇 Contact</span>'}
                        ${result.spam_likelihood > 0 ? `<span class="badge badge-spam">🚫 ${result.spam_likelihood} spam report${result.spam_likelihood !== 1 ? 's' : ''}</span>` : '<span class="badge badge-safe">✓ No spam reports</span>'}
                        <span class="badge badge-info">Match: ${result.match_score}%</span>
                    </div>
                </div>
            </div>
        `).join('')}
    `;
}

// ============================================
// CONTACTS
// ============================================

async function loadContacts() {
    console.log('Loading contacts...');
    
    try {
        const contacts = await fetchWithAuth(`${API_URL}/contact`);
        console.log('Contacts:', contacts);
        displayContacts(contacts);
        
        // Load top contacts
        const topContacts = await fetchWithAuth(`${API_URL}/interactions/top?limit=10`);
        console.log('Top contacts:', topContacts);
        displayTopContacts(topContacts);
    } catch (error) {
        console.error('Error loading contacts:', error);
    }
}

function displayContacts(contacts) {
    const container = document.getElementById('contactsList');
    
    if (!contacts || contacts.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No contacts yet. Add your first contact above!</p></div>';
        return;
    }
    
    container.innerHTML = contacts.map((contact, index) => `
        <div class="result-item">
            <div class="result-number">#${index + 1}</div>
            <div class="result-info">
                <h4>${contact.first_name} ${contact.last_name || ''}</h4>
                <div class="result-phone">${contact.phone_number}</div>
                <div class="result-meta">
                    <span class="badge badge-contact">Added ${formatDate(contact.created_at)}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function displayTopContacts(contacts) {
    const container = document.getElementById('topContactsList');
    
    if (!contacts || contacts.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No interaction data yet</p></div>';
        return;
    }
    
    container.innerHTML = contacts.map((contact, index) => `
        <div class="interaction-item">
            <div class="rank-badge ${index < 3 ? 'danger' : ''}">#${index + 1}</div>
            <div class="interaction-info">
                <div class="interaction-type">${contact.contact_name || contact.contact_phone}</div>
                <div class="interaction-details">
                    💬 ${contact.interaction_count} interaction${contact.interaction_count !== 1 ? 's' : ''}
                    ${contact.is_registered ? ' • ✓ Registered' : ''}
                </div>
            </div>
        </div>
    `).join('');
}

async function handleCreateContact(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('contactSubmit');
    const messageDiv = document.getElementById('contactMessage');
    
    const data = {
        first_name: document.getElementById('contactFirstName').value.trim(),
        last_name: document.getElementById('contactLastName').value.trim(),
        phone_number: document.getElementById('contactPhone').value.trim()
    };
    
    if (!data.first_name || !data.phone_number) {
        showContactMessage('First name and phone number are required', 'error');
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Saving...';
    messageDiv.style.display = 'none';
    
    try {
        const result = await fetchWithAuth(`${API_URL}/contact`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        console.log('Contact created:', result);
        showContactMessage('✅ Contact added successfully!', 'success');
        document.getElementById('contactForm').reset();
        
        // Reload contacts
        setTimeout(() => {
            loadContacts();
        }, 1000);
    } catch (error) {
        console.error('Error creating contact:', error);
        showContactMessage(error.message || 'Failed to add contact', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '💾 Save Contact';
    }
}

function showContactMessage(message, type) {
    const messageDiv = document.getElementById('contactMessage');
    messageDiv.textContent = message;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
}

// ============================================
// SPAM REPORTING
// ============================================

async function loadSpamStats() {
    console.log('Loading spam stats...');
    
    try {
        const stats = await fetchWithAuth(`${API_URL}/interactions/spam-stats`);
        console.log('Spam stats:', stats);
        displaySpamStats(stats);
    } catch (error) {
        console.error('Error loading spam stats:', error);
    }
}

function displaySpamStats(stats) {
    const container = document.getElementById('spamStatsList');
    
    if (!stats || stats.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No spam reports yet</p></div>';
        return;
    }
    
    container.innerHTML = stats.map((stat, index) => `
        <div class="interaction-item spam-item">
            <div class="rank-badge danger">#${index + 1}</div>
            <div class="interaction-info">
                <div class="interaction-type">${stat.phone_number}</div>
                <div class="interaction-details">
                    🚫 ${stat.spam_count} report${stat.spam_count !== 1 ? 's' : ''} from ${stat.unique_reporters} user${stat.unique_reporters !== 1 ? 's' : ''}
                    ${stat.latest_description ? ` • "${stat.latest_description}"` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

async function handleReportSpam(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('spamSubmit');
    const messageDiv = document.getElementById('spamMessage');
    
    const data = {
        phone_number: document.getElementById('spamPhone').value.trim(),
        description: document.getElementById('spamDescription').value.trim()
    };
    
    if (!data.phone_number) {
        showSpamMessage('Phone number is required', 'error');
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    messageDiv.style.display = 'none';
    
    try {
        const result = await fetchWithAuth(`${API_URL}/spam`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        console.log('Spam reported:', result);
        showSpamMessage('✅ Spam reported successfully!', 'success');
        document.getElementById('spamForm').reset();
        
        // Reload spam stats
        setTimeout(() => {
            loadSpamStats();
        }, 1000);
    } catch (error) {
        console.error('Error reporting spam:', error);
        showSpamMessage(error.message || 'Failed to report spam', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '📢 Submit Report';
    }
}

function showSpamMessage(message, type) {
    const messageDiv = document.getElementById('spamMessage');
    messageDiv.textContent = message;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
}

async function applySpamFilters() {
    const minReports = document.getElementById('minReportsFilter').value;
    const dateRange = document.getElementById('dateRangeFilter').value;
    
    let url = `${API_URL}/interactions/spam-stats`;
    const params = [];
    
    if (minReports && minReports !== 'all') {
        params.push(`min_reports=${minReports}`);
    }
    
    if (dateRange && dateRange !== 'all') {
        const now = new Date();
        let startDate;
        
        if (dateRange === '7') {
            startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        } else if (dateRange === '30') {
            startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        } else if (dateRange === '90') {
            startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
        }
        
        if (startDate) {
            params.push(`start_date=${startDate.toISOString()}`);
        }
    }
    
    if (params.length > 0) {
        url += '?' + params.join('&');
    }
    
    try {
        const stats = await fetchWithAuth(url);
        console.log('Filtered spam stats:', stats);
        displaySpamStats(stats);
    } catch (error) {
        console.error('Error loading filtered spam stats:', error);
    }
}