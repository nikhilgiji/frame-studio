import { useState } from "react";

import {
  defaultShortcuts,
  saveShortcuts,
  shortcutConflicts,
  type ShortcutAction,
  type ShortcutMap,
} from "../services/shortcuts";

const labels: Record<ShortcutAction, string> = {
  previous: "Viewer: previous",
  next: "Viewer: next",
  previousAlt: "Viewer: previous alternate",
  nextAlt: "Viewer: next alternate",
  closeViewer: "Viewer: close",
  favorite: "Toggle favorite",
  reject: "Toggle rejected",
  reviewed: "Toggle reviewed",
  selectVisible: "Gallery: select visible",
  clearSelection: "Gallery: clear selection",
  openSelected: "Gallery: open selected",
  undo: "Undo",
  redo: "Redo",
};

export function SettingsPage() {
  const [darkMode, setDarkMode] = useState(
    () => localStorage.getItem("vision-curator:theme") !== "light",
  );
  const [values, setValues] = useState<ShortcutMap>(() => {
    try {
      return {
        ...defaultShortcuts,
        ...JSON.parse(localStorage.getItem("vision-curator:shortcuts") ?? "{}"),
      };
    } catch {
      return { ...defaultShortcuts };
    }
  });
  const [message, setMessage] = useState("");
  const conflicts = shortcutConflicts(values);
  return (
    <main className="settings-page">
      <section className="form-card">
        <p className="eyebrow">Local preferences</p>
        <h2>Settings</h2>
        <p>Shortcuts persist in this browser installation.</p>
        <label className="theme-toggle">
          <input
            type="checkbox"
            checked={darkMode}
            onChange={(event) => {
              const dark = event.target.checked;
              setDarkMode(dark);
              localStorage.setItem(
                "vision-curator:theme",
                dark ? "dark" : "light",
              );
              window.dispatchEvent(new Event("vision-curator:theme"));
            }}
          />
          Dark mode
        </label>
        <div className="shortcut-grid">
          {(Object.keys(defaultShortcuts) as ShortcutAction[]).map((action) => (
            <label key={action}>
              {labels[action]}
              <input
                aria-label={labels[action]}
                value={values[action]}
                onKeyDown={(event) => {
                  event.preventDefault();
                  setValues({
                    ...values,
                    [action]: event.key === " " ? "Space" : event.key,
                  });
                }}
                onChange={(event) =>
                  setValues({ ...values, [action]: event.target.value })
                }
              />
            </label>
          ))}
        </div>
        {conflicts.length > 0 && <div role="alert">{conflicts[0]}</div>}
        {message && <p role="status">{message}</p>}
        <div className="form-actions">
          <button
            disabled={conflicts.length > 0}
            onClick={() => {
              try {
                saveShortcuts(values);
                setMessage("Settings saved");
              } catch (error) {
                setMessage((error as Error).message);
              }
            }}
          >
            Save shortcuts
          </button>
          <button
            onClick={() => {
              const defaults = { ...defaultShortcuts };
              setValues(defaults);
              saveShortcuts(defaults);
              setMessage("Defaults restored");
            }}
          >
            Restore defaults
          </button>
        </div>
      </section>
    </main>
  );
}
