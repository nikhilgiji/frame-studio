import { expect, test } from "@playwright/test";
import path from "node:path";

test("complete Phase 1 curation workflow persists", async ({ page }) => {
  const projectName = `E2E Road ${Date.now()}`;
  await page.goto("/");
  await expect(page.getByText("Backend connected")).toBeVisible();
  const onboarding = page.getByRole("button", { name: "Start curating" });
  if (await onboarding.isVisible()) await onboarding.click();
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
  await expect(page.getByText("completed", { exact: true })).toBeVisible({
    timeout: 20_000,
  });

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
  await expect(page.getByText("completed", { exact: true })).toBeVisible({
    timeout: 20_000,
  });
  await page.reload();
  await expect(page.getByText("6 frames")).toBeVisible();
  const restoredViewer = page.getByRole("dialog", { name: "Frame 0" });
  await expect(restoredViewer).toBeVisible();
  await expect(restoredViewer.getByText("Vehicle")).toBeVisible();
  await page.keyboard.press("Escape");
  await page.getByLabel("Favorites").check();
  await expect(page.getByText("1 frames", { exact: true })).toBeVisible();
  await expect(page).toHaveURL(/favorite=true/);
  await page.reload();
  await expect(page.getByLabel("Favorites")).toBeChecked();
  await expect(page.getByText("1 frames", { exact: true })).toBeVisible();
  await expect(page.getByRole("dialog", { name: "Frame 0" })).toBeVisible();
  await page.keyboard.press("Escape");

  await page.getByLabel("Video filter").selectOption({ label: "e2e.avi" });
  await expect(
    page.getByRole("region", { name: "Video timeline" }),
  ).toBeVisible();
  const frameJump = page.locator("label").filter({ hasText: "Frame number" });
  await frameJump.getByRole("spinbutton").fill("10");
  await frameJump.getByRole("button", { name: "Jump" }).click();
  await expect(page.getByRole("dialog", { name: "Frame 10" })).toBeVisible();
  await page.keyboard.press("Escape");

  await page.getByText("Review queues").click();
  await page.getByLabel("Queue name").fill("Favorite queue");
  await page.getByRole("button", { name: "Create queue" }).click();
  await expect(page.getByText("Favorite queue")).toBeVisible();
  await page.getByRole("button", { name: "Resume" }).click();
  await expect(page.getByRole("dialog", { name: "Frame 0" })).toBeVisible();
});

test("Phase 2 settings persist and remain responsive", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/settings");
  const previous = page.getByLabel("Viewer: previous", { exact: true });
  await previous.press("j");
  await page.getByRole("button", { name: "Save shortcuts" }).click();
  await expect(page.getByRole("status")).toHaveText("Settings saved");
  await page.getByLabel("Dark mode").uncheck();
  await page.reload();
  await expect(
    page.getByLabel("Viewer: previous", { exact: true }),
  ).toHaveValue("j");
  await expect(page.getByLabel("Dark mode")).not.toBeChecked();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
});
