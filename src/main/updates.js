const config = require('./config');

async function checkUpdates() {
  try {
    const res = await fetch(config.UPDATE_URL, { signal: AbortSignal.timeout(5000) });
    if (!res.ok) return { ok: false, error: 'Connection error' };
    const data = await res.json();
    const remote = data.version || config.VERSION;
    const current = config.VERSION;
    if (remote > current) {
      return { ok: true, update: true, version: remote, url: data.url || '#' };
    }
    return { ok: true, update: false, version: current };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

module.exports = { checkUpdates };
