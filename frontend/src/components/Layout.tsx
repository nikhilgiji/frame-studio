import type { ReactNode } from "react";
import { Link } from "react-router-dom";

export function Layout({ children }: { children: ReactNode }) {
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
        </nav>
      </header>
      {children}
    </div>
  );
}
