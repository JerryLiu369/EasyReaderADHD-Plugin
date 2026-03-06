import esbuild from "esbuild";
import fs from "fs";
import path from "path";

const outDir = "dist";

// watch 模式 / NODE_ENV=development 时视为开发构建
const isDev =
  process.argv.includes("--watch") || process.env.NODE_ENV === "development";

const options = {
  entryPoints: {
    content: "src/content/index.js",
    background: "src/background/index.js",
  },
  outdir: outDir,
  bundle: true,
  minify: !isDev,
  sourcemap: isDev ? "inline" : false,
  target: "es2020",
  format: "iife",
  logLevel: "info",
  // 注入编译期常量，esbuild 会常量折叠并消除 if (false) 分支（生产包零日志开销）
  define: {
    "process.env.NODE_ENV": isDev ? '"development"' : '"production"',
  },
};

async function build() {
  try {
    console.log("🔨 构建开始...");
    await esbuild.build(options);
    console.log("✅ 构建完成！");
    console.log("📦 输出文件:");
    console.log("   - dist/content.js");
    console.log("   - dist/background.js");
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
