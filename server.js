/**
 * Express server for JS frontend
 */
const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();
const PORT = process.env.PORT || 3001;

// In Codespaces or local, using localhost for backend (same container network)
// In production, use the BACKEND_URL environment variable
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

// Serve static files from public folder
app.use(express.static(path.join(__dirname, 'public')));

// Proxy API routes to backend (use http-proxy-middleware for proper multipart handling)
app.use('/api/', createProxyMiddleware({
  target: `${BACKEND_URL}/api`,  // Include /api in target
  changeOrigin: true
}));

app.get('/search', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Serve index.html for home and all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Frontend server running on http://localhost:${PORT}`);
  console.log(`Backend URL: ${BACKEND_URL}`);
});
