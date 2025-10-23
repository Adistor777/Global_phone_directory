// API Configuration
const API_BASE = 'http://127.0.0.1:8000/api';

// Application State
const app = {
    user: null,
    token: null,
    currentView: 'dashboard',

    // Initialize App
    init() {
        this.checkAuth();
        this.attachEventListeners();
    },

    // Check if user is authenticated
    checkAuth() {
        const token = localStorage.getItem('access_token');
        const user = localStorage.getItem('user');

        if (token && user) {
            this.token = token;
            this.user = JSON.parse(user);
            this.showApp();
            this.updateUserInfo();
            this.loadDashboard();
        } else {
            this.showAuth();
        }
    },

    // Show/Hide Pages
    showAuth() {
        document.getElementById('authPage').classList.add('active');
        document.getElementById('appPage').classList.remove('active');
    },

    showApp() {
        document.getElementById('authPage').classList.remove('active');
        document.getElementById('appPage').classList.add('active');
    },

    // Auth Tab Switching
    showTab(tab) {
        const tabs = document.querySelectorAll('.tab');
        tabs.forEach(t => t.classList.remove('active'));

        if (tab === 'login') {
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('signupForm').style.display = 'none';
            tabs[0].classList.add('active');
        } else {
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('signupForm').style.display = 'block';
            tabs[1].classList.add('active');
        }
    },

    // Navigate between views
    navigate(view) {
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

        document.getElementById(`${view}View`).classList.add('active');
        this.currentView = view;

        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            if (link.textContent.toLowerCase().includes(view)) {
                link.classList.add('active');
            }
        });

        if (view === 'dashboard') this.loadDashboard();
        if (view === 'contacts') this.loadTopContacts();
        if (view === 'spam') this.loadSpamStats();
    },

    // Update user info in navbar
    updateUserInfo() {
        if (this.user) {
            document.getElementById('userName').textContent = this.user.full_name || this.user.first_name;
            document.getElementById('userPhone').textContent = this.user.phone_number;
        }
    },

    // Logout
    logout() {
        if (confirm('Are you sure you want to logout?')) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            this.user = null;
            this.token = null;
            this.showAuth();
        }
    },

    // Show/Hide loading
    showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    },

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    },

    // API Request Helper
    async apiRequest(endpoint, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(this.token && { 'Authorization': `Bearer ${this.token}` })
            },
            ...options
        };

        try {
            const response = await fetch(`${API_BASE}${endpoint}`, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // Event Listeners
    attachEventListeners() {
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleLogin();
        });

        document.getElementById('signupForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleSignup();
        });

        document.getElementById('addContactForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleAddContact();
        });

        document.getElementById('reportSpamForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleReportSpam();
        });

        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });
    },

    // Handle Login
    async handleLogin() {
        const phone = document.getElementById('loginPhone').value;
        const password = document.getElementById('loginPassword').value;
        const errorDiv = document.getElementById('loginError');

        this.showLoading();

        try {
            const data = await this.apiRequest('/user/login', {
                method: 'POST',
                body: JSON.stringify({ phone_number: phone, password })
            });

            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            localStorage.setItem('user', JSON.stringify(data.user));

            this.token = data.access_token;
            this.user = data.user;

            this.showApp();
            this.updateUserInfo();
            this.loadDashboard();
        } catch (error) {
            errorDiv.textContent = error.message;
            errorDiv.classList.add('show');
        } finally {
            this.hideLoading();
        }
    },

    // Handle Signup
    async handleSignup() {
        const firstName = document.getElementById('signupFirstName').value;
        const lastName = document.getElementById('signupLastName').value;
        const phone = document.getElementById('signupPhone').value;
        const email = document.getElementById('signupEmail').value;
        const password = document.getElementById('signupPassword').value;
        const errorDiv = document.getElementById('signupError');

        this.showLoading();

        try {
            const data = await this.apiRequest('/user/signup', {
                method: 'POST',
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    phone_number: phone,
                    email: email || undefined,
                    password
                })
            });

            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            localStorage.setItem('user', JSON.stringify(data.user));

            this.token = data.access_token;
            this.user = data.user;

            this.showApp();
            this.updateUserInfo();
            this.loadDashboard();
        } catch (error) {
            errorDiv.textContent = error.message;
            errorDiv.classList.add('show');
        } finally {
            this.hideLoading();
        }
    },

    // Load Dashboard
    async loadDashboard() {
        try {
            const data = await this.apiRequest('/dashboard');

            const statsHTML = `
                <div class="card stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-number">${data.total_interactions}</div>
                    <div class="stat-label">Total Interactions</div>
                </div>
                <div class="card stat-card">
                    <div class="stat-icon">📞</div>
                    <div class="stat-number">${data.interaction_stats.calls}</div>
                    <div class="stat-label">Calls Made</div>
                </div>
                <div class="card stat-card">
                    <div class="stat-icon">💬</div>
                    <div class="stat-number">${data.interaction_stats.messages}</div>
                    <div class="stat-label">Messages Sent</div>
                </div>
                <div class="card stat-card">
                    <div class="stat-icon">🚫</div>
                    <div class="stat-number">${data.interaction_stats.spam_reports}</div>
                    <div class="stat-label">Spam Reports</div>
                </div>
                <div class="card stat-card">
                    <div class="stat-icon">⚠️</div>
                    <div class="stat-number">${data.spam_stats.received}</div>
                    <div class="stat-label">Times Reported</div>
                </div>
                <div class="card stat-card">
                    <div class="stat-icon">✅</div>
                    <div class="stat-number">${data.spam_stats.reported}</div>
                    <div class="stat-label">Reports Made</div>
                </div>
            `;
            document.getElementById('dashboardStats').innerHTML = statsHTML;

            const interactionsHTML = data.recent_interactions.length > 0
                ? `<ul class="interaction-list">
                    ${data.recent_interactions.map(i => `
                        <li class="interaction-item">
                            <div class="interaction-info">
                                <div class="interaction-type">
                                    ${this.getInteractionIcon(i.type)} ${this.formatInteractionType(i.type)}
                                </div>
                                <div class="interaction-details">
                                    ${i.direction === 'outgoing' ? '📤 To' : '📥 From'}: <strong>${i.with}</strong>
                                </div>
                            </div>
                            <div class="interaction-time">🕒 ${i.date}</div>
                        </li>
                    `).join('')}
                </ul>`
                : '<div class="empty-state"><div class="empty-state-icon">📭</div><h3>No interactions yet</h3><p>Start by adding contacts or reporting spam!</p></div>';

            document.getElementById('recentInteractions').innerHTML = interactionsHTML;
        } catch (error) {
            console.error('Failed to load dashboard:', error);
        }
    },

    // Search
    async performSearch() {
        const query = document.getElementById('searchInput').value.trim();
        if (!query) {
            alert('Please enter a name or phone number to search');
            return;
        }

        const resultsDiv = document.getElementById('searchResults');
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Searching...</p></div>';

        try {
            const data = await this.apiRequest(`/search?q=${encodeURIComponent(query)}`);

            if (data.results && data.results.length > 0) {
                resultsDiv.innerHTML = `
                    <div class="results-header">
                        <h3>🎯 Search Results</h3>
                        <div class="results-count">Found ${data.count} result(s) for "${query}"</div>
                    </div>
                    ${data.results.map((result, index) => `
                        <div class="result-item">
                            <div class="result-number">${index + 1}</div>
                            <div class="result-info">
                                <h4>${result.name}</h4>
                                <div class="result-phone">📱 ${result.phone_number}</div>
                                <div class="result-meta">
                                    <span class="badge ${result.is_registered ? 'badge-registered' : 'badge-contact'}">
                                        ${result.is_registered ? '✓ Registered User' : '📞 Contact'}
                                    </span>
                                    ${result.spam_likelihood > 0 ? `
                                        <span class="badge badge-spam">
                                            🚫 ${result.spam_likelihood} spam report(s)
                                        </span>
                                    ` : `
                                        <span class="badge badge-safe">✅ No spam reports</span>
                                    `}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                `;
            } else {
                resultsDiv.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">🔍</div>
                        <h3>No results found for "${query}"</h3>
                        <p>Try searching with:</p>
                        <ul>
                            <li>Different name spelling</li>
                            <li>Full phone number with country code</li>
                            <li>Partial name (e.g., "Jon" instead of "Jonathan")</li>
                        </ul>
                    </div>
                `;
            }
        } catch (error) {
            resultsDiv.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">❌</div>
                    <h3>Search failed</h3>
                    <p>${error.message}</p>
                </div>
            `;
        }
    },

    // Add Contact
    async handleAddContact() {
        const firstName = document.getElementById('contactFirstName').value;
        const lastName = document.getElementById('contactLastName').value;
        const phone = document.getElementById('contactPhone').value;
        const messageDiv = document.getElementById('contactMessage');

        this.showLoading();

        try {
            await this.apiRequest('/contact', {
                method: 'POST',
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    phone_number: phone
                })
            });

            messageDiv.textContent = '✓ Contact added successfully!';
            messageDiv.className = 'message success';
            document.getElementById('addContactForm').reset();
            
            setTimeout(() => {
                messageDiv.className = 'message';
            }, 3000);

            this.loadTopContacts();
        } catch (error) {
            messageDiv.textContent = `✗ ${error.message}`;
            messageDiv.className = 'message error';
        } finally {
            this.hideLoading();
        }
    },

    // Load Top Contacts
    async loadTopContacts() {
        const container = document.getElementById('topContactsList');
        if (!container) return;
        
        container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

        try {
            const data = await this.apiRequest('/interactions/top?limit=10');

            if (data && data.length > 0) {
                container.innerHTML = `
                    <ul class="interaction-list">
                        ${data.map((contact, index) => `
                            <li class="interaction-item">
                                <div class="rank-badge">#${index + 1}</div>
                                <div class="interaction-info">
                                    <div class="interaction-type">
                                        ${contact.contact_name}
                                    </div>
                                    <div class="interaction-details">📱 ${contact.contact_phone}</div>
                                </div>
                                <div>
                                    <span class="badge badge-info">💬 ${contact.interaction_count} interactions</span>
                                    ${contact.is_registered ? '<span class="badge badge-registered">✓ User</span>' : ''}
                                </div>
                            </li>
                        `).join('')}
                    </ul>
                `;
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">👥</div>
                        <h3>No interactions yet</h3>
                        <p>Add contacts and start interacting to see your top contacts here</p>
                    </div>
                `;
            }
        } catch (error) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">❌</div>
                    <p>Failed to load: ${error.message}</p>
                </div>
            `;
        }
    },

    // Report Spam
    async handleReportSpam() {
        const phone = document.getElementById('spamPhone').value;
        const description = document.getElementById('spamDescription').value;
        const messageDiv = document.getElementById('spamMessage');

        this.showLoading();

        try {
            await this.apiRequest('/spam', {
                method: 'POST',
                body: JSON.stringify({
                    phone_number: phone,
                    description: description || undefined
                })
            });

            messageDiv.textContent = '✓ Spam report submitted! Thank you for protecting the community.';
            messageDiv.className = 'message success';
            document.getElementById('reportSpamForm').reset();
            
            setTimeout(() => {
                messageDiv.className = 'message';
            }, 3000);

            this.loadSpamStats();
        } catch (error) {
            messageDiv.textContent = `✗ ${error.message}`;
            messageDiv.className = 'message error';
        } finally {
            this.hideLoading();
        }
    },

    // Load Spam Statistics with Filters
    async loadSpamStats() {
        const container = document.getElementById('spamStats');
        if (!container) return;
        
        container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

        try {
            // Build query with filters
            let query = '/interactions/spam-stats';
            const params = [];
            
            const minReports = document.getElementById('spamMinReports')?.value;
            const dateRange = document.getElementById('spamDateRange')?.value;
            
            if (minReports) params.push(`min_reports=${minReports}`);
            
            if (dateRange) {
                const today = new Date();
                const startDate = new Date(today);
                startDate.setDate(today.getDate() - parseInt(dateRange));
                params.push(`start_date=${startDate.toISOString().split('T')[0]}`);
            }
            
            if (params.length > 0) query += '?' + params.join('&');

            const data = await this.apiRequest(query);

            if (data && data.length > 0) {
                const topSpam = data.slice(0, 15);
                
                container.innerHTML = `
                    <div class="spam-summary">
                        <p><strong>${data.length}</strong> spam number(s) found with current filters</p>
                    </div>
                    <ul class="interaction-list">
                        ${topSpam.map((spam, index) => `
                            <li class="interaction-item spam-item">
                                <div class="rank-badge danger">#${index + 1}</div>
                                <div class="interaction-info">
                                    <div class="interaction-type">
                                        📱 ${spam.phone_number}
                                    </div>
                                    <div class="interaction-details">
                                        👥 Reported by ${spam.unique_reporters} user(s)
                                        ${spam.latest_description ? `<br>💬 "${spam.latest_description}"` : ''}
                                    </div>
                                </div>
                                <span class="badge badge-spam">🚫 ${spam.spam_count} reports</span>
                            </li>
                        `).join('')}
                    </ul>
                    ${data.length > 15 ? `<p class="showing-text">Showing top 15 of ${data.length} results</p>` : ''}
                `;
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📊</div>
                        <h3>No spam reports found</h3>
                        <p>Try adjusting the filters or be the first to report a spam number!</p>
                    </div>
                `;
            }
        } catch (error) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">❌</div>
                    <p>Failed to load: ${error.message}</p>
                </div>
            `;
        }
    },

    // Helper Functions
    getInteractionIcon(type) {
        const icons = {
            'call': '📞',
            'message': '💬',
            'spam_report': '🚫'
        };
        return icons[type] || '📱';
    },

    formatInteractionType(type) {
        const types = {
            'call': 'Call',
            'message': 'Message',
            'spam_report': 'Spam Report'
        };
        return types[type] || type;
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});