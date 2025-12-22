const fs = require("fs");
const path = require("path");

const sourceFile = path.join(__dirname, "frontend/src/lib/api.ts");
const targetFiles = [path.join(__dirname, "admin-panel/src/lib/apiUrl.ts")];
if (!fs.existsSync(sourceFile)) {
  throw new Error(`Source file missing: ${sourceFile}`);
}

const { size } = fs.statSync(sourceFile);
const MAX_SIZE_BYTES = 1024 * 1024; // 1MB safety cap
if (size > MAX_SIZE_BYTES) {
  throw new Error(`Source file too large to process safely: ${sourceFile}`);
}

const replacement = fs.readFileSync(sourceFile, "utf8");

targetFiles.forEach((file) => {
  if (!fs.existsSync(file)) {
    throw new Error(`Target file missing: ${file}`);
  }

  const current = fs.readFileSync(file, "utf8");
  if (current === replacement) {
    console.log(`ℹ️ No change needed: ${file}`);
    return;
  }
  const tempFile = `${file}.tmp`;
  try {
    fs.writeFileSync(tempFile, replacement, "utf8");
    fs.renameSync(tempFile, file);
    console.log(`✅ Updated: ${file}`);
  } catch (error) {
    try {
      if (fs.existsSync(tempFile)) {
        fs.rmSync(tempFile, { force: true });
      }
    } catch (cleanupError) {
      console.warn(`⚠️ Cleanup failed for ${tempFile}:`, cleanupError);
    }
    throw error;
  }
});
