const path = require('path');
const fs = require('fs');
const config = require('./config');

const MAX_SIZE = config.MAX_FILE_SIZE_MB * 1024 * 1024;

function extract(filePath) {
  return new Promise((resolve, reject) => {
    try {
      const stat = fs.statSync(filePath);
      if (stat.size > MAX_SIZE) {
        return resolve({ ok: false, error: `File too large (max ${config.MAX_FILE_SIZE_MB}MB)` });
      }
      const ext = path.extname(filePath).toLowerCase();
      const filename = path.basename(filePath);

      if (ext === '.docx') {
        const mammoth = require('mammoth');
        const buffer = fs.readFileSync(filePath);
        mammoth.extractRawText({ buffer })
          .then((result) => resolve({ ok: true, filename, content: result.value }))
          .catch((e) => resolve({ ok: false, error: e.message }));
        return;
      }
      if (ext === '.pdf') {
        const pdf = require('pdf-parse');
        const dataBuffer = fs.readFileSync(filePath);
        pdf(dataBuffer)
          .then((data) => resolve({ ok: true, filename, content: data.text }))
          .catch((e) => resolve({ ok: false, error: e.message }));
        return;
      }
      if (ext === '.xlsx' || ext === '.xls') {
        const XLSX = require('xlsx');
        const wb = XLSX.readFile(filePath, { type: 'file' });
        const lines = [];
        wb.SheetNames.forEach((name) => {
          const sheet = wb.Sheets[name];
          const rows = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });
          rows.forEach((row) => {
            const line = Array.isArray(row) ? row.join('\t') : String(row);
            if (line.trim()) lines.push(line);
          });
        });
        return resolve({ ok: true, filename, content: lines.join('\n') });
      }
      resolve({ ok: false, error: 'Unsupported format (DOCX, PDF, XLSX)' });
    } catch (e) {
      resolve({ ok: false, error: e.message });
    }
  });
}

module.exports = { extract };
