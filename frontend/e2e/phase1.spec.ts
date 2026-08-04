import { expect, test } from "@playwright/test";
import path from "node:path";

test("complete Phase 1 curation workflow persists", async ({ page }) => {
  const projectName = `E2E Road ${Date.now()}`;
  await page.goto("/");
  await expect(page.getByText("Backend connected")).toBeVisible();
  await page.getByRole("link", { name: "Projects", exact: true }).click();
  await page.getByRole("button", { name: "New project" }).click();
  await page.getByLabel("Project name").fill(projectName);
  await page.getByLabel("Description").fill("Playwright workflow");
  await page.getByRole("button", { name: "Create project" }).click();
  await page.getByRole("link", { name: projectName }).click();

  await page.getByLabel("Label name").fill("Vehicle");
  await page.getByLabel("Label shortcut").fill("v");
  await page.getByRole("button", { name: "Add label" }).click();
  await expect(page.getByText("Vehicle").first()).toBeVisible();

  await page
    .getByLabel("Choose files")
    .setInputFiles(path.resolve("tests/fixtures/e2e.avi"));
  await page.getByRole("button", { name: "Import 1 video" }).click();
  await expect(page.getByRole("heading", { name: "e2e.avi" })).toBeVisible();
  await page.getByRole("button", { name: "Extract frames" }).click();
  await page.getByLabel("Value").fill("5");
  await page.getByRole("button", { name: "Start extraction" }).click();
  await expect(page.getByText("completed")).toBeVisible({ timeout: 20_000 });

  await page.getByRole("link", { name: /Open frame gallery/ }).click();
  await expect(page.getByText("6 frames")).toBeVisible();
  const first = page.getByRole("img", { name: "Frame 0" }).locator("..");
  await first.click();
  await page.keyboard.press("v");
  await expect(first.getByText("Vehicle")).toBeVisible();
  await page.getByRole("button", { name: "Mark reviewed" }).click();
  await expect(first.getByText(/reviewed/)).toBeVisible();
  await first.dblclick();
  await expect(page.getByRole("dialog", { name: "Frame 0" })).toBeVisible();
  await page.keyboard.press("f");
  await page.keyboard.press("Escape");

  await page.getByRole("button", { name: "Export dataset" }).click();
  await page.getByLabel("Folder name").fill(`e2e-${Date.now()}`);
  await page.getByRole("button", { name: "Start export" }).click();
  await expect(page.getByText("completed")).toBeVisible({ timeout: 20_000 });
  await page.reload();
  await expect(page.getByText("6 frames")).toBeVisible();
  await expect(page.getByText("Vehicle").first()).toBeVisible();
  await expect(page.getByRole("dialog", { name: "Frame 0" })).toBeVisible();
  await page.keyboard.press("Escape");
  await page.getByLabel("Favorites").check();
  await expect(page.getByText("1 frames")).toBeVisible();
  await expect(page).toHaveURL(/favorite=true/);
  await page.reload();
  await expect(page.getByLabel("Favorites")).toBeChecked();
  await expect(page.getByText("1 frames")).toBeVisible();
});
