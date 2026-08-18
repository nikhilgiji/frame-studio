import { defineConfig, devices } from "@playwright/test";
import { execFileSync } from "node:child_process";

execFileSync("../.venv/bin/python", ["../scripts/create_test_video.py"]);

const apiPort = process.env.PLAYWRIGHT_API_PORT ?? "8000";
const webPort = process.env.PLAYWRIGHT_WEB_PORT ?? "3000";
const apiUrl = `http://127.0.0.1:${apiPort}`;
const webUrl = `http://127.0.0.1:${webPort}`;

export default defineConfig({
  testDir: "./e2e",
  timeout: 45_000,
  fullyParallel: false,
  use: { baseURL: webUrl, trace: "retain-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: `cd ../backend && VISION_CURATOR_DATABASE_URL=sqlite:///../storage/e2e.db VISION_CURATOR_STORAGE_ROOT=../storage/e2e ../.venv/bin/alembic upgrade head && VISION_CURATOR_DATABASE_URL=sqlite:///../storage/e2e.db VISION_CURATOR_STORAGE_ROOT=../storage/e2e VISION_CURATOR_CORS_ORIGINS='["${webUrl}"]' ../.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port ${apiPort}`,
      url: `${apiUrl}/api/v1/health`,
      reuseExistingServer: false,
    },
    {
      command: `VITE_API_URL=${apiUrl}/api/v1 npm run dev -- --port ${webPort}`,
      url: webUrl,
      reuseExistingServer: false,
    },
  ],
});
