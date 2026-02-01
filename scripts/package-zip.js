import fs from "fs";
import path from "path";
import { execFile } from "child_process";
import archiver from "archiver";

const repoRoot = process.cwd();
const outputDir = path.join(repoRoot, "artifacts");
const outputFile = path.join(outputDir, "EasyReaderADHD-Plugin.zip");

function execGit(args) {
  return new Promise((resolve, reject) => {
    execFile("git", args, { cwd: repoRoot }, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(stderr || error.message));
        return;
      }
      resolve(stdout);
    });
  });
}

function normalizeZipName(filePath) {
  return filePath.replace(/\\/g, "/");
}

async function buildZip() {
  await fs.promises.mkdir(outputDir, { recursive: true });

  const stdout = await execGit(["ls-files", "-c", "-o", "--exclude-standard"]);
  const files = stdout.split(/\r?\n/).filter(Boolean);

  if (files.length === 0) {
    console.log("⚠️ 未找到可打包文件");
    return;
  }

  const output = fs.createWriteStream(outputFile);
  const archive = archiver("zip", { zlib: { level: 9 } });

  const finalizePromise = new Promise((resolve, reject) => {
    output.on("close", resolve);
    output.on("error", reject);
    archive.on("error", reject);
  });

  archive.pipe(output);

  for (const file of files) {
    const fullPath = path.join(repoRoot, file);
    if (!fs.existsSync(fullPath)) continue;
    const stat = fs.statSync(fullPath);
    if (!stat.isFile()) continue;
    archive.file(fullPath, { name: normalizeZipName(file) });
  }

  await archive.finalize();
  await finalizePromise;

  console.log(`📦 已生成压缩包: ${outputFile}`);
}

buildZip().catch((error) => {
  console.error("❌ 打包失败:", error);
  process.exit(1);
});
