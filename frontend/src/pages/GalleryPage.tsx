import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useVirtualizer } from "@tanstack/react-virtual";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useHistory, useLocation, useParams } from "react-router-dom";

import { ErrorState } from "../components/ErrorState";
import { ExportPanel } from "../components/ExportPanel";
import { FrameViewer } from "../components/FrameViewer";
import { LoadingState } from "../components/LoadingState";
import { listFrames, thumbnailUrl } from "../services/frames";
import { listVideos } from "../services/videos";
import {
  assignLabels,
  bulkLabels,
  bulkReview,
  createLabel,
  getSession,
  listLabels,
  reviewFrame,
  saveSession,
  type ReviewChanges,
} from "../services/review";
import type { Frame } from "../types/frame";

export function GalleryPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = Number(projectId);
  const location = useLocation();
  const history = useHistory();
  const queryClient = useQueryClient();
  const filters = useMemo(
    () => new URLSearchParams(location.search),
    [location.search],
  );
  const [page, setPage] = useState(Number(filters.get("page") ?? 1));
  const [size, setSize] = useState(180);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [anchor, setAnchor] = useState<number | null>(null);
  const [viewer, setViewer] = useState<number | null>(null);
  const [newLabel, setNewLabel] = useState("");
  const [shortcut, setShortcut] = useState("");
  const [undo, setUndo] = useState<null | (() => Promise<unknown>)>(null);
  const scroll = useRef<HTMLDivElement>(null);
  const restored = useRef(false);
  const resumedFrame = useRef(false);
  const frames = useQuery({
    queryKey: ["frames", id, page, location.search],
    queryFn: ({ signal }) => listFrames(id, page, 200, filters, signal),
  });
  const labels = useQuery({
    queryKey: ["labels", id],
    queryFn: ({ signal }) => listLabels(id, signal),
  });
  const videos = useQuery({
    queryKey: ["videos", id],
    queryFn: ({ signal }) => listVideos(id, signal),
  });
  const session = useQuery({
    queryKey: ["session", id],
    queryFn: ({ signal }) => getSession(id, signal),
  });
  useEffect(() => {
    if (!session.data || restored.current) return;
    restored.current = true;
    setSize(session.data.thumbnail_size);
    setPage(session.data.gallery_position || 1);
    if (!location.search && Object.keys(session.data.active_filters).length) {
      const restoredFilters = new URLSearchParams();
      Object.entries(session.data.active_filters).forEach(([key, value]) =>
        (Array.isArray(value) ? value : [value]).forEach((item) =>
          restoredFilters.append(key, String(item)),
        ),
      );
      history.replace({ search: restoredFilters.toString() });
    }
  }, [history, location.search, session.data]);
  useEffect(() => {
    if (restored.current)
      void saveSession(id, {
        gallery_position: page,
        thumbnail_size: size,
        active_filters: Object.fromEntries(
          [...new Set(filters.keys())].map((key) => {
            const values = filters.getAll(key);
            return [key, values.length > 1 ? values : values[0]];
          }),
        ),
      });
  }, [filters, id, page, size]);
  const items = useMemo(() => frames.data?.items ?? [], [frames.data]);
  useEffect(() => {
    if (!resumedFrame.current && session.data?.last_frame_id) {
      const index = items.findIndex(
        (frame) => frame.id === session.data?.last_frame_id,
      );
      if (index >= 0) {
        resumedFrame.current = true;
        setViewer(index);
      }
    }
  }, [items, session.data?.last_frame_id]);
  const columns = Math.max(1, Math.floor(1000 / (size + 14)));
  const rows = Math.ceil(items.length / columns);
  const virtual = useVirtualizer({
    count: rows,
    getScrollElement: () => scroll.current,
    estimateSize: () => size + 54,
    overscan: 2,
    initialRect: { width: 1000, height: 600 },
  });
  const refresh = useCallback(
    () => queryClient.invalidateQueries({ queryKey: ["frames", id] }),
    [id, queryClient],
  );
  const actReview = useCallback(
    async (frame: Frame, changes: ReviewChanges) => {
      const previous = {
        review_status: frame.review_status,
        favorite: frame.favorite,
        rejected: frame.rejected,
      };
      await reviewFrame(frame.id, changes);
      setUndo(() => async () => reviewFrame(frame.id, previous));
      await refresh();
    },
    [refresh],
  );
  function choose(index: number, event: React.MouseEvent) {
    const frame = items[index];
    const next = new Set(event.metaKey || event.ctrlKey ? selected : []);
    if (event.shiftKey && anchor !== null)
      for (let i = Math.min(anchor, index); i <= Math.max(anchor, index); i++)
        next.add(items[i].id);
    else if (next.has(frame.id)) next.delete(frame.id);
    else next.add(frame.id);
    setSelected(next);
    setAnchor(index);
  }
  async function applyLabel(labelId: number) {
    const ids = selected.size
      ? [...selected]
      : viewer !== null
        ? [items[viewer].id]
        : [];
    if (!ids.length) return;
    if (ids.length === 1) await assignLabels(ids[0], [labelId]);
    else await bulkLabels(ids, [labelId], "assign");
    setUndo(() => async () => bulkLabels(ids, [labelId], "remove"));
    await refresh();
  }
  useEffect(() => {
    function key(event: KeyboardEvent) {
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement ||
        event.target instanceof HTMLSelectElement
      )
        return;
      const label = labels.data?.find(
        (item) => item.shortcut?.toLowerCase() === event.key.toLowerCase(),
      );
      if (label) void applyLabel(label.id);
    }
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  });
  function updateFilter(name: string, value: string) {
    const next = new URLSearchParams(filters);
    if (value) next.set(name, value);
    else next.delete(name);
    next.delete("page");
    setPage(1);
    history.replace({ search: next.toString() });
  }
  function toggleLabelFilter(labelId: number, checked: boolean) {
    const next = new URLSearchParams(filters);
    const values = next
      .getAll("label_ids")
      .filter((value) => value !== String(labelId));
    next.delete("label_ids");
    values.forEach((value) => next.append("label_ids", value));
    if (checked) next.append("label_ids", String(labelId));
    setPage(1);
    history.replace({ search: next.toString() });
  }
  if (frames.isLoading)
    return (
      <main>
        <LoadingState label="Loading frames" />
      </main>
    );
  if (frames.error)
    return (
      <main>
        <ErrorState message={frames.error.message} />
      </main>
    );
  return (
    <main className="gallery-page">
      <div className="gallery-bar">
        <Link to={`/projects/${id}`}>← Project</Link>
        <strong>{frames.data?.total.toLocaleString()} frames</strong>
        <select
          aria-label="Video filter"
          value={filters.get("video_id") ?? ""}
          onChange={(e) => updateFilter("video_id", e.target.value)}
        >
          <option value="">All videos</option>
          {videos.data?.map((video) => (
            <option key={video.id} value={video.id}>
              {video.filename}
            </option>
          ))}
        </select>
        <input
          aria-label="Search frames"
          placeholder="Search filename"
          value={filters.get("search") ?? ""}
          onChange={(e) => updateFilter("search", e.target.value)}
        />
        <select
          aria-label="Review filter"
          value={filters.get("review_status") ?? ""}
          onChange={(e) => updateFilter("review_status", e.target.value)}
        >
          <option value="">All review states</option>
          <option value="unreviewed">Unreviewed</option>
          <option value="reviewed">Reviewed</option>
        </select>
        <label>
          <input
            type="checkbox"
            checked={filters.get("favorite") === "true"}
            onChange={(e) =>
              updateFilter("favorite", e.target.checked ? "true" : "")
            }
          />{" "}
          Favorites
        </label>
        <label>
          <input
            type="checkbox"
            checked={filters.get("rejected") === "true"}
            onChange={(e) =>
              updateFilter("rejected", e.target.checked ? "true" : "")
            }
          />{" "}
          Rejected
        </label>
        <label>
          <input
            type="checkbox"
            checked={filters.get("unlabeled") === "true"}
            onChange={(e) =>
              updateFilter("unlabeled", e.target.checked ? "true" : "")
            }
          />{" "}
          Unlabeled
        </label>
        <input
          aria-label="Timestamp from"
          type="number"
          min="0"
          step="0.01"
          placeholder="From seconds"
          value={filters.get("timestamp_min") ?? ""}
          onChange={(e) => updateFilter("timestamp_min", e.target.value)}
        />
        <input
          aria-label="Timestamp to"
          type="number"
          min="0"
          step="0.01"
          placeholder="To seconds"
          value={filters.get("timestamp_max") ?? ""}
          onChange={(e) => updateFilter("timestamp_max", e.target.value)}
        />
        <button
          onClick={() => {
            history.replace({ search: "" });
            setPage(1);
          }}
        >
          Clear filters
        </button>
        <label>
          Size{" "}
          <input
            type="range"
            min="110"
            max="280"
            value={size}
            onChange={(e) => setSize(Number(e.target.value))}
          />
        </label>
        <span>{selected.size} selected</span>
      </div>
      <aside className="label-bar">
        <ExportPanel projectId={id} selectedIds={[...selected]} />
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void createLabel(id, {
              name: newLabel,
              shortcut: shortcut || null,
              color: "#69e2bc",
            }).then(() => {
              setNewLabel("");
              setShortcut("");
              return queryClient.invalidateQueries({
                queryKey: ["labels", id],
              });
            });
          }}
        >
          <input
            aria-label="New label"
            value={newLabel}
            onChange={(e) => setNewLabel(e.target.value)}
            placeholder="New label"
            required
          />
          <input
            aria-label="Shortcut"
            value={shortcut}
            onChange={(e) => setShortcut(e.target.value)}
            placeholder="Key"
            maxLength={2}
          />
          <button>Add</button>
        </form>
        {labels.data?.map((label) => (
          <span key={label.id} className="label-action">
            <label title="Filter by label">
              <input
                type="checkbox"
                checked={filters.getAll("label_ids").includes(String(label.id))}
                onChange={(e) => toggleLabelFilter(label.id, e.target.checked)}
              />
              {label.name}
            </label>
            <button
              style={{ borderColor: label.color }}
              onClick={() => void applyLabel(label.id)}
            >
              Assign{label.shortcut && <kbd>{label.shortcut}</kbd>}
            </button>
            <button
              disabled={!selected.size}
              onClick={() => {
                const ids = [...selected];
                void bulkLabels(ids, [label.id], "remove").then(refresh);
                setUndo(
                  () => async () => bulkLabels(ids, [label.id], "assign"),
                );
              }}
            >
              Remove
            </button>
          </span>
        ))}
        <button
          disabled={!selected.size}
          onClick={() => {
            const ids = [...selected];
            void bulkReview(ids, { review_status: "reviewed" }).then(refresh);
            setUndo(
              () => async () =>
                bulkReview(ids, { review_status: "unreviewed" }),
            );
          }}
        >
          Mark reviewed
        </button>
        <button
          disabled={!undo}
          onClick={() => {
            void undo?.().then(refresh);
            setUndo(null);
          }}
        >
          Undo
        </button>
      </aside>
      {!items.length ? (
        <div className="empty-state">
          <h3>No matching frames</h3>
        </div>
      ) : (
        <div className="gallery-scroll" ref={scroll}>
          <div style={{ height: virtual.getTotalSize(), position: "relative" }}>
            {virtual.getVirtualItems().map((row) => (
              <div
                className="frame-row"
                key={row.key}
                style={{
                  position: "absolute",
                  transform: `translateY(${row.start}px)`,
                  gridTemplateColumns: `repeat(${columns}, ${size}px)`,
                }}
              >
                {items
                  .slice(row.index * columns, (row.index + 1) * columns)
                  .map((frame, offset) => {
                    const index = row.index * columns + offset;
                    return (
                      <button
                        className={`frame-card ${selected.has(frame.id) ? "selected" : ""}`}
                        key={frame.id}
                        onClick={(e) => choose(index, e)}
                        onDoubleClick={() => {
                          setViewer(index);
                          void saveSession(id, { last_frame_id: frame.id });
                        }}
                      >
                        <img
                          loading="lazy"
                          src={thumbnailUrl(frame.id)}
                          alt={`Frame ${frame.frame_number}`}
                          style={{ height: size * 0.65 }}
                        />
                        <span>
                          #{frame.frame_number} ·{" "}
                          {frame.timestamp_seconds.toFixed(2)}s
                        </span>
                        <small>
                          {frame.review_status}
                          {frame.favorite ? " ★" : ""}
                          {frame.rejected ? " ✕" : ""}
                        </small>
                        <i>
                          {frame.labels.map((label) => label.name).join(", ")}
                        </i>
                      </button>
                    );
                  })}
              </div>
            ))}
          </div>
        </div>
      )}
      <div className="pagination">
        <button disabled={page === 1} onClick={() => setPage(page - 1)}>
          Previous page
        </button>
        <span>Page {page}</span>
        <button
          disabled={!frames.data?.has_next}
          onClick={() => setPage(page + 1)}
        >
          Next page
        </button>
      </div>
      {viewer !== null && (
        <FrameViewer
          frames={items}
          index={viewer}
          onIndex={setViewer}
          onClose={() => setViewer(null)}
          onReview={(frame, changes) => void actReview(frame, changes)}
        />
      )}
    </main>
  );
}
