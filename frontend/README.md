# PlacementPrep AI - Enterprise Frontend Architecture

Welcome to the production-ready frontend repository for **PlacementPrep AI**, an AI-powered Placement Preparation Platform.

## 🚀 Overview

This architecture is built strictly using **HTML5, CSS3, and Vanilla JS (ES6+)** with **Bootstrap 5**, following enterprise SaaS patterns. It achieves high modularity and reusability without relying on heavy frameworks like React or Angular.

## 📁 Folder Structure

```text
frontend/
├── assets/                  # Global static assets
│   ├── css/                 # Modular CSS Design System (variables, components, etc.)
│   ├── js/                  # Core JS logic (navigation, themes, loader, validation)
│   ├── images/              # Static images and placeholders
│   └── icons/               # Custom SVG icons
├── components/              # Reusable HTML snippets loaded via JS
│   ├── sidebar.html
│   ├── navbar.html
│   ├── loader.html
│   └── toast.html
├── layouts/                 # Base layout templates
│   └── master-layout.html   # Reference for creating new pages
├── pages/                   # Application Views (Dashboard, DSA, Mock Tests, etc.)
│   ├── 404.html
│   ├── 500.html
│   └── empty-states.html
├── README.md                # Project documentation
└── DEVELOPER_NOTES.md       # Migration and integration strategy
```

## 🎨 Design System

The platform utilizes a **Glassmorphism** and **Clean SaaS** theme (White + Blue `#2563EB`).
- **Typography**: Poppins (Google Fonts)
- **CSS Architecture**: Variables, Components, Utilities, Animations, Theme (Dark Mode), and Responsive queries are split into specific files to avoid monolithic stylesheets.

## ⚙️ Core Features

1. **Client-Side Component Loading**: `navigation.js` dynamically fetches and injects `sidebar.html` and `navbar.html` into any page that contains `<div id="sidebar-container"></div>`.
2. **Global Loading Experience**: Animated skeleton loaders and a full-page transition loader.
3. **Toast Notifications**: Accessible via `window.showToast(type, message)` globally.
4. **Theme Management**: Persisted Dark/Light mode using `theme.js` and local storage.

## 🛠️ Development Setup

Since the frontend uses JavaScript `fetch()` API to load HTML components (Sidebar, Navbar), **you cannot open the files directly via `file://` protocol** due to CORS restrictions.

You must run a local web server:
```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx serve
```
Then navigate to `http://localhost:8000/pages/dashboard.html`
