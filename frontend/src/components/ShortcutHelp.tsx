import { useShortcuts } from "../services/shortcuts";

export function ShortcutHelp({ onClose }: { onClose: () => void }) {
  const shortcuts = useShortcuts();
  return (
    <section
      className="shortcut-help"
      role="dialog"
      aria-label="Keyboard shortcuts"
    >
      <h3>Keyboard shortcuts</h3>
      <dl>
        {Object.entries(shortcuts).map(([action, key]) => (
          <div key={action}>
            <dt>{action.replace(/([A-Z])/g, " $1")}</dt>
            <dd>
              <kbd>{key}</kbd>
            </dd>
          </div>
        ))}
        <div>
          <dt>Label actions</dt>
          <dd>Configured per label</dd>
        </div>
      </dl>
      <button onClick={onClose}>Close help</button>
    </section>
  );
}
