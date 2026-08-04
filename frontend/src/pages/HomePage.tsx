import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
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
  const [onboarding, setOnboarding] = useState(
    () => localStorage.getItem("vision-curator:onboarding-complete") !== "true",
  );
  let recent: { id: number; name: string }[] = [];
  try {
    recent = JSON.parse(
      localStorage.getItem("vision-curator:recent-projects") ?? "[]",
    );
  } catch {
    recent = [];
  }

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
        <h3>Phase 2 workspace</h3>
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
        {recent.length > 0 && (
          <div className="recent-projects">
            <h4>Recent projects</h4>
            {recent.map((project) => (
              <Link
                key={project.id}
                className="primary-link"
                to={`/projects/${project.id}`}
              >
                {project.name} →
              </Link>
            ))}
          </div>
        )}
      </section>
      {onboarding && (
        <section
          className="onboarding"
          role="dialog"
          aria-label="Welcome to Vision Curator"
        >
          <p className="eyebrow">First run</p>
          <h3>Welcome to Vision Curator</h3>
          <ol>
            <li>Create a project and import local videos.</li>
            <li>Extract frames with the sampling mode you need.</li>
            <li>Review with the gallery, queues, labels, and shortcuts.</li>
            <li>Export the curated selection and manifest.</li>
          </ol>
          <button
            autoFocus
            onClick={() => {
              localStorage.setItem(
                "vision-curator:onboarding-complete",
                "true",
              );
              setOnboarding(false);
            }}
          >
            Start curating
          </button>
        </section>
      )}
    </main>
  );
}
