# CFOBuddy — Next.js Frontend Implementation

Build a full Next.js frontend for CFOBuddy that matches the Stitch "Algorithmic Architect" design system: deep navy surfaces (`#0b1326`), teal (`#6bd8cb`) + purple (`#d0bcff`) accents, Manrope/Inter fonts, glassmorphism, no hard borders (tonal layering only).

## Proposed Changes

### Frontend Scaffold

#### [NEW] [frontend/](file:///c:/Users/MSI/Desktop/cfobuddy/frontend/)

Initialize with `npx -y create-next-app@latest ./` (TypeScript, App Router, vanilla CSS).

---

### Design System

#### [NEW] [globals.css](file:///c:/Users/MSI/Desktop/cfobuddy/frontend/src/app/globals.css)

Full CSS design system with:
- CSS custom properties for all Stitch color tokens (surface hierarchy, primary/secondary/tertiary)
- Typography scale using Google Fonts (Manrope for headlines, Inter for body)
- Tonal layering system (no 1px borders — depth via background color shifts)
- Glassmorphism utility classes (`backdrop-filter: blur(20px)`)
- Signature gradients (primary → secondary for AI elements)
- Spacing scale, border-radius tokens
- Smooth micro-animations and transitions

---

### Pages

#### [NEW] [page.tsx](file:///c:/Users/MSI/Desktop/cfobuddy/frontend/src/app/page.tsx) — Landing Page

Matching the Stitch "Landing Page" screen:
- **Navbar**: CFOBuddy logo, nav links (Dashboard, Analytics, Strategy, Reports), CTA button
- **Hero Section**: Headline "CFOBuddy: Your Precision AI Financial Analyst", sub-copy, 3 stat cards (Net Liquidity, AI Forecast Accuracy, Risk Index)
- **Features Grid**: 4 feature cards (AI-driven analysis, Automated charts, Multi-file support, Real-time insights) with icon + description
- **Pricing Section**: 3 tiers (Professional, Enterprise AI highlighted, Custom)
- **CTA Section**: Final call-to-action
- **Footer**: Copyright, links

#### [NEW] [dashboard/page.tsx](file:///c:/Users/MSI/Desktop/cfobuddy/frontend/src/app/dashboard/page.tsx) — Dashboard + AI Chat

Matching the Stitch "Dashboard & AI Chatbot" screen:
- **Sidebar** (`surface-container-low`): Logo, nav items (Overview, AI Advisor, Cash Flow, Investments), chat history list with thread names, user profile at bottom
- **Main Area**: Greeting header, chat interface
- **Chat Interface**: Message bubbles (user in `surface-container-high`, AI in `tertiary-container`), typing indicator, input field with `surface-container-lowest` background and teal glow on focus
- **File upload**: Drag-and-drop area + file list display

---

### Components

#### [NEW] [components/Sidebar.tsx](file:///c:/Users/MSI/Desktop/cfobuddy/frontend/src/components/Sidebar.tsx)
Sidebar navigation with chat history, nav items, and user profile area.

#### [NEW] [components/ChatArea.tsx](file:///c:/Users/MSI/Desktop/cfobuddy/frontend/src/components/ChatArea.tsx)
Main chat interface: message list, AI response rendering (with markdown support), loading states.

#### [NEW] [components/ChatInput.tsx](file:///c:/Users/MSI/Desktop/cfobuddy/frontend/src/components/ChatInput.tsx)
Auto-resizing textarea with teal glow focus state, send button.

#### [NEW] [components/FileUpload.tsx](file:///c:/Users/MSI/Desktop/cfobuddy/frontend/src/components/FileUpload.tsx)
Drag-and-drop file upload with supported format indicators and file list.

#### [NEW] [components/Navbar.tsx](file:///c:/Users/MSI/Desktop/cfobuddy/frontend/src/components/Navbar.tsx)
Landing page top navigation bar.

---

### API Layer

#### [NEW] [lib/api.ts](file:///c:/Users/MSI/Desktop/cfobuddy/frontend/src/lib/api.ts)

Fetch wrapper connecting to FastAPI backend at `http://localhost:8000`:
- `sendMessage(message, threadId)` → POST `/chat`
- `getThreads()` → GET `/threads`
- `getFiles()` → GET `/files`
- `uploadFile(file)` → POST `/upload`

---

### Backend CORS Update

#### [MODIFY] [main.py](file:///c:/Users/MSI/Desktop/cfobuddy/api/main.py)

Add `http://localhost:3000` to CORS origins (already present, just verify).

---

## Verification Plan

### Browser Verification
1. Run `npm run dev` in `frontend/` — verify the dev server starts on `http://localhost:3000`
2. Open Landing Page in browser — verify hero, features, pricing sections render with the correct dark navy theme
3. Navigate to `/dashboard` — verify sidebar, chat interface render correctly
4. Type a message in the chat input — verify the UI updates (actual backend connectivity is optional since the backend requires API keys)

### Manual Verification
- Visually compare the running frontend against the Stitch design screenshots to confirm color palette, typography, and layout fidelity
