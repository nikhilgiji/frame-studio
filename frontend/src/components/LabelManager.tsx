import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";

import {
  createLabel,
  deleteLabel,
  listLabels,
  updateLabel,
} from "../services/review";

export function LabelManager({ projectId }: { projectId: number }) {
  const client = useQueryClient();
  const labels = useQuery({
    queryKey: ["labels", projectId],
    queryFn: ({ signal }) => listLabels(projectId, signal),
  });
  const [name, setName] = useState("");
  const [shortcut, setShortcut] = useState("");
  const [color, setColor] = useState("#69e2bc");
  const [error, setError] = useState("");
  const refresh = () =>
    client.invalidateQueries({ queryKey: ["labels", projectId] });
  async function add(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await createLabel(projectId, { name, shortcut: shortcut || null, color });
      setName("");
      setShortcut("");
      await refresh();
    } catch (reason) {
      setError((reason as Error).message);
    }
  }
  async function edit(
    id: number,
    current: string,
    currentShortcut: string | null,
  ) {
    const next = window.prompt("Label name", current);
    if (!next) return;
    const key = window.prompt(
      "Keyboard shortcut (blank for none)",
      currentShortcut ?? "",
    );
    try {
      await updateLabel(id, { name: next, shortcut: key || null });
      await refresh();
    } catch (reason) {
      setError((reason as Error).message);
    }
  }
  return (
    <section className="label-manager">
      <h3>Labels</h3>
      <form onSubmit={(e) => void add(e)}>
        <input
          aria-label="Label name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          placeholder="Vehicle"
        />
        <input
          aria-label="Label shortcut"
          value={shortcut}
          onChange={(e) => setShortcut(e.target.value)}
          maxLength={2}
          placeholder="V"
        />
        <input
          aria-label="Label color"
          type="color"
          value={color}
          onChange={(e) => setColor(e.target.value)}
        />
        <button>Add label</button>
      </form>
      {error && (
        <div role="alert" className="inline-error">
          {error}
        </div>
      )}
      <div>
        {labels.data?.map((label, index) => (
          <span key={label.id} style={{ borderColor: label.color }}>
            <b>{label.name}</b>
            {label.shortcut && <kbd>{label.shortcut}</kbd>}
            <button
              onClick={() => void edit(label.id, label.name, label.shortcut)}
            >
              Edit
            </button>
            <button
              disabled={!index}
              onClick={() =>
                void updateLabel(label.id, { position: index - 1 }).then(
                  refresh,
                )
              }
            >
              ↑
            </button>
            <button
              disabled={index === (labels.data?.length ?? 0) - 1}
              onClick={() =>
                void updateLabel(label.id, { position: index + 1 }).then(
                  refresh,
                )
              }
            >
              ↓
            </button>
            <button
              onClick={() => {
                if (window.confirm(`Delete label “${label.name}”?`))
                  void deleteLabel(label.id).then(refresh);
              }}
            >
              Delete
            </button>
          </span>
        ))}
      </div>
    </section>
  );
}
