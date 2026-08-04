import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { getHealth } from "../services/api";
import { useAppStore } from "../store/appStore";

export function HomePage() {
  const { data, error, isLoading, refetch } = useQuery({
    queryKey: ["health"],
    queryFn: ({ signal }) => getHealth(signal),
  });
  const sidebarOpen = useAppStore((state) => state.sidebarOpen);
  const toggleSidebar = useAppStore((state) => state.toggleSidebar);
  const lastProject = localStorage.getItem("vision-curator:last-project");

  return (
    <main>
      <section className="hero">
        <p className="eyebrow">Workspace status</p>
        <h2>Your computer vision review desk.</h2>
        <p className="lede">
          Import, inspect, label, and export video frames without sending source
          data off your machine.
        </p>
        {isLoading && <LoadingState label="Connecting to local API" />}
        {error && (
          <ErrorState message={error.message} onRetry={() => void refetch()} />
        )}
        {data && (
          <div className="status">
            <span />
            Backend connected
          </div>
        )}
      </section>
      <section className="foundation">
        <h3>Phase 1 workspace ready</h3>
        <p>
          Create projects, extract frames, review with shortcuts, and export
          curated datasets.
        </p>
        <button onClick={toggleSidebar}>
          UI state: {sidebarOpen ? "expanded" : "compact"}
        </button>
        <Link className="primary-link" to="/projects">
          Open projects →
        </Link>
        {lastProject && (
          <Link className="primary-link" to={`/projects/${lastProject}`}>
            Resume last project →
          </Link>
        )}
      </section>
    </main>
  );
}
