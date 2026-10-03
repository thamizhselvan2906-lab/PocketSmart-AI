# PocketSmart AI 🚀
**AI-Powered Budgeting and Recommendation Platform**

PocketSmart AI is a web application designed to keep users strictly within budget when furnishing rooms, planning events, and curating jewelry ensembles. Built with **Flask**, **SQLite**, and **Google Gemini AI**, it features real-time category budget allocation, outfit photo vision analysis, dynamic recommendation cards, and live budget recalculations.

---

## ✨ Key Features

### 1. 🛋️ Home Interior Planner
- Enter total room budget and select currency ($, ₹, €, £).
- Choose room type: **Living Room**, **Bedroom**, or **Kitchen & Dining**.
- Select room items and adjust quantities with interactive counters.
- Generates tailored product recommendations (product name, category, estimated price, rationale, platform, and direct shopping links).

### 2. 🎉 Party & Event Planner
- Enter total budget and specify guest count with an interactive slider.
- Real-time **per-guest budget calculator**.
- Event types: Birthday, Wedding, Corporate Gala, Anniversary, Dinner Party.
- Automatically divides budget across **Venue**, **Catering & Drinks**, **Decoration**, and **Entertainment**.
- Curates party packages and vendors matching guest capacity and budget.

### 3. 💎 Jewelry Planner with Gemini Vision
- Specify budget, occasion, style, and preferred metal/gemstones.
- **Outfit Image Upload**: Drag-and-drop outfit photos for multimodal AI vision analysis. Gemini analyzes the neckline, color palette, and cut to recommend harmonizing jewelry.
- Recommendations stay strictly within the allocated budget.

### 4. 📊 Live Budget Dashboard & Recommendation Cards
- **Live Metrics**: Total Budget Planned, Estimated Spend, Remaining Surplus/Savings, and Recommendation counts.
- **Budget Health Bar**: Dynamic color transitions (Green: within budget, Amber: near limit, Red: over budget).
- **Interactive Checkboxes**: Uncheck or check items to recalculate total spending and remaining budget instantly in real-time.
- **Platform Badges & Direct Links**: Curated links to Amazon, IKEA, Target, Etsy, Blue Nile, Tanishq, and more.
- **SQLite Persistence**: Save generated plans, view plan history, inspect details, toggle items, and delete plans.

### 5. 🤖 Dual-Mode AI Architecture
- **Gemini Live AI**: Direct integration with Google Gemini 1.5/2.0 API using your API key.
- **Smart Demo Engine**: Out-of-the-box algorithmic fallback engine with realistic catalog data so you can test all features immediately without requiring an API key.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.13, Flask 3.0, SQLAlchemy 2.0, Werkzeug, Pillow
- **AI**: Google Generative AI (`google-generativeai` / Gemini 1.5 & 2.0 Flash)
- **Database**: SQLite (persisted locally in `pocketsmart.db`)
- **Frontend**: Responsive SPA with Tailwind CSS, Glassmorphism design system, Vanilla JavaScript, and Inter/Outfit typography

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed
- (Optional) Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

### 2. Installation
Open PowerShell or your terminal in the project directory:

```bash
# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup (Optional)
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Open `.env` and add your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=5000
```

> **Note**: If you don't provide an API key, PocketSmart AI will automatically run in **Smart Demo Engine** mode with realistic catalog products, so all features remain 100% operational! You can also enter the API key at any time using the ⚙️ button in the top navigation bar.

### 4. Run the Application
Run the root launcher:

```bash
python run.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
PocketSmart AI/
├── backend/
│   ├── app.py              # Flask server and RESTful API endpoints
│   ├── config.py           # Application configurations and paths
│   ├── database.py         # SQLAlchemy engine and session setup
│   ├── models.py           # SQLite database schema (Plans, Items, Allocations)
│   ├── gemini_service.py   # Gemini API integration and fallback engine
│   └── mock_data.py        # Realistic product catalog and search links
├── frontend/
│   ├── index.html          # Main responsive SPA layout
│   └── static/
│       ├── css/
│       │   └── style.css   # Glassmorphism, animations, badges
│       └── js/
│           ├── api.js      # REST API client & toast notifications
│           ├── app.js      # Coordinator, tabs, loading overlay, modals
│           ├── dashboard.js# Analytics KPIs, saved plans, plan details
│           └── planners.js # 3 planners logic, image upload, recalculations
├── uploads/                # Directory for user-uploaded outfit photos
├── .env.example            # Environment variables template
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation
└── run.py                  # Single-command application launcher
```

---

## 🔒 Responsible AI & Pricing Notice
PocketSmart AI provides realistic price estimations and curated search queries to authentic retailer platforms. Prices are estimated for budgeting guidance. Actual purchase prices on third-party merchant sites may vary based on seller promotions, shipping, taxes, and regional availability.
