import { useEffect, useState } from "react";

export const defaultShortcuts = {
  previous: "ArrowLeft",
  next: "ArrowRight",
  previousAlt: "a",
  nextAlt: "d",
  closeViewer: "Escape",
  favorite: "f",
  reject: "r",
  reviewed: "Space",
  selectVisible: "s",
  clearSelection: "c",
  openSelected: "Enter",
  undo: "z",
  redo: "y",
} as const;

export type ShortcutAction = keyof typeof defaultShortcuts;
export type ShortcutMap = Record<ShortcutAction, string>;
const storageKey = "vision-curator:shortcuts";

export function readShortcuts(): ShortcutMap {
  try {
    return {
      ...defaultShortcuts,
      ...JSON.parse(localStorage.getItem(storageKey) ?? "{}"),
    };
  } catch {
    return { ...defaultShortcuts };
  }
}

export function normalizedKey(key: string) {
  return key === " " ? "Space" : key.length === 1 ? key.toLowerCase() : key;
}

export function shortcutConflicts(map: ShortcutMap) {
  const entries = Object.entries(map) as [ShortcutAction, string][];
  const seen = new Map<string, ShortcutAction>();
  const conflicts: string[] = [];
  for (const [action, raw] of entries) {
    const key = normalizedKey(raw);
    if (!key) continue;
    const previous = seen.get(key);
    if (previous) conflicts.push(`${previous} and ${action} both use ${key}`);
    else seen.set(key, action);
  }
  return conflicts;
}

export function saveShortcuts(map: ShortcutMap) {
  const conflicts = shortcutConflicts(map);
  if (conflicts.length) throw new Error(conflicts[0]);
  localStorage.setItem(storageKey, JSON.stringify(map));
  window.dispatchEvent(new Event("vision-curator:shortcuts"));
}

export function useShortcuts() {
  const [shortcuts, setShortcuts] = useState(readShortcuts);
  useEffect(() => {
    const refresh = () => setShortcuts(readShortcuts());
    window.addEventListener("vision-curator:shortcuts", refresh);
    window.addEventListener("storage", refresh);
    return () => {
      window.removeEventListener("vision-curator:shortcuts", refresh);
      window.removeEventListener("storage", refresh);
    };
  }, []);
  return shortcuts;
}
