import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { App } from "../src/App";

const project = {
  id: 1,
  name: "Road",
  description: "",
  root_path: "/storage/road",
  created_at: "2026-08-04T10:00:00Z",
  updated_at: "2026-08-04T10:00:00Z",
};
const video = {
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
};
function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

test("configures extraction and displays completed progress", async () => {
  const user = userEvent.setup();
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
    const url = String(input);
    const method = init?.method ?? "GET";
    if (url.endsWith("/projects/1") && method === "GET")
      return json({ data: project });
    if (url.endsWith("/projects/1/videos")) return json({ data: [video] });
    if (url.endsWith("/videos/4/extraction-jobs") && method === "POST")
      return json(
        {
          data: {
            id: 9,
            project_id: 1,
            video_id: 4,
            status: "pending",
            progress: 0,
            processed_frames: 0,
            total_frames: 25,
          },
        },
        202,
      );
    if (url.endsWith("/extraction-jobs/9"))
      return json({
        data: {
          id: 9,
          project_id: 1,
          video_id: 4,
          status: "completed",
          progress: 100,
          processed_frames: 25,
          total_frames: 25,
        },
      });
    throw new Error(`Unexpected ${method} ${url}`);
  });
  window.history.pushState({}, "", "/projects/1");
  render(<App />);
  await user.click(await screen.findByRole("button", { name: /Videos/ }));
  await user.click(
    await screen.findByRole("button", { name: "Extract frames" }),
  );
  await user.selectOptions(
    screen.getByLabelText("Sampling"),
    "frames_per_second",
  );
  await user.clear(screen.getByLabelText("Value"));
  await user.type(screen.getByLabelText("Value"), "2");
  await user.click(screen.getByRole("button", { name: "Start extraction" }));
  expect(await screen.findByText("completed")).toBeInTheDocument();
  expect(screen.getByText("25 / 25 frames")).toBeInTheDocument();
});
