import { $ } from './utils.js';

export function addSplashLog(msg, type = 'log') {
  const inner = $('splash-logs-inner');
  const splash = $('splash');
  if (!inner || !splash || splash.classList.contains('splash-hidden')) return;
  const line = document.createElement('div');
  line.className = type === 'error' ? 'splash-log-line splash-log-error' : 'splash-log-line';
  let text = typeof msg === 'string' ? msg : (msg?.message || String(msg));
  // Evitar mensaje crudo de Electron "Error invoking remote method 'channel': ..."
  const invokingMatch = text.match(/Error invoking remote method '[^']+':\s*(.+)/);
  if (invokingMatch) text = invokingMatch[1].trim();
  line.textContent = `[${new Date().toLocaleTimeString('en-US', { hour12: false })}] ${text}`;
  inner.appendChild(line);
  inner.parentElement.scrollTop = inner.parentElement.scrollHeight;
}

export function showError(elId, msg) {
  const el = $(elId);
  if (el) {
    el.textContent = msg || '';
    el.style.display = msg ? 'block' : 'none';
  }
}

export function showLoader(text) {
  const overlay = $('global-loader');
  const textEl = $('loader-text');
  if (overlay) {
    if (textEl) textEl.textContent = text || 'Calculando...';
    overlay.classList.add('show');
  }
}

export function hideLoader() {
  const overlay = $('global-loader');
  if (overlay) overlay.classList.remove('show');
}

export function showToast(message, type = 'info') {
  const container = $('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.setAttribute('role', 'status');
  toast.textContent = message;
  container.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('show'));
  const duration = 3200;
  const remove = () => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 280);
  };
  const t = setTimeout(remove, duration);
  toast.addEventListener('click', () => {
    clearTimeout(t);
    remove();
  });
}

export function hideSplash() {
  const splash = $('splash');
  const appEl = $('app');
  if (splash) splash.classList.add('splash-hidden');
  if (appEl) {
    appEl.classList.add('app-ready');
    appEl.classList.remove('app-hidden');
  }
}

function patchConsoleForSplash() {
  const splash = $('splash');
  if (!splash) return;
  const origLog = console.log;
  const origError = console.error;
  console.log = (...args) => {
    if (!splash.classList.contains('splash-hidden')) {
      addSplashLog(args.map((a) => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' '), 'log');
    }
    origLog.apply(console, args);
  };
  console.error = (...args) => {
    if (!splash.classList.contains('splash-hidden')) {
      addSplashLog(args.map((a) => (a instanceof Error ? a.message : typeof a === 'object' ? JSON.stringify(a) : String(a))).join(' '), 'error');
    }
    origError.apply(console, args);
  };
}

export function initSplashLogs() {
  patchConsoleForSplash();
}
