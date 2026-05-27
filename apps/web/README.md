# AirWatch web

React 19 + TypeScript + Vite frontend. See [the root README](../../README.md)
for the overall project.

## Local dev

```bash
npm install
VITE_API_URL=http://localhost:8000 npm run dev
# → http://localhost:5173
```

By default the API URL comes from `VITE_API_URL`. Set it in `.env.local`
for local dev or in your hosting provider for prod.

## Build

```bash
npm run typecheck     # tsc -b
npm run build         # tsc -b && vite build → dist/
npm run preview       # serve dist/ locally
```

## Pages

| Route             | What it shows                                                                |
| ----------------- | ---------------------------------------------------------------------------- |
| `/`               | Status pills + location table + admin "trigger ingest" button                |
| `/location/:id`   | PM2.5 + weather time series, KPI tiles, scatter plots for weather correlation |
| `/summary`        | Bad-air days leaderboard with bar chart and a 90-day trend line              |
| `/alerts`         | Email subscription form + list                                               |

## Stack

- **React 19** with `@tanstack/react-query` for server state
- **Recharts** for time series, bar, and scatter visualizations
- **CSS variables** (in `src/index.css`) with automatic `prefers-color-scheme`
  dark mode — no Tailwind, no CSS-in-JS runtime

## Project layout

```
src/
├── components/   # KPI, PM25Chart, WeatherChart, ScatterPlot
├── lib/api.ts    # Typed REST client (all fetch calls live here)
├── pages/        # Route-level components
├── types/        # Shared TypeScript types
├── App.tsx       # Shell + routes
└── main.tsx      # Vite entry, QueryClient + BrowserRouter
```
