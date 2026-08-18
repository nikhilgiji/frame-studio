import { useEffect, type ReactNode } from "react";
import { Link, NavLink } from "react-router-dom";

export function Layout({ children }: { children: ReactNode }) {
  useEffect(() => {
    const apply = () => {
      document.documentElement.dataset.theme =
        localStorage.getItem("vision-curator:theme") ?? "light";
    };
    apply();
    window.addEventListener("vision-curator:theme", apply);
    return () => window.removeEventListener("vision-curator:theme", apply);
  }, []);
  return (
    <div className="app-shell">
      <header className="app-header">
        <Link to="/" className="app-brand">
          <span className="brand-mark">VC</span>
          <span>Vision Curator</span>
        </Link>
        <nav>
          <NavLink exact to="/" activeClassName="active">
            Home
          </NavLink>
          <NavLink to="/projects" activeClassName="active">
            Projects
          </NavLink>
          <NavLink to="/settings" activeClassName="active">
            Settings
          </NavLink>
        </nav>
        <span className="local-badge">Local workspace</span>
      </header>
      {children}
    </div>
  );
}
