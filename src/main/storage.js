const path = require('path');
const fs = require('fs');
const { app } = require('electron');
const chatsDb = require('./chatsDb');

// When packaged, use userData (writable, e.g. %AppData%\omni-hud) so we can save Groq key and auth
function getAppPath() {
  if (app.isPackaged) return app.getPath('userData');
  return path.join(__dirname, '../../');
}

function getChatsPath() {
  return path.join(getAppPath(), 'chats.json');
}

function getAuthTokenPath() {
  return path.join(getAppPath(), '.auth_token');
}

function getEnvPath() {
  return path.join(getAppPath(), '.env');
}

async function loadChats() {
  if (getAccessToken()) {
    const fromDb = await chatsDb.loadChatsFromDb();
    if (Array.isArray(fromDb)) return fromDb;
  }
  const filePath = getChatsPath();
  try {
    if (fs.existsSync(filePath)) {
      const data = fs.readFileSync(filePath, 'utf8');
      return JSON.parse(data);
    }
  } catch (e) {
    console.error('loadChats error', e);
  }
  return [{ id: 0, title: 'New Session', messages: [] }];
}

async function saveChats(chats) {
  if (getAccessToken()) {
    const result = await chatsDb.saveChatsToDb(chats);
    return result;
  }
  const filePath = getChatsPath();
  try {
    fs.writeFileSync(filePath, JSON.stringify(chats, null, 4), 'utf8');
    return { ok: true };
  } catch (e) {
    console.error('saveChats error', e);
    return { ok: false, error: e.message };
  }
}

const SESSION_FILENAME = '.auth_session';

function getSessionPath() {
  return path.join(getAppPath(), SESSION_FILENAME);
}

function readSession() {
  const filePath = getSessionPath();
  try {
    if (fs.existsSync(filePath)) {
      const raw = fs.readFileSync(filePath, 'utf8').trim();
      const data = JSON.parse(raw);
      if (data && (data.access_token || data.user_id)) return data;
    }
  } catch (_) {}
  return null;
}

function getAuthToken() {
  const session = readSession();
  if (session && session.user_id) return session.user_id;
  const filePath = getAuthTokenPath();
  try {
    if (fs.existsSync(filePath)) return fs.readFileSync(filePath, 'utf8').trim();
  } catch (_) {}
  return null;
}

function getAccessToken() {
  const session = readSession();
  return session ? session.access_token : null;
}

function getRefreshToken() {
  const session = readSession();
  return session ? session.refresh_token : null;
}

function setAuthToken(token) {
  const filePath = getAuthTokenPath();
  try {
    fs.writeFileSync(filePath, token, 'utf8');
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

function setSession(userId, accessToken, refreshToken) {
  const filePath = getSessionPath();
  try {
    fs.writeFileSync(filePath, JSON.stringify({
      user_id: userId,
      access_token: accessToken || '',
      refresh_token: refreshToken || ''
    }), 'utf8');
    fs.writeFileSync(getAuthTokenPath(), userId, 'utf8');
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

function removeAuthToken() {
  const filePath = getAuthTokenPath();
  const sessionPath = getSessionPath();
  try {
    if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
    if (fs.existsSync(sessionPath)) fs.unlinkSync(sessionPath);
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

function getGroqKey() {
  const envPath = getEnvPath();
  try {
    if (fs.existsSync(envPath)) {
      const content = fs.readFileSync(envPath, 'utf8');
      const match = content.match(/GROQ_API_KEY\s*=\s*(.+)/);
      if (match) return match[1].trim().replace(/^["']|["']$/g, '');
    }
  } catch (_) {}
  return process.env.GROQ_API_KEY || null;
}

async function getGroqKeyAsync() {
  const accessToken = getAccessToken();
  const refreshToken = getRefreshToken();
  const baseUrl = (process.env.OMNI_WEB_API_URL || '').replace(/\/$/, '');
  if (accessToken && baseUrl) {
    try {
      const res = await fetch(`${baseUrl}/api/profile/groq-key/value`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'X-Refresh-Token': refreshToken || '',
        },
      });
      if (res.ok) {
        const data = await res.json();
        if (data && typeof data.key === 'string' && data.key.trim()) return data.key.trim();
      }
    } catch (_) {}
  }
  return getGroqKey();
}

function setGroqKey(key) {
  const envPath = getEnvPath();
  let lines = [];
  try {
    if (fs.existsSync(envPath)) {
      lines = fs.readFileSync(envPath, 'utf8').split('\n');
    }
  } catch (_) {}
  let found = false;
  const newLines = lines.map((line) => {
    if (/^\s*GROQ_API_KEY\s*=/.test(line)) {
      found = true;
      return `GROQ_API_KEY=${key}`;
    }
    return line;
  });
  if (!found) newLines.push(`GROQ_API_KEY=${key}`);
  try {
    fs.writeFileSync(envPath, newLines.join('\n'), 'utf8');
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

module.exports = {
  loadChats,
  saveChats,
  getAuthToken,
  getAccessToken,
  getRefreshToken,
  setAuthToken,
  setSession,
  removeAuthToken,
  getGroqKey,
  getGroqKeyAsync,
  setGroqKey
};
