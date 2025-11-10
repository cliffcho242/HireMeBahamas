const axios = require('axios');

// Minimal browser-like shim for Node to support localStorage and CustomEvent
global.window = global.window || {};
global.window._dispatchedEvents = global.window._dispatchedEvents || [];

global.window.addEventListener = function (name, fn) {
  this._listeners = this._listeners || {};
  (this._listeners[name] = this._listeners[name] || []).push(fn);
};

global.window.dispatchEvent = function (event) {
  this._dispatchedEvents.push(event);
  const listeners = (this._listeners && this._listeners[event.type]) || [];
  listeners.forEach(fn => {
    try { fn(event); } catch (e) { /* ignore */ }
  });
};

class CustomEvent {
  constructor(type, opts) {
    this.type = type;
    this.detail = opts && opts.detail;
  }
}
global.CustomEvent = CustomEvent;

// Minimal localStorage
const storage = {};
global.localStorage = {
  getItem: (k) => (k in storage ? storage[k] : null),
  setItem: (k, v) => { storage[k] = String(v); },
  removeItem: (k) => { delete storage[k]; },
  clear: () => { Object.keys(storage).forEach(k => delete storage[k]); }
};

// Create axios instance and interceptors similar to services/api.ts behavior
const api = axios.create({ baseURL: 'http://localhost:9999' });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  config.headers = config.headers || {};
  config.headers['X-Retry-Count'] = config.headers['X-Retry-Count'] || 0;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config || {};
    // Simulate logging
    // console.error('API Error:', error?.response?.status);

    if (error.response && error.response.status === 401) {
      const isAuthEndpoint = (config.url || '').includes('/auth/') || (config.url || '').includes('/profile');
      try { localStorage.removeItem('token'); } catch (e) {}
      // dispatch event
      try {
        window.dispatchEvent(new CustomEvent('auth:logout', { detail: { url: config.url, isAuthEndpoint } }));
      } catch (e) {
        // fallback
      }
    }

    return Promise.reject(error);
  }
);

// Attach a listener to record that auth:logout was received
let logoutEventReceived = false;
window.addEventListener('auth:logout', (e) => {
  logoutEventReceived = true;
  console.log('auth:logout event received in test, detail=', e.detail);
});

// Set token to simulate logged-in state
localStorage.setItem('token', 'FAKE_TOKEN');

// Make a request that will be mocked by adapter to return a 401 error
// We'll use a custom adapter that always returns a rejected response with 401
api.defaults.adapter = async function mockAdapter(config) {
  // emulate some async delay
  await new Promise(r => setTimeout(r, 50));
  const err = new Error('Request failed with status code 401');
  err.config = config;
  err.response = { status: 401, data: { message: 'Unauthorized (mock)' }, config };
  return Promise.reject(err);
};

(async () => {
  try {
    await api.get('/api/test');
    console.error('Request unexpectedly succeeded');
    process.exit(2);
  } catch (err) {
    // After error handling, check expectations
    const tokenAfter = localStorage.getItem('token');
    const dispatched = window._dispatchedEvents.filter(e => e.type === 'auth:logout');

    console.log('tokenAfter=', tokenAfter);
    console.log('logoutEventReceived=', logoutEventReceived);
    console.log('dispatched count=', dispatched.length);

    if (tokenAfter === null && logoutEventReceived && dispatched.length > 0) {
      console.log('TEST PASS: token cleared and auth:logout dispatched');
      process.exit(0);
    } else {
      console.error('TEST FAIL');
      process.exit(3);
    }
  }
})();
