import { defineConfig, devices } from "@playwright/test";
import { execFileSync } from "node:child_process";

execFileSync("../.venv/bin/python", ["../scripts/create_test_video.py"]);

export default defineConfig({
  testDir: "./e2e",
  timeout: 45_000,
  fullyParallel: false,
  use: { baseURL: "http://127.0.0.1:3000", trace: "retain-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command:
        "cd ../backend && VISION_CURATOR_DATABASE_URL=sqlite:///../storage/e2e.db VISION_CURATOR_STORAGE_ROOT=../storage/e2e ../.venv/bin/alembic upgrade head && VISION_CURATOR_DATABASE_URL=sqlite:///../storage/e2e.db VISION_CURATOR_STORAGE_ROOT=../storage/e2e ../.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000",
      url: "http://127.0.0.1:8000/api/v1/health",
      reuseExistingServer: false,
    },
    {
      command: "npm run dev",
      url: "http://127.0.0.1:3000",
      reuseExistingServer: false,
    },
  ],
});
