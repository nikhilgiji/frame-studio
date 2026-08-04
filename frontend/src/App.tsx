import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { BrowserRouter, Redirect, Route, Switch } from "react-router-dom";

import { AppErrorBoundary } from "./components/AppErrorBoundary";
import { Layout } from "./components/Layout";
import { ToastProvider } from "./components/ToastProvider";
import { HomePage } from "./pages/HomePage";
import { GalleryPage } from "./pages/GalleryPage";
import { ProjectDetailPage } from "./pages/ProjectDetailPage";
import { ProjectsPage } from "./pages/ProjectsPage";
import { SettingsPage } from "./pages/SettingsPage";

export function App() {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { retry: false, staleTime: 10_000 },
        },
      }),
  );

  return (
    <AppErrorBoundary>
      <ToastProvider>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <Layout>
              <Switch>
                <Route exact path="/" component={HomePage} />
                <Route exact path="/projects" component={ProjectsPage} />
                <Route exact path="/settings" component={SettingsPage} />
                <Route
                  exact
                  path="/projects/:projectId"
                  component={ProjectDetailPage}
                />
                <Route
                  exact
                  path="/projects/:projectId/gallery"
                  component={GalleryPage}
                />
                <Redirect to="/" />
              </Switch>
            </Layout>
          </BrowserRouter>
        </QueryClientProvider>
      </ToastProvider>
    </AppErrorBoundary>
  );
}
