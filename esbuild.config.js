import esbuild from "esbuild";
import fs from "fs";
import path from "path";

const outDir = ".";

const options = {
  entryPoints: {
    content: "src/content/index.js",
    background: "src/background/index.js",
  },
  outdir: outDir,
  bundle: true,
  minify: true,
  sourcemap: false,
  target: "es2020",
  format: "iife",
  logLevel: "info",
};

async function build() {
  try {
    console.log("🔨 构建开始...");
    await esbuild.build(options);
    console.log("✅ 构建完成！");
    console.log("📦 输出文件:");
    console.log("   - content.js");
    console.log("   - background.js");
  } catch (error) {
    console.error("❌ 构建失败:", error);
    process.exit(1);
  }
}

if (process.argv.includes("--watch")) {
  const context = await esbuild.context(options);
  await context.watch();
  console.log("👀 监视模式启动...");
  console.log("按 Ctrl+C 停止");
} else {
  build();
}
