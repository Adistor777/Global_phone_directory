# 🔍 Spam Detection & Contact Management System

A Truecaller-like spam detection and contact management system built with Django REST Framework and vanilla JavaScript. This application provides community-driven spam protection, global directory search, and comprehensive interaction analytics.

![Django](https://img.shields.io/badge/Django-5.0.6-green)
![DRF](https://img.shields.io/badge/DRF-3.15.1-red)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Performance](#-performance)
- [Security](#-security)
- [Deployment](#-deployment)

---

## ✨ Features

### Part 1: Core API Features

#### 🔐 Authentication & User Management
- JWT-based authentication with access & refresh tokens
- User registration with phone number validation
- **Auto-registration**: Login automatically creates new accounts for unknown numbers
- Phone number normalization (supports +91, 91, or plain format)
- Secure password hashing with PBKDF2

#### 📇 Contact Management
- Create and manage personal contacts
- Phone number normalization and validation
- Duplicate prevention (one contact per phone per user)
- Automatic interaction tracking

#### 🚫 Spam Reporting
- Report any phone number as spam (registered or unregistered)
- Community-driven spam database
- One report per user per number
- Optional spam descriptions
- View spam likelihood for any number

#### 🔍 Advanced Search
- **Fuzzy name search** using Levenshtein distance algorithm
- **Exact phone search** with format normalization
- Results ranked by match score (0-100)
- Deduplication (users prioritized over contacts)
- Pagination (10 results per page)
- Shows spam likelihood for each result

### Part 2: Interaction Dashboard

#### 📊 Interaction Tracking
- Automatic tracking of all user activities
- Three interaction types: calls, messages, spam reports
- Complete audit trail with timestamps
- Flexible metadata storage (JSON field)

#### 📈 Analytics & Insights
- **Total Interactions**: Aggregate count across all types
- **Breakdown by Type**: Calls, messages, spam reports
- **Recent Activity**: Last 10 interactions with filtering
- **Top Contacts**: Most frequently contacted people (ranked)
- **Spam Statistics**: Most reported numbers with counts
- **7-Day Activity Trend**: Visual timeline of activity

#### 🎯 Advanced Filtering
- Filter interactions by type (call/message/spam_report)
- Date range filtering for spam reports
- Minimum report count filtering
- Phone-specific spam queries
- Pagination on all list endpoints

#### 🎨 Dashboard UI
- Beautiful single-page application
- Real-time statistics and updates
- Responsive design (mobile-friendly)
- Interactive charts and visualizations
- Professional purple gradient theme

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.0.6
- **API**: Django REST Framework 3.15.1
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Phone Validation**: phonenumbers
- **Fuzzy Search**: fuzzywuzzy + python-Levenshtein
- **Database**: SQLite (dev) / PostgreSQL (production-ready)

### Frontend
- **Pure JavaScript** (Vanilla JS - no frameworks)
- **CSS3** with animations and transitions
- **HTML5** with semantic markup
- **LocalStorage** for token persistence

### Development Tools
- **Environment**: python-dotenv
- **Package Manager**: pip
- **Version Control**: Git

---

## 💻 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- Git

### Step 1: Clone Repository
```bash
git clone <your-repository-url>
cd hiring-challenge/app
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration (Optional)

Create `.env` file in the `app/` directory:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite by default)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# JWT Configuration
JWT_ACCESS_TOKEN_HOURS=1
JWT_REFRESH_TOKEN_DAYS=7

# Phone Number Settings
PHONENUMBER_DEFAULT_REGION=IN

# API Settings
PAGE_SIZE=10
```

### Step 5: Run Migrations
```bash
python manage.py migrate
```

### Step 6: Create Superuser (Optional)
```bash
python manage.py createsuperuser
# Follow prompts:
# Phone: +919999999999
# First name: Admin
# Password: admin123
```

### Step 7: Populate Sample Data (Recommended)
```bash
python manage.py populate --users 30
```

This creates:
- 30 users with realistic names
- Random contacts for each user
- Sample spam reports
- Interaction history
- Default password: `mytest123`

---

## 🚀 Quick Start

### Start Backend Server
```bash
# From app/ directory
python manage.py runserver
```

Server runs at: `http://127.0.0.1:8000/`

### Start Frontend Server

**Option 1: Python HTTP Server**
```bash
cd frontend
python -m http.server 8080
```

**Option 2: Direct File Open**
```bash
# Simply open frontend/index.html in your browser
```

Frontend runs at: `http://localhost:8080/`

### Login with Demo Account

**Default credentials after populate:**
- Phone: `+917220875841`
- Password: `mytest123`

**Or create your own account using the signup form!**

---

## 📚 API Documentation

### Base URL
```
http://127.0.0.1:8000/api
```

### Authentication

All endpoints except `/user/signup` and `/user/login` require JWT authentication.

**Include token in headers:**
```
Authorization: Bearer <access_token>
```

---

### Endpoints

#### 1. User Authentication

**POST /api/user/signup**
```json
Request:
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+919876543210",
  "email": "john@example.com",
  "password": "secure123"
}

Response (201):
{
  "user": {
    "id": "uuid",
    "full_name": "John Doe",
    "phone_number": "+919876543210"
  },
  "access_token": "eyJ0eXAi...",
  "refresh_token": "eyJ0eXAi..."
}
```

**POST /api/user/login**
```json
Request:
{
  "phone_number": "+919876543210",
  "password": "secure123"
}

Response (200 - Existing User | 201 - New User):
{
  "user": {...},
  "access_token": "...",
  "refresh_token": "..."
}
```

---

#### 2. Contact Management

**POST /api/contact**
```json
Request:
{
  "first_name": "Alice",
  "last_name": "Smith",
  "phone_number": "9123456789"
}

Response (201):
{
  "id": "uuid",
  "first_name": "Alice",
  "last_name": "Smith",
  "phone_number": "+919123456789",
  "created_at": "2025-10-23T10:30:00Z"
}
```

---

#### 3. Spam Reporting

**POST /api/spam**
```json
Request:
{
  "phone_number": "9999999999",
  "description": "Telemarketing spam call"
}

Response (201):
{
  "id": "uuid",
  "phone_number": "+919999999999",
  "description": "Telemarketing spam call",
  "created_at": "2025-10-23T10:30:00Z"
}
```

---

#### 4. Search

**GET /api/search?q={query}**
```json
// Search by name
GET /api/search?q=John

// Search by phone
GET /api/search?q=9876543210

Response:
{
  "count": 5,
  "next": "http://.../api/search?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "name": "John Doe",
      "phone_number": "+919876543210",
      "is_registered": true,
      "spam_likelihood": 3,
      "match_score": 100
    }
  ]
}
```

**GET /api/search/detail/{id}**
```json
Response:
{
  "id": "uuid",
  "name": "John Doe",
  "phone_number": "+919876543210",
  "email": "john@example.com",  // Only if in contacts
  "is_registered": true,
  "spam_likelihood": 3
}
```

---

#### 5. Interactions

**POST /api/interaction**
```json
Request:
{
  "receiver_phone": "+919876543210",
  "interaction_type": "call",
  "metadata": {
    "duration": 120,
    "notes": "Follow-up call"
  }
}

Response (201):
{
  "id": "uuid",
  "initiator": {...},
  "receiver_phone": "+919876543210",
  "interaction_type": "call",
  "metadata": {...},
  "created_at": "2025-10-23T10:30:00Z"
}
```

**GET /api/interactions/recent**
```
// All interactions
GET /api/interactions/recent

// Filter by type
GET /api/interactions/recent?type=call
GET /api/interactions/recent?type=message
GET /api/interactions/recent?type=spam_report

// Pagination
GET /api/interactions/recent?page=2
```

**GET /api/interactions/top?limit={n}**
```json
// Top 5 contacts (default)
GET /api/interactions/top

// Top 10 contacts
GET /api/interactions/top?limit=10

Response:
[
  {
    "contact_name": "Alice Smith",
    "contact_phone": "+919123456789",
    "interaction_count": 25,
    "is_registered": true
  }
]
```

**GET /api/interactions/spam-stats**
```
// All spam reports
GET /api/interactions/spam-stats

// Last 7 days
GET /api/interactions/spam-stats?start_date=2025-10-16

// Date range
GET /api/interactions/spam-stats?start_date=2025-10-01&end_date=2025-10-31

// Minimum 5 reports
GET /api/interactions/spam-stats?min_reports=5

// Combined filters
GET /api/interactions/spam-stats?start_date=2025-10-01&min_reports=5

// Specific number
GET /api/interactions/spam-stats?phone_number=9999999999
```

---

#### 6. Dashboard

**GET /api/dashboard**
```json
Response:
{
  "user": {...},
  "total_interactions": 24,
  "interaction_stats": {
    "calls": 8,
    "messages": 5,
    "spam_reports": 11
  },
  "recent_interactions": [...],
  "top_contacts": [...],
  "spam_stats": {...},
  "activity_trend": [
    {"date": "2025-10-17", "day": "Thu", "count": 0},
    {"date": "2025-10-23", "day": "Wed", "count": 24}
  ]
}
```

---

## 🗄️ Database Schema

### User Model
```python
- id (UUID, primary key)
- phone_number (String, unique, indexed)
- first_name (String)
- last_name (String, optional)
- email (Email, unique, optional)
- password (Hashed)
- is_active (Boolean)
- is_staff (Boolean)
- is_superuser (Boolean)
- created_at, updated_at (Timestamps)
```

### Contact Model
```python
- id (UUID, primary key)
- phone_number (String, indexed)
- first_name (String)
- last_name (String, optional)
- created_by (FK to User)
- created_at, updated_at (Timestamps)
- Unique: (phone_number, created_by)
```

### ScamRecord Model
```python
- id (UUID, primary key)
- phone_number (String, indexed)
- description (Text, optional)
- reported_by (FK to User)
- created_at, updated_at (Timestamps)
- Unique: (phone_number, reported_by)
```

### Interaction Model
```python
- id (UUID, primary key)
- initiator (FK to User)
- receiver (FK to User, optional)
- receiver_phone (String)
- interaction_type (Choice: call/message/spam_report)
- metadata (JSON)
- created_at, updated_at (Timestamps)
- Indexes: initiator, receiver, type, created_at
```

---

## 📁 Project Structure
```
hiring-challenge/app/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3
├── app/
│   ├── settings.py              # Django configuration
│   ├── urls.py                  # Main URL routing
│   ├── utils.py                 # Phone normalization
│   ├── mixins.py                # Reusable model mixins
│   ├── admin.py                 # Admin panel config
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # Custom User model
│   │   ├── contact.py           # Contact model
│   │   ├── scam.py              # Spam record model
│   │   └── interaction.py       # Interaction tracking
│   ├── serializers/             # DRF serializers
│   │   ├── input/               # Request validation
│   │   │   ├── user.py
│   │   │   ├── contact.py
│   │   │   ├── scam.py
│   │   │   └── interaction.py
│   │   └── output/              # Response formatting
│   │       ├── user.py
│   │       ├── contact.py
│   │       ├── scam.py
│   │       └── interaction.py
│   ├── api/
│   │   ├── viewsets/            # API business logic
│   │   │   ├── user.py
│   │   │   ├── contact.py
│   │   │   ├── scam.py
│   │   │   ├── search.py
│   │   │   ├── interaction.py
│   │   │   └── dashboard.py
│   │   └── router/              # URL routing
│   │       ├── urls.py
│   │       ├── user.py
│   │       ├── contact.py
│   │       ├── scam.py
│   │       ├── search.py
│   │       ├── interaction.py
│   │       └── dashboard.py
│   ├── management/
│   │   └── commands/
│   │       └── populate.py      # Sample data generator
│   └── templates/
│       └── dashboard.html       # Dashboard template
└── frontend/                     # Frontend SPA
    ├── index.html               # Main HTML
    ├── styles.css               # Styling
    └── app.js                   # JavaScript logic
```

---

## 🧪 Testing

### Manual Testing with Frontend

1. **Start both servers** (backend + frontend)
2. **Open browser** to `http://localhost:8080`
3. **Login** with demo credentials
4. **Test each feature**:
   - ✅ Dashboard loads with stats
   - ✅ Search by name and phone
   - ✅ Add a new contact
   - ✅ Report spam number
   - ✅ View top contacts
   - ✅ Apply spam filters

### API Testing with Postman

Import the Postman collection (if available) or test endpoints manually:
```bash
# Login
curl -X POST http://127.0.0.1:8000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+919876543210","password":"test123"}'

# Search (replace TOKEN)
curl -X GET "http://127.0.0.1:8000/api/search?q=John" \
  -H "Authorization: Bearer TOKEN"
```

### Django Admin Panel

Access at: `http://127.0.0.1:8000/admin`

- View all users, contacts, spam reports
- Manually create/edit records
- Monitor system activity

---

## ⚡ Performance

### Optimization Techniques

1. **Database Indexes**
   - Phone numbers (frequent lookups)
   - Foreign keys (join optimization)
   - Created timestamps (sorting)
   - Interaction types (filtering)

2. **Query Optimization**
   - `select_related()` for foreign keys
   - `prefetch_related()` for reverse relations
   - `values()` and `annotate()` for aggregations
   - Early query termination

3. **Pagination**
   - Default 10 items per page
   - Prevents large result sets
   - Reduces memory usage

4. **Caching Ready**
   - Stateless JWT authentication
   - Can add Redis for session/query caching

### Scalability Considerations

**Current (SQLite):**
- ✅ Development ready
- ✅ Handles thousands of records
- ✅ Fast for single-user testing

**Production (PostgreSQL):**
- ✅ Millions of records
- ✅ Concurrent users
- ✅ Read replicas for search
- ✅ Connection pooling

---

## 🔒 Security

### Implemented Security Features

1. **Authentication & Authorization**
   - JWT tokens with expiration (1 hour access, 7 days refresh)
   - Stateless authentication (scalable)
   - Protected endpoints (401 for unauthorized)

2. **Password Security**
   - PBKDF2 hashing with salt
   - Never stored in plain text
   - Never logged or exposed

3. **Input Validation**
   - Phone number format validation
   - Email format validation
   - Required field checks
   - Type validation

4. **SQL Injection Prevention**
   - Django ORM (parameterized queries)
   - No raw SQL without parameterization

5. **CORS Configuration**
   - Configured for development
   - Restrict origins in production

6. **Data Integrity**
   - Unique constraints (prevent duplicates)
   - Foreign key constraints
   - Database-level validation

### Production Security Checklist

- [ ] Change `SECRET_KEY` to strong random value
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use HTTPS only
- [ ] Set secure cookie flags
- [ ] Add rate limiting
- [ ] Configure CORS properly
- [ ] Set up monitoring (Sentry)
- [ ] Regular security audits
- [ ] Keep dependencies updated

---

## 🚀 Deployment

### Production Setup

#### 1. Environment Variables
```env
SECRET_KEY=<strong-random-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=spam_detector_db
DB_USER=your_user
DB_PASSWORD=strong_password
DB_HOST=localhost
DB_PORT=5432
```

#### 2. PostgreSQL Setup
```bash
# Install PostgreSQL
pip install psycopg2-binary

# Update settings.py with DB credentials
```

#### 3. Static Files
```bash
python manage.py collectstatic
```

#### 4. WSGI Server (Gunicorn)
```bash
pip install gunicorn
gunicorn app.wsgi:application --bind 0.0.0.0:8000
```

#### 5. Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location / {
        root /path/to/frontend;
        try_files $uri /index.html;
    }
}
```

---

## 🎯 Key Features Explained

### Phone Number Normalization

All phone numbers are stored in E.164 format (`+919876543210`):
- Works with: `9876543210`, `+919876543210`, `919876543210`
- Uses `phonenumbers` library for validation
- Default region: India (+91)
- Consistent storage enables accurate matching

### Fuzzy Search Algorithm

Uses Levenshtein distance for name matching:
- "Jon" finds "John", "Jonathan", "Jonas"
- Calculates similarity percentage (0-100)
- Results ranked by match score
- Handles typos and variations

### Auto-Registration

Smart login behavior:
- Existing user + correct password → Login (200)
- Existing user + wrong password → Error (401)
- New phone number → Auto-create account (201)
- Seamless onboarding experience

### Interaction Tracking

Automatic audit trail:
- Contact creation → logged as interaction
- Spam report → logged as interaction
- Manual interaction creation available
- Enables comprehensive analytics

---

## 🐛 Troubleshooting

### Common Issues

**1. Port already in use**
```bash
# Change port
python manage.py runserver 8001
```

**2. Database errors**
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py populate --users 30
```

**3. JWT token expired**
- Just login again to get fresh token
- Tokens expire after 1 hour

**4. Phone number validation error**
- Ensure format: `+91XXXXXXXXXX` or `XXXXXXXXXX`
- At least 10 digits required

**5. CORS errors (if any)**
- Check `CORS_ALLOW_ALL_ORIGINS` is `True` in settings
- Verify `corsheaders` is installed

---

## 📝 Management Commands

### Populate Database
```bash
# Default: 30 users
python manage.py populate

# Custom options
python manage.py populate --users 50 --max-contacts 15 --password testpass
```

**Options:**
- `--users`: Number of users to create (default: 30)
- `--max-contacts`: Max contacts per user (default: 10)
- `--max-spam`: Max spam reports per user (default: 5)
- `--password`: Default password for all users (default: mytest123)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is part of a technical assessment for Almabase.

---

## 👤 Author

**Aditya**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- Django & Django REST Framework teams
- Anthropic's Claude for assistance
- Almabase for the opportunity
- Open source community

---

## 📞 Demo Credentials

After running `populate` command:

**Login:**
- Phone: `+917220875841`
- Password: `mytest123`

**Admin Panel:**
- Phone: `+919999999999`
- Password: `admin123`

---

## 🎓 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Phone Number Library](https://github.com/daviddrysdale/python-phonenumbers)

---

**Built with ❤️ using Django REST Framework**

*Last Updated: October 23, 2025*