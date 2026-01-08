# Frontend Application

This directory contains the frontend application for the timeline visualization.

## Overview

The frontend is a highly interactive visual interface for exploring historical and geographical events across multiple dimensions (time, geography, people, events).

## Key Features

- **Interactive Timeline Visualization**: Visualize events across time with zoom capabilities
- **Multi-Dimensional Navigation**: Pivot between timeline, geography, people, and events
- **Geographic Mapping**: View events on interactive maps with temporal changes
- **Responsive Design**: Works across modern browsers (Chrome, Safari, Firefox, Edge)
- **Mobile Support**: Progressive enhancement for mobile platforms in the future

## Architecture

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/          # Page-level components
│   ├── views/          # Major view components (timeline, map, etc.)
│   ├── hooks/          # Custom React hooks
│   ├── services/       # API client and services
│   ├── store/          # State management (Redux, Zustand, etc.)
│   ├── styles/         # Global styles and theming
│   └── utils/          # Utility functions
└── package.json        # Dependencies and scripts
```

## Technology Stack (Recommended)

- **Frontend Framework**: React or Vue.js
- **Visualization**: D3.js or Apache ECharts for timeline/charts
- **Mapping**: Leaflet or Mapbox for geographic visualization
- **State Management**: Zustand or Redux
- **Styling**: Tailwind CSS or Styled Components
- **Build Tool**: Vite or Webpack

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test
```

## Performance Considerations

The frontend must load and render very quickly with minimal processing on the client device:

- Lazy load data as users navigate
- Use virtualization for large lists
- Implement caching for API responses
- Optimize bundle size with code splitting
- Use Web Workers for heavy computations

## TODO

- [ ] Set up React/Vue project structure
- [ ] Implement timeline visualization component
- [ ] Implement geographic map component
- [ ] Create dimension pivot UI
- [ ] Implement zoom functionality
- [ ] Add data filtering and search
- [ ] Implement responsive design
- [ ] Add accessibility features (a11y)
- [ ] Performance optimization
- [ ] Mobile PWA support

## Local demo: Lightweight One-Page App (OPA)

A small, self-contained One-Page App (OPA) is included for quick demo and exploration of the API. It is intentionally lightweight (vanilla JS + CSS) so it can be served statically and used as a reference UI.

Files included in this repository under `frontend/`:

- `index.html` — single page app markup
- `style.css` — modern, accessible styling
- `app.js` — client logic: search, pivot, zoom, keyboard navigation

Running the demo:

1. Start the API (see project README):

```bash
docker-compose up --build
```

2. Serve the `frontend/` directory and open in a browser:

```bash
cd frontend
python3 -m http.server 8080
# open http://localhost:8080
```

Notes:

- The SPA expects the API at `http://localhost:8000` by default. If your API runs elsewhere, update `API_BASE` in `app.js`.
- Accessibility: keyboard support (Enter to select, `n`/`p` to navigate), ARIA labels, and visible focus styles are provided.
- Use the Zoom controls to change detail density and the Pivot controls to fetch related dimension results.
