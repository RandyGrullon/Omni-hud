const path = require('path');
const fs = require('fs');
const FormData = require('form-data');
const storage = require('./storage');

require('dotenv').config({ path: path.join(__dirname, '../../.env') });

async function transcribe(audioBase64) {
  const apiKey = storage.getGroqKey() || process.env.GROQ_API_KEY;
  if (!apiKey) return { ok: false, error: 'GROQ_API_KEY not set' };

  const { app } = require('electron');
  const tempPath = path.join(app.getPath('temp'), `omni_voice_${Date.now()}.webm`);
  const buf = Buffer.from(audioBase64, 'base64');
  fs.writeFileSync(tempPath, buf);

  const form = new FormData();
  form.append('file', fs.createReadStream(tempPath), { filename: 'audio.webm', contentType: 'audio/webm' });
  form.append('model', 'whisper-large-v3');

  try {
    const response = await fetch('https://api.groq.com/openai/v1/audio/transcriptions', {
      method: 'POST',
      headers: { Authorization: `Bearer ${apiKey}`, ...form.getHeaders() },
      body: form
    });
    const data = await response.json();
    try { fs.unlinkSync(tempPath); } catch (_) {}
    if (data.error) return { ok: false, error: data.error.message };
    return { ok: true, text: data.text || '' };
  } catch (e) {
    try { fs.unlinkSync(tempPath); } catch (_) {}
    return { ok: false, error: e.message };
  }
}

module.exports = {
  transcribe
};
