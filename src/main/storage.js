const path = require('path');
const fs = require('fs');
const { app } = require('electron');

function getAppPath() {
  return app.isPackaged ? path.dirname(app.getPath('exe')) : path.join(__dirname, '../../');
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

function loadChats() {
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

function saveChats(chats) {
  const filePath = getChatsPath();
  try {
    fs.writeFileSync(filePath, JSON.stringify(chats, null, 4), 'utf8');
    return { ok: true };
  } catch (e) {
    console.error('saveChats error', e);
    return { ok: false, error: e.message };
  }
}

function getAuthToken() {
  const filePath = getAuthTokenPath();
  try {
    if (fs.existsSync(filePath)) {
      return fs.readFileSync(filePath, 'utf8').trim();
    }
  } catch (_) {}
  return null;
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

function removeAuthToken() {
  const filePath = getAuthTokenPath();
  try {
    if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
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
  setAuthToken,
  removeAuthToken,
  getGroqKey,
  setGroqKey
};
