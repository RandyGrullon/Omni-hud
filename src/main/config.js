const path = require('path');
// Load .env from project root
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

const PAGES = {
  LOGIN: 0,
  ACTIVATION: 1,
  CONFIG: 2,
  CHAT: 3,
  FILE: 4,
  PROFILE: 5
};

const WINDOW = {
  WIDTH: 950,
  HEIGHT: 700
};

const GROQ_MODEL = 'llama-3.3-70b-versatile';
const VISION_MODEL = 'llama-3.2-11b-vision-preview';
const DEVELOPER_SYSTEM_PROMPT = (
  'LANGUAGE RULES: YOU MUST DETECT THE USER\'S LANGUAGE AND REPLY IN THE SAME LANGUAGE. ' +
  'IF THE USER WRITES IN ENGLISH, REPLY IN ENGLISH. IF THE USER WRITES IN SPANISH, REPLY IN SPANISH. ' +
  'Act as a Senior Full Stack Developer. Provide Markdown code and concise explanations.'
);

const MAX_RECORDING_DURATION_SEC = 60;
const MAX_FILE_SIZE_MB = 10;
const VERSION = '1.0.2';
const UPDATE_URL = 'https://raw.githubusercontent.com/RandyGrullon/Omni-hud/main/version.json';

const HOTKEYS = {
  INVOKE: 'CommandOrControl+Space',
  VOICE_SYSTEM: 'CommandOrControl+Shift+R',
  VOICE_MIC: 'CommandOrControl+Shift+M',
  VOICE_SYSTEM_AUDIO: 'CommandOrControl+Shift+P',
  CLEAR_CHAT: 'CommandOrControl+L'
};

module.exports = {
  PAGES,
  WINDOW,
  GROQ_MODEL,
  VISION_MODEL,
  DEVELOPER_SYSTEM_PROMPT,
  MAX_RECORDING_DURATION_SEC,
  MAX_FILE_SIZE_MB,
  VERSION,
  UPDATE_URL,
  HOTKEYS,
  getEnv: (key) => process.env[key]
};
