import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { App } from "../src/App";
import type { Video } from "../src/types/video";

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

test("imports multiple videos, displays metadata, and confirms deletion", async () => {
  const user = userEvent.setup();
  let videos: Video[] = [];
  const project = {
    id: 1,
    name: "Road",
    description: "",
    root_path: "/storage/road",
    created_at: "2026-08-04T10:00:00Z",
    updated_at: "2026-08-04T10:00:00Z",
  };
  vi.spyOn(window, "confirm").mockReturnValue(true);
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
    const url = String(input);
    const method = init?.method ?? "GET";
    if (url.endsWith("/projects/1") && method === "GET")
      return json({ data: project, error: null });
    if (url.endsWith("/projects/1/videos") && method === "GET")
      return json({ data: videos, error: null });
    if (url.endsWith("/projects/1/videos/import") && method === "POST") {
      expect(init?.body).toBeInstanceOf(FormData);
      videos = [
        {
          id: 4,
          project_id: 1,
          filename: "drive.mp4",
          source_path: "drive.mp4",
          stored_path: "/storage/road/videos/a.mp4",
          file_size: 1048576,
          fps: 25,
          duration_seconds: 10,
          frame_count: 250,
          width: 1920,
          height: 1080,
          codec: "avc1",
          status: "ready",
          created_at: "2026-08-04T10:00:00Z",
        },
      ];
      return json({
        data: {
          imported: videos,
          skipped: [
            {
              filename: "notes.txt",
              code: "UNSUPPORTED_FORMAT",
              message: "Unsupported video format: .txt.",
            },
          ],
          errors: [],
        },
        error: null,
      });
    }
    if (url.endsWith("/videos/4") && method === "DELETE") {
      videos = [];
      return new Response(null, { status: 204 });
    }
    throw new Error(`Unexpected request: ${method} ${url}`);
  });
  window.history.pushState({}, "", "/projects/1");
  render(<App />);
  await user.click(await screen.findByRole("button", { name: /Videos/ }));

  const files = [
    new File(["video"], "drive.mp4", { type: "video/mp4" }),
    new File(["video-2"], "second.mov", { type: "video/quicktime" }),
  ];
  await user.upload(await screen.findByLabelText("Choose files"), files);
  await user.click(screen.getByRole("button", { name: "Import 2 videos" }));
  expect(await screen.findByText("1 imported")).toBeInTheDocument();
  expect(screen.getByText(/Unsupported video format/)).toBeInTheDocument();
  expect(
    await screen.findByRole("heading", { name: "drive.mp4" }),
  ).toBeInTheDocument();
  expect(screen.getByText(/1920×1080/)).toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: "Delete" }));
  expect(window.confirm).toHaveBeenCalledWith(
    "Delete the imported copy of “drive.mp4”?",
  );
  await waitFor(() =>
    expect(screen.getByText("No videos imported")).toBeInTheDocument(),
  );
});
