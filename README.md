# Smart Plate DZ — React rebuild

A React + Vite + Tailwind rebuild of the Smart Plate DZ website (Algerian smart license plates platform).

## Features

- React 18 + Vite (fast HMR dev server)
- Tailwind CSS for styling
- React Router for multi-page navigation
- Built-in i18n with three languages: French (default), Arabic (RTL), English
- Responsive layout (mobile, tablet, desktop)
- Pages mirroring the live site:
  - `/` Accueil (home)
  - `/produits` and `/accueil` Produits
  - `/services`
  - `/smartsticks`
  - `/securite`
  - `/a-propos`
  - `/bienvenue` (and `/dashboard`)
  - `/se-connecter`

## Requirements

- Node.js 18+ (download from https://nodejs.org)
- npm (comes with Node)

## Run locally

Open a terminal in this folder, then:

```bash
npm install
npm run dev
```

Vite will print a URL like `http://localhost:5173` — open it in your browser.

## Build for production

```bash
npm run build
```

Compiled static files end up in `dist/`. You can drop that folder into Hostinger File Manager (replace your existing `public_html`) to deploy.

## Switching languages

Use the `AR / EN / FR` switcher in the top-right of the navbar. The selection is saved to `localStorage`. Arabic switches the entire layout to RTL.

## Editing content

All translatable text lives in `src/locales/{fr,en,ar}.js`. Edit those files to change copy without touching components.

## Project structure

```
src/
  components/      shared UI (Navbar, Footer, TopBanner, Logo, LanguageSwitcher, Layout)
  pages/           one file per page
  locales/         fr.js / en.js / ar.js translations
  i18n.jsx         language context + provider
  App.jsx          routes
  main.jsx         entry
  index.css        Tailwind + global styles
```
