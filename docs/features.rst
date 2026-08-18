Features
========

Dashboard
---------

The project Overview shows the next workflow action, review goal, aggregate
counts, label distribution, frames per video, review status, daily progress,
background job history, and file integrity. Statistics can be filtered by video
and date. Dense sections collapse when they are not needed.

Video and frame processing
--------------------------

* Batch import with supported-file validation and per-file error reporting.
* Metadata probing for dimensions, frame rate, duration, codec, and frame count.
* Asynchronous extraction with progress, cancellation, retry, and restart
  recovery.
* JPEG/PNG output and optional aspect-preserving resize constraints.
* Cached thumbnails that can be safely regenerated.

Review workspace
----------------

* Paginated API responses capped at 200 frames.
* Virtualized, container-responsive thumbnail rows.
* Full-resolution viewer with fit, original-size, zoom, and pan controls.
* Review, favorite, reject, label, selection, and all-filtered batch actions.
* Video timeline with extraction markers and timestamp/frame-number jumps.
* Persistent filters, page, thumbnail size, last frame, and review queues.
* Multi-step undo/redo for review and label changes.

Dataset export
--------------

Exports may contain copied frame images, a manifest, or both. Selection can be
explicit or filter-based. Paths are constrained beneath the configured export
root, and original videos and extracted frames are never modified.

Reliability and privacy
-----------------------

Frame Studio runs locally and does not upload source media. SQLite stores
metadata and review state. Integrity checks report missing or unsafe videos,
frames, and thumbnails, while repairs are limited to regenerating valid cached
thumbnails. Destructive project and video actions require confirmation.

Accessibility and responsive design
-----------------------------------

The interface provides visible keyboard focus, semantic controls and dialogs,
reduced-motion support, light and dark themes, configurable shortcuts, and
responsive layouts tested at widths from 320 to 1440 pixels.
