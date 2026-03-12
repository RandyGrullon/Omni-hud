const Groq = require('groq-sdk');
const path = require('path');
const config = require('./config');
const storage = require('./storage');

require('dotenv').config({ path: path.join(__dirname, '../../.env') });

let client = null;
let abortController = null;

function getClient() {
  const apiKey = storage.getGroqKey() || process.env.GROQ_API_KEY;
  if (!apiKey) throw new Error('GROQ_API_KEY not set');
  if (!client) client = new Groq({ apiKey });
  return client;
}

function cancel() {
  if (abortController) abortController.abort();
}

async function streamChat(payload, onChunk) {
  const { prompt, history, imageB64 } = payload;
  abortController = new AbortController();
  const groq = getClient();

  const model = imageB64 ? config.VISION_MODEL : config.GROQ_MODEL;
  const messages = [{ role: 'system', content: config.DEVELOPER_SYSTEM_PROMPT }];

  for (const msg of history || []) {
    messages.push({
      role: msg.role === 'model' ? 'assistant' : 'user',
      content: msg.content
    });
  }

  const userContent = [];
  if (imageB64) {
    userContent.push({
      type: 'image_url',
      image_url: { url: `data:image/jpeg;base64,${imageB64}` }
    });
  }
  userContent.push({ type: 'text', text: prompt });
  messages.push({ role: 'user', content: userContent });

  let fullResponse = '';
  try {
    const stream = await groq.chat.completions.create({
      model,
      messages,
      temperature: 0.7,
      max_tokens: 2048,
      stream: true
    });

    for await (const chunk of stream) {
      if (abortController.signal.aborted) break;
      const text = chunk.choices?.[0]?.delta?.content;
      if (text) {
        fullResponse += text;
        onChunk(text);
      }
    }
    return { ok: true, fullResponse };
  } catch (e) {
    if (e.name === 'AbortError') return { ok: true, fullResponse };
    return { ok: false, error: e.message };
  } finally {
    abortController = null;
  }
}

module.exports = {
  streamChat,
  cancel
};
