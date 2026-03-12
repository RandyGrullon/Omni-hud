const { desktopCapturer, screen: electronScreen } = require('electron');

async function getSources() {
  const size = electronScreen.getPrimaryDisplay().size;
  const sources = await desktopCapturer.getSources({
    types: ['screen'],
    thumbnailSize: size
  });
  return sources.map((s) => ({ id: s.id, name: s.name, thumbnail: s.thumbnail.toDataURL() }));
}

async function captureRegion(bounds) {
  const display = electronScreen.getPrimaryDisplay();
  const size = display.size;
  const scale = display.scaleFactor || 1;
  const sources = await desktopCapturer.getSources({
    types: ['screen'],
    thumbnailSize: { width: size.width * scale, height: size.height * scale }
  });
  if (!sources.length) return { ok: false, error: 'No source' };
  const img = sources[0].thumbnail;
  if (!img) return { ok: false, error: 'No thumbnail' };

  const { x = 0, y = 0, width, height } = bounds || {};
  if (width <= 0 || height <= 0) return { ok: false, error: 'Invalid bounds' };

  let cropped = img;
  if (typeof img.crop === 'function') {
    cropped = img.crop({
      x: Math.round(x * scale),
      y: Math.round(y * scale),
      width: Math.round(width * scale),
      height: Math.round(height * scale)
    });
  }
  const png = cropped.toPNG();
  const base64 = Buffer.isBuffer(png) ? png.toString('base64') : png;
  return { ok: true, imageBase64: base64 };
}

module.exports = {
  getSources,
  captureRegion
};
