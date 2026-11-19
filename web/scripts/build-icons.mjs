// Xuất favicon.ico, apple-icon.png, opengraph-image.png từ public/brand/logo-mark.svg.
// Chạy lại khi đổi logo: node scripts/build-icons.mjs (từ thư mục web/).
import { readFile, writeFile, copyFile } from "node:fs/promises";
import sharp from "sharp";

const CANVAS = "#070b10"; // --color-canvas trong app/globals.css
const mark = await readFile(new URL("../public/brand/logo-mark.svg", import.meta.url));
const out = (name) => new URL(`../app/${name}`, import.meta.url);

const png = (size) => sharp(mark, { density: 600 }).resize(size, size).png().toBuffer();

// Đặt biểu tượng giữa một nền màu đặc (apple-icon và OG không nên trong suốt).
async function onCanvas(width, height, markSize) {
  const glyph = await png(markSize);
  return sharp({ create: { width, height, channels: 4, background: CANVAS } })
    .composite([{ input: glyph, gravity: "center" }])
    .png()
    .toBuffer();
}

// ICO chứa các ảnh PNG (định dạng mọi trình duyệt hiện đại đọc được).
function ico(images) {
  const header = Buffer.alloc(6);
  header.writeUInt16LE(0, 0);
  header.writeUInt16LE(1, 2);
  header.writeUInt16LE(images.length, 4);
  let offset = 6 + 16 * images.length;
  const entries = images.map(({ size, data }) => {
    const e = Buffer.alloc(16);
    e.writeUInt8(size >= 256 ? 0 : size, 0);
    e.writeUInt8(size >= 256 ? 0 : size, 1);
    e.writeUInt16LE(1, 4);
    e.writeUInt16LE(32, 6);
    e.writeUInt32LE(data.length, 8);
    e.writeUInt32LE(offset, 12);
    offset += data.length;
    return e;
  });
  return Buffer.concat([header, ...entries, ...images.map((i) => i.data)]);
}

const sizes = [16, 32, 48];
const favicon = ico(await Promise.all(sizes.map(async (size) => ({ size, data: await png(size) }))));
await writeFile(out("favicon.ico"), favicon);
await writeFile(out("apple-icon.png"), await onCanvas(180, 180, 140));
await writeFile(out("opengraph-image.png"), await onCanvas(1200, 630, 440));
await copyFile(new URL("../public/brand/logo-mark.svg", import.meta.url), out("icon.svg"));
console.log("Đã ghi app/favicon.ico, app/icon.svg, app/apple-icon.png, app/opengraph-image.png");
