import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

vi.mock("@tanstack/react-virtual", () => ({
  useVirtualizer: ({ count }: { count: number }) => ({
    getTotalSize: () => count * 240,
    getVirtualItems: () =>
      Array.from({ length: count }, (_, index) => ({
        key: index,
        index,
        start: index * 240,
      })),
  }),
}));

import { App } from "../src/App";

test("virtualizes gallery cards and navigates the full-resolution viewer", async () => {
  const user = userEvent.setup();
  const items = [0, 10, 20].map((number, index) => ({
    id: index + 1,
    project_id: 1,
    video_id: 1,
    frame_number: number,
    timestamp_seconds: number / 10,
    width: 640,
    height: 480,
    review_status: "unreviewed",
    favorite: false,
    rejected: false,
    reviewed_at: null,
    created_at: "2026-08-04T10:00:00Z",
    labels: [],
  }));
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
    const url = String(input);
    if (url.includes("/frames?"))
      return new Response(
        JSON.stringify({
          items,
          page: 1,
          page_size: 200,
          total: 100000,
          has_next: true,
        }),
        { status: 200 },
      );
    if (url.endsWith("/labels"))
      return new Response(JSON.stringify({ data: [] }), { status: 200 });
    if (url.endsWith("/review-session") && (init?.method ?? "GET") === "GET")
      return new Response(
        JSON.stringify({
          data: {
            id: 1,
            project_id: 1,
            video_id: null,
            last_frame_id: null,
            active_filters: {},
            gallery_position: 0,
            thumbnail_size: 180,
            created_at: "",
            updated_at: "",
          },
        }),
        { status: 200 },
      );
    if (url.endsWith("/review-session"))
      return new Response(JSON.stringify({ data: {} }), { status: 200 });
    throw new Error(`Unexpected ${url}`);
  });
  window.history.pushState({}, "", "/projects/1/gallery");
  render(<App />);
  expect(await screen.findByText("100,000 frames")).toBeInTheDocument();
  expect(screen.getAllByRole("img")).toHaveLength(3);
  const first = await screen.findByRole("img", { name: "Frame 0" });
  await user.dblClick(first.closest("button")!);
  expect(screen.getByRole("dialog", { name: "Frame 0" })).toBeInTheDocument();
  await user.keyboard("{ArrowRight}");
  expect(screen.getByRole("dialog", { name: "Frame 10" })).toBeInTheDocument();
  await user.keyboard("{Escape}");
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
});
