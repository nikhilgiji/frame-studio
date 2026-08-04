import { useEffect, type ReactNode } from "react";
import { Link } from "react-router-dom";

export function Layout({ children }: { children: ReactNode }) {
  useEffect(() => {
    const apply = () => {
      document.documentElement.dataset.theme =
        localStorage.getItem("vision-curator:theme") ?? "dark";
    };
    apply();
    window.addEventListener("vision-curator:theme", apply);
    return () => window.removeEventListener("vision-curator:theme", apply);
  }, []);
  return (
    <div className="app-shell">
      <header>
        <Link to="/" className="brand-mark">
          VC
        </Link>
        <div>
          <h1>Vision Curator</h1>
          <p>Local video dataset workspace</p>
        </div>
        <nav>
          <Link to="/projects">Projects</Link>
          {" · "}
          <Link to="/settings">Settings</Link>
        </nav>
      </header>
      {children}
    </div>
  );
}
