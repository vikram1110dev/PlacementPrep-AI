# Developer Notes & Migration Strategy

## Component Integration Strategy

To maintain a DRY (Don't Repeat Yourself) codebase in a vanilla HTML environment, we use a Javascript-based component injector.

### How to create a new page:
1. Copy `layouts/master-layout.html` to `pages/new-page.html`.
2. Ensure the following placeholder IDs exist:
   - `<div id="loader-container"></div>`
   - `<div id="sidebar-container"></div>`
   - `<div id="navbar-container"></div>`
   - `<div id="toast-container"></div>`
3. Include the global CSS and JS files in the `<head>` and `<body>` respectively.
4. `navigation.js` will automatically fetch the HTML snippets from `../components/` and inject them.

### How to Migrate Existing Legacy Pages
If you are moving a legacy flat HTML file (e.g., `admin-users.html`) to the new `pages/` directory:
1. Move the file to `pages/`.
2. Replace the hardcoded `<aside class="sidebar">` block with `<div id="sidebar-container"></div>`.
3. Replace the hardcoded `<header class="top-navbar">` block with `<div id="navbar-container"></div>`.
4. Update CSS paths from `href="css/..."` to `href="../assets/css/..."`.
5. Add the core JS files to the bottom of the body:
```html
<script src="../assets/js/helpers.js"></script>
<script src="../assets/js/theme.js"></script>
<script src="../assets/js/loader.js"></script>
<script src="../assets/js/notifications.js"></script>
<script src="../assets/js/navigation.js"></script>
```

## CSS Naming Conventions
- Use standard Bootstrap 5 classes wherever possible (`d-flex`, `mt-3`, `text-muted`).
- For custom elements, use BEM-like or utility classes defined in our design system (`.card-glass`, `.stat-card-modern`, `.text-truncate-2`).
- Never hardcode colors in HTML style tags. Always use CSS variables `var(--primary-color)`.

## Handling "Empty States"
Whenever dynamic data is missing (e.g., no search results, no projects added), render one of the empty states found in `pages/empty-states.html` rather than a blank table or generic text.

## API Integration Mockups
Currently, features like `saveProfileBtn` or `deleteAccountBtn` are mocked using `setTimeout` to simulate latency and then trigger `window.showToast()`. When connecting to FastAPI, replace the `setTimeout` blocks with `fetch()` calls to the backend endpoints.
