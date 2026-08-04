import { createContext, useContext } from "react";

export type ToastKind = "success" | "error" | "info";
export const ToastContext = createContext<{
  notify: (message: string, kind?: ToastKind) => void;
}>({ notify: () => undefined });
export const useToast = () => useContext(ToastContext);
