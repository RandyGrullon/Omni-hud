const { app, BrowserWindow, ipcMain, globalShortcut, dialog, session, desktopCapturer } = require('electron');
const path = require('path');
const fs = require('fs');
const config = require('../src/main/config');
const storage = require('../src/main/storage');
const auth = require('../src/main/auth');
const ai = require('../src/main/ai');
const voice = require('../src/main/voice');
const screen = require('../src/main/screen');
const documents = require('../src/main/documents');

let mainWindow = null;
let lockFilePath = null;

function getLockFilePath() {
  return path.join(app.getPath('userData'), 'omni_hud.lock');
}

function isProcessAlive(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (e) {
    return false;
  }
}

function acquireLock() {
  lockFilePath = getLockFilePath();
  try {
    const fd = fs.openSync(lockFilePath, 'wx');
    fs.writeSync(fd, process.pid.toString());
    fs.closeSync(fd);
    return true;
  } catch (e) {
    if (e.code !== 'EEXIST') throw e;
    try {
      const pid = parseInt(fs.readFileSync(lockFilePath, 'utf8'), 10);
      if (!Number.isNaN(pid) && pid !== process.pid && !isProcessAlive(pid)) {
        fs.unlinkSync(lockFilePath);
        return acquireLock();
      }
    } catch (_) {
      try { fs.unlinkSync(lockFilePath); } catch (_) {}
      return acquireLock();
    }
    return false;
  }
}

function releaseLock() {
  if (!lockFilePath) return;
  try {
    if (fs.existsSync(lockFilePath)) fs.unlinkSync(lockFilePath);
  } catch (_) {}
}

const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
  process.exit(0);
}

app.on('second-instance', () => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.show();
    mainWindow.focus();
  }
});

if (!acquireLock()) {
  app.quit();
  process.exit(0);
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: config.WINDOW.WIDTH,
    height: config.WINDOW.HEIGHT,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    show: false
  });

  mainWindow.setContentProtection(true);

  mainWindow.loadFile(path.join(__dirname, '../src/renderer/index.html'));

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.focus();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function registerShortcuts() {
  globalShortcut.register(config.HOTKEYS.INVOKE, () => {
    if (!mainWindow) return;
    if (mainWindow.isVisible()) mainWindow.hide();
    else {
      mainWindow.show();
      mainWindow.focus();
    }
  });

  globalShortcut.register(config.HOTKEYS.VOICE_SYSTEM, () => {
    if (mainWindow && mainWindow.webContents) {
      if (!mainWindow.isVisible()) mainWindow.show();
      mainWindow.focus();
      mainWindow.webContents.send('voice-trigger', 'system');
    }
  });

  globalShortcut.register(config.HOTKEYS.VOICE_MIC, () => {
    if (mainWindow && mainWindow.webContents) {
      if (!mainWindow.isVisible()) mainWindow.show();
      mainWindow.focus();
      mainWindow.webContents.send('voice-trigger', 'mic');
    }
  });

  globalShortcut.register(config.HOTKEYS.VOICE_SYSTEM_AUDIO, () => {
    if (mainWindow && mainWindow.webContents) {
      if (!mainWindow.isVisible()) mainWindow.show();
      mainWindow.webContents.send('voice-trigger', 'system_audio');
    }
  });

  globalShortcut.register(config.HOTKEYS.CLEAR_CHAT, () => {
    if (mainWindow && mainWindow.webContents) mainWindow.webContents.send('clear-chat-request');
  });
}

app.whenReady().then(() => {
  if (app.isPackaged) {
    try {
      require('dotenv').config({ path: path.join(app.getPath('userData'), '.env') });
    } catch (_) {}
    // Asegurar OMNI_WEB_API_URL en instalación (por si config.js no cargó supabase.config.json)
    if (!process.env.OMNI_WEB_API_URL) {
      try {
        const configPath = path.join(__dirname, '../src/main/supabase.config.json');
        const data = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        if (data && data.OMNI_WEB_API_URL) process.env.OMNI_WEB_API_URL = data.OMNI_WEB_API_URL;
      } catch (_) {}
    }
  }
  createWindow();
  registerShortcuts();

  session.defaultSession.setDisplayMediaRequestHandler((request, callback) => {
    desktopCapturer.getSources({ types: ['screen'] }).then((sources) => {
      if (sources.length === 0) {
        callback({});
        return;
      }
      try {
        callback({ video: sources[0], audio: 'loopback' });
      } catch (e) {
        callback({});
      }
    }).catch(() => callback({}));
  });

  ipcMain.handle('window:close', () => { if (mainWindow) mainWindow.close(); });
  ipcMain.handle('window:isVisible', () => mainWindow ? mainWindow.isVisible() : false);

  ipcMain.handle('storage:loadChats', async () => {
    try {
      return await storage.loadChats();
    } catch (e) {
      console.error('storage:loadChats', e);
      return [{ id: 0, title: 'New Session', messages: [] }];
    }
  });
  ipcMain.handle('storage:saveChats', (_, chats) => storage.saveChats(chats));
  ipcMain.handle('storage:getAuthToken', () => {
    try {
      return storage.getAuthToken();
    } catch (e) {
      console.error('storage:getAuthToken', e);
      return null;
    }
  });
  ipcMain.handle('storage:setAuthToken', (_, token) => storage.setAuthToken(token));
  ipcMain.handle('storage:removeAuthToken', () => storage.removeAuthToken());
  ipcMain.handle('storage:getGroqKey', () => storage.getGroqKey());
  ipcMain.handle('storage:getGroqKeyAsync', async () => {
    try {
      return await storage.getGroqKeyAsync();
    } catch (e) {
      console.error('storage:getGroqKeyAsync', e);
      return storage.getGroqKey();
    }
  });
  ipcMain.handle('storage:setGroqKey', (_, key) => storage.setGroqKey(key));
  ipcMain.handle('storage:syncGroqKeyToWeb', async (_, key) => {
    const accessToken = storage.getAccessToken();
    const refreshToken = storage.getRefreshToken();
    if (!key || typeof key !== 'string') {
      return { ok: false, error: 'No key provided' };
    }
    if (!accessToken) {
      return { ok: false, error: 'Session expired or incomplete. Log out and log in again to save the key to the cloud.' };
    }
    const baseUrl = (process.env.OMNI_WEB_API_URL || 'https://localhost:3000').replace(/\/$/, '');
    const url = `${baseUrl}/api/profile/groq-key`;
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
          'X-Refresh-Token': refreshToken || '',
        },
        body: JSON.stringify({ key: key.trim() }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        return { ok: false, error: (data && data.error) || res.statusText };
      }
      return { ok: true };
    } catch (e) {
      return { ok: false, error: e && e.message ? e.message : 'Network error' };
    }
  });

  ipcMain.handle('profile:update', async (_, payload) => {
    const accessToken = storage.getAccessToken();
    const refreshToken = storage.getRefreshToken();
    if (!accessToken) return { ok: false, error: 'No session' };
    const baseUrl = (process.env.OMNI_WEB_API_URL || '').replace(/\/$/, '');
    if (!baseUrl) return { ok: false, error: 'OMNI_WEB_API_URL not set' };
    try {
      const res = await fetch(`${baseUrl}/api/profile`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
          'X-Refresh-Token': refreshToken || '',
        },
        body: JSON.stringify({
          first_name: payload.first_name,
          last_name: payload.last_name,
          username: payload.username,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) return { ok: false, error: (data && data.error) || res.statusText };
      return { ok: true, profile: data };
    } catch (e) {
      return { ok: false, error: e && e.message ? e.message : 'Network error' };
    }
  });

  ipcMain.handle('auth:login', async (_, email, password) => auth.login(email, password));
  ipcMain.handle('auth:logout', () => auth.logout());
  ipcMain.handle('auth:getProfile', async () => auth.getProfile());
  ipcMain.handle('auth:validateAccess', async () => {
    try {
      return await auth.validateAccess();
    } catch (e) {
      console.error('auth:validateAccess', e);
      return { ok: false, needLogin: true, error: e && e.message ? e.message : 'Validation failed' };
    }
  });
  ipcMain.handle('auth:activate', async (_, key) => auth.activateKey(key));

  ipcMain.handle('ai:stream', async (_, payload) => {
    try {
      const result = await ai.streamChat(payload, (chunk) => {
        if (mainWindow && mainWindow.webContents) mainWindow.webContents.send('ai-chunk', chunk);
      });
      if (mainWindow && mainWindow.webContents) {
        if (result.ok) mainWindow.webContents.send('ai-done', result.fullResponse || '');
        else mainWindow.webContents.send('ai-error', result.error || 'Unknown error');
      }
      return result;
    } catch (e) {
      const errMsg = e && (e.message || e.toString) ? (e.message || e.toString()) : 'Unknown error';
      if (mainWindow && mainWindow.webContents) mainWindow.webContents.send('ai-error', errMsg);
      return { ok: false, error: errMsg };
    }
  });

  ipcMain.on('ai-cancel', () => ai.cancel());

  ipcMain.handle('voice:transcribe', async (_, audioBase64) => voice.transcribe(audioBase64));

  ipcMain.handle('screen:getSources', () => screen.getSources());
  ipcMain.handle('screen:captureRegion', (_, bounds) => screen.captureRegion(bounds));
  ipcMain.handle('screen:startRegionSelect', () => {
    return new Promise((resolve) => {
      if (mainWindow) mainWindow.hide();
      const selectorWindow = new BrowserWindow({
        fullscreen: true,
        frame: false,
        transparent: true,
        skipTaskbar: true,
        webPreferences: {
          preload: path.join(__dirname, 'selector-preload.js'),
          contextIsolation: true
        }
      });
      selectorWindow.setIgnoreMouseEvents(false);
      selectorWindow.loadFile(path.join(__dirname, '../src/renderer/selector.html'));
      ipcMain.once('region-selected', (_, bounds) => {
        selectorWindow.close();
        if (mainWindow) mainWindow.show();
        resolve(bounds);
      });
      selectorWindow.on('closed', () => {
        ipcMain.removeAllListeners('region-selected');
        if (mainWindow) mainWindow.show();
        resolve(null);
      });
    });
  });

  ipcMain.handle('documents:extract', async (_, filePath) => documents.extract(filePath));
  ipcMain.handle('dialog:openFile', async () => {
    const { filePaths } = await dialog.showOpenDialog(mainWindow, {
      properties: ['openFile'],
      filters: [
        { name: 'Documents', extensions: ['docx', 'pdf', 'xlsx', 'xls'] }
      ]
    });
    return filePaths && filePaths[0] ? filePaths[0] : null;
  });

  ipcMain.handle('files:listDirectory', async (_, dirPath) => {
    try {
      const os = require('os');
      const basePath = dirPath || os.homedir();
      const entries = fs.readdirSync(basePath, { withFileTypes: true });
      const list = entries.map((ent) => ({
        name: ent.name,
        path: path.join(basePath, ent.name),
        isDirectory: ent.isDirectory()
      }));
      return { ok: true, entries: list };
    } catch (e) {
      return { ok: false, error: e.message, entries: [] };
    }
  });

  ipcMain.handle('dialog:openDirectory', async () => {
    const { filePaths } = await dialog.showOpenDialog(mainWindow, {
      properties: ['openDirectory']
    });
    return filePaths && filePaths[0] ? filePaths[0] : null;
  });

  ipcMain.handle('updates:check', async () => {
    const { checkUpdates } = require('../src/main/updates');
    return checkUpdates();
  });
});

app.on('window-all-closed', () => {
  globalShortcut.unregisterAll();
  releaseLock();
  app.quit();
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});
