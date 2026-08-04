import { render, screen } from "@testing-library/react";

import { App } from "../src/App";

test("shows API connectivity when the health endpoint responds", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ status: "ok" }), { status: 200 }),
  );

  render(<App />);

  expect(screen.getByRole("status")).toHaveTextContent(
    "Connecting to local API",
  );
  expect(await screen.findByText("Backend connected")).toBeInTheDocument();
  expect(fetch).toHaveBeenCalledWith(
    "http://localhost:8000/api/v1/health",
    expect.objectContaining({ signal: expect.any(AbortSignal) }),
  );
});

test("shows a recoverable error when the backend is unavailable", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(null, { status: 503 }),
  );

  render(<App />);

  expect(await screen.findByRole("alert")).toHaveTextContent(
    "The local API is unavailable.",
  );
  expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
});
