require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

const onboardingRoutes = require('./routes/onboarding');
const roadmapRoutes = require('./routes/roadmap');
const progressRoutes = require('./routes/progress');
const chatRoutes = require('./routes/chat');

const app = express();
const PORT = process.env.PORT || 3001;

// Security & logging middleware
app.use(helmet());
app.use(morgan('combined'));
app.use(cors({ origin: process.env.FRONTEND_URL || 'http://localhost:3000' }));
app.use(express.json({ limit: '2mb' }));

// Health check
app.get('/health', (req, res) => res.json({ status: 'ok', service: 'SkillPilot API' }));

// Routes
app.use('/api/onboarding', onboardingRoutes);
app.use('/api/roadmap', roadmapRoutes);
app.use('/api/progress', progressRoutes);
app.use('/api/chat', chatRoutes);

// Global error handler
app.use((err, req, res, next) => {
  console.error('[ERROR]', err.message);
  console.error('[ERROR stack]', err.stack);
  if (err.response) {
    // axios error — log the upstream response body
    console.error('[ERROR upstream status]', err.response.status);
    console.error('[ERROR upstream data]', JSON.stringify(err.response.data));
  }
  res.status(err.status || 500).json({
    error: err.message || 'Internal server error',
    ...(process.env.NODE_ENV !== 'production' && err.response
      ? { upstream: { status: err.response.status, data: err.response.data } }
      : {}),
  });
});

app.listen(PORT, () => {
  console.log(`SkillPilot backend running on http://localhost:${PORT}`);
});

module.exports = app;
