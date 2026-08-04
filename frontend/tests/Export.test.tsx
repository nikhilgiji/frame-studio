import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ExportPanel } from "../src/components/ExportPanel";

test("starts a selected-frame export and displays its destination", async () => {
  const user = userEvent.setup();
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
    const url = String(input);
    if (url.endsWith("/projects/1/export-jobs") && init?.method === "POST")
      return new Response(
        JSON.stringify({ data: { id: 8, status: "pending", progress: 0 } }),
        { status: 202 },
      );
    if (url.endsWith("/export-jobs/8"))
      return new Response(
        JSON.stringify({
          data: {
            id: 8,
            status: "completed",
            progress: 100,
            destination_path: "/storage/exports/dataset",
          },
        }),
        { status: 200 },
      );
    throw new Error(`Unexpected request ${url}`);
  });
  render(
    <QueryClientProvider client={new QueryClient()}>
      <ExportPanel projectId={1} selectedIds={[2, 3]} />
    </QueryClientProvider>,
  );
  await user.click(screen.getByRole("button", { name: "Export dataset" }));
  expect(screen.getByLabelText("Mode")).toHaveValue("selected");
  await user.click(screen.getByRole("button", { name: "Start export" }));
  expect(await screen.findByText("completed")).toBeInTheDocument();
  expect(screen.getByText(/storage\/exports\/dataset/)).toBeInTheDocument();
});
