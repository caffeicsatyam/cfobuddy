# CFO Buddy — Frontend

A premium, ChatGPT-inspired interface for the CFO Buddy financial assistant. Built with Next.js 15+, React, and CSS Modules.

## Features

- **ChatGPT UI** — Warm dark theme, collapsible sidebar, and centered chat layout.
- **Suggestion Chips** — Quick access to common financial analysis prompts.
- **Interactive Charts** — Seamless rendering of generated Plotly charts.
- **Responsive Design** — Optimized for both desktop and mobile views.
- **Smooth UX** — Thread-based conversation management and typing indicators.

## Setup & Development

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000).

## Architecture

- `/src/app` — Page routes (Landing and Dashboard).
- `/src/components` — Reusable UI components (Sidebar, ChatArea, etc.).
- `/src/lib` — API clients, types, and utility functions.
- `/public` — Static assets and icons.

## Design System

CFO Buddy uses a custom CSS-variable based design system defined in `src/app/globals.css`. 
- **Colors**: Deep charcoal (#212121) and Emerald green (#10a37f).
- **Fonts**: Inter and Manrope for a modern, professional look.

---

MIT © [caffeicsatyam](https://github.com/caffeicsatyam)
