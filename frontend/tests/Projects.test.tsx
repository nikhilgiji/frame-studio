import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { App } from "../src/App";
import type { Project } from "../src/types/project";

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

test("creates, edits, opens, and deletes a project with confirmation", async () => {
  const user = userEvent.setup();
  let projects: Project[] = [];
  vi.spyOn(window, "confirm").mockReturnValue(true);
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
    const url = String(input);
    const method = init?.method ?? "GET";
    if (url.endsWith("/projects") && method === "GET")
      return json({ data: projects, error: null });
    if (url.endsWith("/projects") && method === "POST") {
      const body = JSON.parse(String(init?.body)) as {
        name: string;
        description: string;
      };
      projects = [
        {
          id: 1,
          ...body,
          root_path: "/storage/projects/road",
          created_at: "2026-08-04T10:00:00Z",
          updated_at: "2026-08-04T10:00:00Z",
        },
      ];
      return json({ data: projects[0], error: null }, 201);
    }
    if (url.endsWith("/projects/1") && method === "PATCH") {
      const body = JSON.parse(String(init?.body)) as {
        name: string;
        description: string;
      };
      projects = [
        { ...projects[0], ...body, updated_at: "2026-08-04T11:00:00Z" },
      ];
      return json({ data: projects[0], error: null });
    }
    if (url.endsWith("/projects/1") && method === "GET")
      return json({ data: projects[0], error: null });
    if (url.endsWith("/projects/1/videos") && method === "GET")
      return json({ data: [], error: null });
    if (url.endsWith("/projects/1") && method === "DELETE") {
      projects = [];
      return new Response(null, { status: 204 });
    }
    throw new Error(`Unexpected request: ${method} ${url}`);
  });
  window.history.pushState({}, "", "/projects");
  render(<App />);

  expect(await screen.findByText("No projects yet")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "New project" }));
  await user.type(screen.getByLabelText("Project name"), "Road Dataset");
  await user.type(screen.getByLabelText("Description"), "Dashcam review");
  await user.click(screen.getByRole("button", { name: "Create project" }));
  expect(
    await screen.findByRole("heading", { name: "Road Dataset" }),
  ).toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: "Edit" }));
  const name = screen.getByLabelText("Project name");
  await user.clear(name);
  await user.type(name, "Road Scenes");
  await user.click(screen.getByRole("button", { name: "Save changes" }));
  expect(
    await screen.findByRole("heading", { name: "Road Scenes" }),
  ).toBeInTheDocument();

  await user.click(screen.getByRole("link", { name: "Road Scenes" }));
  expect(await screen.findByText("No videos imported")).toBeInTheDocument();
  await user.click(screen.getByRole("link", { name: /All projects/ }));
  await user.click(await screen.findByRole("button", { name: "Delete" }));
  expect(window.confirm).toHaveBeenCalledWith(
    "Delete “Road Scenes”? Project files will remain on disk.",
  );
  await waitFor(() =>
    expect(screen.getByText("No projects yet")).toBeInTheDocument(),
  );
});

test("shows a clear duplicate-name error", async () => {
  const user = userEvent.setup();
  vi.spyOn(globalThis, "fetch").mockImplementation(async (_input, init) => {
    if ((init?.method ?? "GET") === "GET")
      return json({ data: [], error: null });
    return json(
      {
        data: null,
        error: {
          code: "PROJECT_NAME_EXISTS",
          message: "A project with this name already exists.",
        },
      },
      409,
    );
  });
  window.history.pushState({}, "", "/projects");
  render(<App />);

  await user.click(await screen.findByRole("button", { name: "New project" }));
  await user.type(screen.getByLabelText("Project name"), "Duplicate");
  await user.click(screen.getByRole("button", { name: "Create project" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "A project with this name already exists.",
  );
});
