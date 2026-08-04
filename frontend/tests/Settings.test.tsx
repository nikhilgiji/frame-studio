import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { App } from "../src/App";

test("persists customized shortcuts and rejects conflicts", async () => {
  const user = userEvent.setup();
  window.history.pushState({}, "", "/settings");
  const view = render(<App />);
  const previous = screen.getByLabelText("Viewer: previous");
  fireEvent.keyDown(previous, { key: "j" });
  await user.click(screen.getByRole("button", { name: "Save shortcuts" }));
  expect(screen.getByRole("status")).toHaveTextContent("Settings saved");
  expect(localStorage.getItem("vision-curator:shortcuts")).toContain(
    '"previous":"j"',
  );

  view.unmount();
  render(<App />);
  expect(screen.getByLabelText("Viewer: previous")).toHaveValue("j");
  fireEvent.keyDown(screen.getByLabelText("Viewer: next"), { key: "j" });
  expect(screen.getByRole("alert")).toHaveTextContent("both use j");
  expect(screen.getByRole("button", { name: "Save shortcuts" })).toBeDisabled();
});
