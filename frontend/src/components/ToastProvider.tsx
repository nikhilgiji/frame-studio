import { useCallback, useMemo, useState, type ReactNode } from "react";

import { ToastContext, type ToastKind } from "./toastContext";

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<
    { id: number; message: string; kind: ToastKind }[]
  >([]);
  const notify = useCallback((message: string, kind: ToastKind = "success") => {
    const id = Date.now() + Math.random();
    setToasts((current) => [...current, { id, message, kind }]);
    window.setTimeout(
      () => setToasts((current) => current.filter((toast) => toast.id !== id)),
      4000,
    );
  }, []);
  const value = useMemo(() => ({ notify }), [notify]);
  return (
    <ToastContext.Provider value={value}>
      {children}
      <div
        className="toast-region"
        aria-live="polite"
        aria-label="Notifications"
      >
        {toasts.map((toast) => (
          <button
            key={toast.id}
            className={`toast ${toast.kind}`}
            onClick={() =>
              setToasts((items) => items.filter((item) => item.id !== toast.id))
            }
          >
            {toast.message}
          </button>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
