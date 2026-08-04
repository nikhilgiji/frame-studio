Vision Curator — Internal Video Dataset Curation Tool

Project Goal

Build a locally hosted web application for Computer Vision engineers to:

* Import videos and video folders
* Extract frames using configurable sampling strategies
* Review tens of thousands of frames efficiently
* Assign labels using mouse or keyboard shortcuts
* Save review progress
* Export curated datasets
* Later add automated frame-quality and similarity features

The application must run locally and be accessible through a browser.

Example:

http://localhost:3000

The backend should run locally at:

http://localhost:8000

The system should be implemented incrementally in three phases.

Do not begin a later phase until the current phase passes its verification checklist.

⸻

Recommended Technology Stack

Backend

* Python 3.11+
* FastAPI
* SQLAlchemy 2
* SQLite
* Alembic
* OpenCV or PyAV
* Pillow
* Uvicorn
* Pydantic
* pytest

Frontend

* React
* Vite
* TypeScript
* React Router
* TanStack Query
* Zustand
* Material UI or Tailwind CSS
* react-window or another virtualization library
* Vitest
* React Testing Library
* Playwright

Packaging and Development

* Docker Compose optional
* .env configuration
* Ruff
* Black
* mypy
* ESLint
* Prettier

⸻

High-Level Architecture

Browser
   |
   v
React Frontend
   |
   v
FastAPI REST API
   |
   +-- Project Service
   +-- Video Service
   +-- Frame Extraction Service
   +-- Thumbnail Service
   +-- Review and Label Service
   +-- Export Service
   +-- Analysis Service
   |
   +-- SQLite Database
   |
   +-- Local File Storage

⸻

Suggested Repository Structure

vision-curator/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── tasks/
│   │   ├── utils/
│   │   └── main.py
│   ├── tests/
│   ├── alembic/
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── store/
│   │   ├── types/
│   │   └── utils/
│   ├── tests/
│   ├── package.json
│   └── vite.config.ts
├── storage/
│   ├── projects/
│   ├── cache/
│   └── exports/
├── scripts/
├── docs/
├── .env.example
├── docker-compose.yml
├── README.md
└── tasks.md

⸻

General Engineering Rules

Apply these rules in every phase.

* Use typed Python and TypeScript.
* Do not hardcode absolute file paths.
* Store application configuration in environment variables.
* Keep database operations inside repository or service layers.
* Keep video-processing logic separate from API routes.
* Return structured API errors.
* Log background operations and failures.
* Never load all full-resolution frames into memory.
* Do not store image binary data in SQLite.
* Store file paths and metadata in SQLite.
* Add database indexes for commonly filtered columns.
* Make background operations cancellable where practical.
* Add unit tests for important backend services.
* Add frontend tests for important user workflows.
* Update the README at the end of each phase.
* Commit or tag the code after each verified phase.

Suggested tags:

phase-1-complete
phase-2-complete
phase-3-complete

⸻

Database Model

Project

id
name
description
root_path
created_at
updated_at

Video

id
project_id
filename
source_path
stored_path
file_size
fps
duration_seconds
frame_count
width
height
codec
status
created_at

ExtractionJob

id
project_id
video_id
mode
mode_value
output_format
jpeg_quality
resize_width
resize_height
status
progress
processed_frames
total_frames
error_message
created_at
started_at
completed_at

Frame

id
project_id
video_id
frame_number
timestamp_seconds
image_path
thumbnail_path
width
height
review_status
favorite
rejected
reviewed_at
created_at

Label

id
project_id
name
shortcut
color
description
created_at

FrameLabel

frame_id
label_id
created_at

ReviewSession

id
project_id
video_id
last_frame_id
active_filters_json
gallery_position
created_at
updated_at

ExportJob

id
project_id
destination_path
export_mode
status
progress
error_message
created_at
completed_at

FrameAnalysis

Implemented in Phase 3.

id
frame_id
blur_score
brightness_score
duplicate_group_id
scene_id
embedding_path
analysis_version
created_at

⸻

API Conventions

Use REST endpoints under:

/api/v1

Use consistent responses:

{
  "data": {},
  "error": null
}

For errors:

{
  "data": null,
  "error": {
    "code": "VIDEO_NOT_FOUND",
    "message": "The requested video does not exist."
  }
}

Paginated endpoints should return:

{
  "items": [],
  "page": 1,
  "page_size": 100,
  "total": 0,
  "has_next": false
}

⸻

Phase 1 — Functional MVP

Phase 1 Objective

Create a usable local application that replaces the team’s current manual workflow.

At the end of Phase 1, a user must be able to:

1. Create a project
2. Import one or more videos
3. Extract frames
4. Browse extracted frames
5. Open a frame in a larger viewer
6. Create labels
7. Assign labels
8. Mark frames as reviewed, rejected, or favorite
9. Export labeled frames
10. Close and reopen the application without losing progress

⸻

Phase 1.1 — Project Setup

Backend Tasks

* Initialize the FastAPI application.
* Configure SQLAlchemy.
* Configure SQLite.
* Add Alembic migrations.
* Add application settings through .env.
* Add structured logging.
* Add CORS configuration.
* Add health endpoints.

Required endpoint:

GET /api/v1/health

Expected response:

{
  "status": "ok"
}

Frontend Tasks

* Initialize React, Vite, and TypeScript.
* Configure React Router.
* Configure TanStack Query.
* Configure Zustand.
* Add the base application layout.
* Add global error handling.
* Add an API client.
* Add loading and error components.

Verification

* Backend starts without errors.
* Frontend starts without errors.
* Frontend can call the health endpoint.
* Database migrations run successfully.
* Restarting the backend does not delete existing data.
* Backend tests and frontend tests run successfully.

⸻

Phase 1.2 — Project Management

Features

* Create a project.
* Edit a project.
* Delete a project with confirmation.
* List projects.
* Open a project.
* Display project creation and modification dates.

Required Endpoints

GET    /api/v1/projects
POST   /api/v1/projects
GET    /api/v1/projects/{project_id}
PATCH  /api/v1/projects/{project_id}
DELETE /api/v1/projects/{project_id}

Acceptance Criteria

* Duplicate project names are handled clearly.
* Project directories are created automatically.
* Deleting a project must require confirmation.
* The application must not accidentally delete files outside the configured storage root.

Verification

* Create three test projects.
* Rename one project.
* Delete one project.
* Restart the application.
* Confirm that the remaining projects still exist.
* Confirm that each project has its own storage directory.

⸻

Phase 1.3 — Video Import

Features

* Import one video.
* Import multiple videos.
* Import all supported videos from a selected folder.
* Do not duplicate the same video accidentally.
* Show video metadata.

Supported formats should initially include:

.mp4
.avi
.mov
.mkv
.webm

Metadata:

* Filename
* Duration
* FPS
* Frame count
* Resolution
* Codec
* File size
* Import status

File-Access Strategy

The backend runs locally and has access to the user’s file system.

Support one of these approaches:

1. Copy imported videos into project storage
2. Register the original path without copying
3. Let the user choose between copying and referencing

Default to copying for portability unless videos are too large.

Required Endpoints

POST   /api/v1/projects/{project_id}/videos/import
GET    /api/v1/projects/{project_id}/videos
GET    /api/v1/videos/{video_id}
DELETE /api/v1/videos/{video_id}

Verification

* Import a short MP4.
* Import multiple videos.
* Import a folder containing supported and unsupported files.
* Confirm unsupported files are skipped with a clear message.
* Confirm video metadata is correct.
* Confirm importing the same video twice is handled.
* Confirm a corrupt video produces a readable error.
* Restart the application and confirm imported videos remain visible.

⸻

Phase 1.4 — Frame Extraction

Extraction Modes

Support all three modes.

Mode A: Every N Frames

Example:

Extract every 10th frame

Mode B: Frames Per Second

Example:

Extract 2 frames per second

Mode C: Every N Seconds

Example:

Extract one frame every 5 seconds

Configuration

* Output format: JPEG or PNG
* JPEG quality
* Optional resize width
* Optional resize height
* Preserve aspect ratio
* Output naming convention
* Prevent accidental duplicate extraction
* Allow extraction overwrite only after confirmation

Suggested filename format:

{video_stem}_frame_{frame_number}_time_{timestamp_ms}.jpg

Background Processing

Extraction must run outside the request thread.

The UI must show:

* Job status
* Progress percentage
* Processed frames
* Estimated total frames
* Current video
* Cancel action
* Error message

Required Endpoints

POST /api/v1/videos/{video_id}/extraction-jobs
GET  /api/v1/extraction-jobs/{job_id}
POST /api/v1/extraction-jobs/{job_id}/cancel
GET  /api/v1/projects/{project_id}/extraction-jobs

Progress may initially use polling.

Verification

For a known test video:

* Extract every 10th frame.
* Extract at 1 FPS.
* Extract one frame every 2 seconds.
* Confirm the approximate expected frame count for each mode.
* Confirm timestamps increase correctly.
* Confirm image files are readable.
* Confirm cancellation stops an active job.
* Confirm the UI remains responsive during extraction.
* Confirm a failed job has a readable error.
* Confirm restarting the application does not corrupt completed jobs.

⸻

Phase 1.5 — Thumbnail Generation

Requirements

* Generate a thumbnail for every extracted frame.
* Preserve aspect ratio.
* Use a maximum size such as 256×256.
* Cache thumbnails on disk.
* Do not regenerate existing valid thumbnails.
* Generate thumbnails in the background.
* Serve thumbnails through a backend endpoint.
* Never load full-resolution images in the gallery.

Required Endpoints

GET /api/v1/frames/{frame_id}/thumbnail
GET /api/v1/frames/{frame_id}/image

Verification

* Confirm every extracted frame has a thumbnail.
* Delete one thumbnail manually.
* Confirm the application regenerates the missing thumbnail.
* Confirm opening the gallery does not decode every full-resolution image.
* Confirm thumbnail paths remain valid after restarting.

⸻

Phase 1.6 — Virtualized Frame Gallery

Requirements

The gallery must support tens of thousands of frames.

* Use virtualized rendering.
* Render only visible or near-visible items.
* Use lazy thumbnail loading.
* Support pagination or cursor-based fetching.
* Do not return every frame record in one API request.
* Allow adjustable thumbnail size.
* Display selection state.
* Display label indicators.
* Display review status.
* Display frame number and timestamp.
* Support single selection.
* Support Ctrl/Cmd multi-selection.
* Support Shift range selection.

Required Endpoint

GET /api/v1/projects/{project_id}/frames

Supported query parameters:

video_id
page
page_size
cursor
review_status
favorite
rejected
label_ids
unlabeled
sort_by
sort_order

Performance Target

With 40,000 generated frame records:

* Initial gallery page should appear within a reasonable local response time.
* Scrolling should remain responsive.
* The browser must not create 40,000 image elements.
* The backend must not return 40,000 records in one response.
* Memory use should remain stable during extended scrolling.

Verification

Create a test project with at least 40,000 frame records and thumbnails.

Verify:

* Initial gallery loads.
* Scrolling remains usable.
* Only visible items are rendered.
* Filters do not load every frame.
* Changing thumbnail size does not freeze the application.
* Navigating away and back preserves the approximate gallery position.
* No obvious memory growth occurs after repeated scrolling.

⸻

Phase 1.7 — Frame Viewer

Features

* Open a frame from the gallery.
* Show the full-resolution image.
* Previous frame.
* Next frame.
* Fit to screen.
* Original size.
* Zoom in.
* Zoom out.
* Reset zoom.
* Mouse wheel zoom.
* Pan when zoomed.
* Show video name.
* Show frame number.
* Show timestamp.
* Show assigned labels.
* Show review state.

Keyboard Shortcuts

Arrow Left   Previous frame
Arrow Right  Next frame
A            Previous frame
D            Next frame
Escape       Close viewer
F            Toggle favorite
R            Toggle rejected
Space        Toggle reviewed

Verification

* Open a frame.
* Navigate through at least 100 frames using the keyboard.
* Verify navigation does not reload the complete gallery.
* Verify zoom and pan.
* Verify the viewer handles missing image files.
* Verify keyboard shortcuts do not fire while typing into a text field.

⸻

Phase 1.8 — Labels and Review Workflow

Label Management

Users must be able to:

* Create labels
* Edit labels
* Delete labels
* Assign colors
* Assign keyboard shortcuts
* Reorder labels
* Detect shortcut conflicts

Example labels:

Vehicle
Pedestrian
Cyclist
Rain
Night
Construction
Empty
Reject

Label Assignment

* Assign one label to one frame.
* Assign multiple labels to one frame.
* Assign labels to multiple selected frames.
* Remove labels.
* Use keyboard shortcuts.
* Save immediately to SQLite.
* Do not copy images during labeling.

Review Status

Each frame supports:

Unreviewed
Reviewed
Rejected
Favorite

Rejected and favorite can be represented as independent flags if required.

Undo

Implement at least one-level undo for the most recent label or review action.

Required Endpoints

GET    /api/v1/projects/{project_id}/labels
POST   /api/v1/projects/{project_id}/labels
PATCH  /api/v1/labels/{label_id}
DELETE /api/v1/labels/{label_id}
POST   /api/v1/frames/{frame_id}/labels
DELETE /api/v1/frames/{frame_id}/labels/{label_id}
POST   /api/v1/frames/bulk-label
PATCH  /api/v1/frames/{frame_id}/review
POST   /api/v1/frames/bulk-review

Verification

* Create at least five labels.
* Assign every label a unique shortcut.
* Confirm duplicate shortcuts are rejected.
* Assign multiple labels to one frame.
* Assign a label to 100 selected frames.
* Remove a label.
* Mark frames reviewed, rejected, and favorite.
* Use keyboard-only navigation and labeling for 100 frames.
* Restart the application.
* Confirm all labels and statuses remain saved.
* Test undo.

⸻

Phase 1.9 — Filters and Search

Filters

* Video
* Label
* Multiple labels
* Unlabeled
* Reviewed
* Unreviewed
* Rejected
* Favorite

Search

* Frame filename
* Video filename
* Frame number
* Timestamp range

Requirements

* Filters should be reflected in the URL where practical.
* Filters must work with pagination.
* Filter changes must cancel stale requests.
* Display result count.
* Include a clear-all-filters action.

Verification

* Combine video, label, and review filters.
* Filter to unlabeled frames.
* Filter to rejected frames.
* Search by filename.
* Search by frame number.
* Confirm counts match database queries.
* Refresh the page and confirm URL-based filters remain active.

⸻

Phase 1.10 — Session Resume

Persist:

* Last project
* Last video
* Last opened frame
* Gallery scroll position
* Active filters
* Thumbnail size
* Viewer state where practical

Required Endpoints

GET   /api/v1/projects/{project_id}/review-session
PATCH /api/v1/projects/{project_id}/review-session

Verification

* Open a project.
* Apply filters.
* Scroll to a later position.
* Open a frame.
* Close and restart the application.
* Confirm the application returns to the saved context.

⸻

Phase 1.11 — Dataset Export

Export Modes

Support:

1. Export by label folders
2. Export selected frames
3. Export favorites
4. Export reviewed frames
5. Export a metadata manifest

Example label-folder export:

exports/
├── Vehicle/
├── Pedestrian/
├── Rain/
├── Night/
└── Reject/

Manifest example:

{
  "project": "Road Dataset",
  "frames": [
    {
      "source_video": "drive_001.mp4",
      "frame_number": 120,
      "timestamp_seconds": 4.0,
      "exported_filename": "drive_001_frame_000120.jpg",
      "labels": ["Vehicle", "Night"],
      "reviewed": true,
      "favorite": false,
      "rejected": false
    }
  ]
}

Multi-Label Export Behavior

Allow the user to choose:

* Copy the frame into every assigned label folder
* Export images once with labels only in the manifest

Conflict Handling

* Skip existing
* Overwrite
* Rename duplicates

Required Endpoints

POST /api/v1/projects/{project_id}/export-jobs
GET  /api/v1/export-jobs/{job_id}
POST /api/v1/export-jobs/{job_id}/cancel

Verification

* Export one label.
* Export multiple labels.
* Export selected frames.
* Export favorites.
* Confirm files and manifest agree.
* Test skip, overwrite, and rename behavior.
* Test multi-label export.
* Cancel a large export.
* Confirm source images are never modified.

⸻

Phase 1.12 — Phase 1 Automated Tests

Backend Tests

Test:

* Project CRUD
* Video metadata extraction
* Frame sampling calculations
* Extraction job state transitions
* Thumbnail generation
* Label assignment
* Bulk labeling
* Review updates
* Frame filtering
* Session persistence
* Export path safety
* Export manifest generation

Frontend Tests

Test:

* Project creation
* Video list rendering
* Extraction configuration validation
* Gallery loading
* Label shortcut behavior
* Filters
* Review state
* Export dialog

End-to-End Tests

Create Playwright tests for:

1. Create project
2. Import a test video
3. Extract frames
4. Open gallery
5. Create labels
6. Label frames
7. Mark frames reviewed
8. Export a dataset
9. Reload application
10. Confirm state persists

⸻

Phase 1 Completion Gate

Phase 1 is complete only when all conditions below are true.

* All Phase 1 acceptance criteria pass.
* Backend unit tests pass.
* Frontend tests pass.
* End-to-end workflow passes.
* A 40,000-frame test gallery remains usable.
* No known critical or high-severity bugs remain.
* README contains setup and usage instructions.
* Database migration instructions are documented.
* A clean machine can run the application using the documented steps.
* Code is tagged as phase-1-complete.

Do not begin Phase 2 before this gate passes.

⸻

Phase 2 — Workflow and Usability Improvements

Phase 2 Objective

Improve review speed, navigation, observability, and reliability based on feedback from Phase 1 users.

At the end of Phase 2, the application should feel like a polished internal product rather than a basic utility.

⸻

Phase 2.1 — Video Timeline Navigation

Features

* Display a timeline for the active video.
* Show current timestamp.
* Jump to timestamp.
* Jump to frame number.
* Show extraction points.
* Display representative thumbnail markers.
* Support beginning, middle, and end navigation.
* Optionally show labeled and rejected regions.

Verification

* Jump to an exact timestamp.
* Confirm the closest extracted frame opens.
* Drag through the timeline.
* Confirm navigation remains responsive.
* Test short and long videos.
* Test variable-frame-rate videos where possible.

⸻

Phase 2.2 — Batch Selection and Batch Actions

Features

* Select all visible frames.
* Select all filtered frames.
* Select a range.
* Invert selection.
* Clear selection.
* Assign labels in bulk.
* Remove labels in bulk.
* Mark reviewed in bulk.
* Mark rejected in bulk.
* Mark favorite in bulk.
* Export selected frames.

Safety

For actions affecting large numbers of frames:

* Show affected frame count.
* Require confirmation.
* Support cancellation where practical.
* Provide an undo mechanism or action history.

Verification

* Select 1,000 frames.
* Apply a label.
* Remove the label.
* Mark them reviewed.
* Confirm UI and database counts match.
* Test select-all-filtered without loading every frame into the browser.

⸻

Phase 2.3 — Configurable Keyboard Shortcuts

Features

* Let users customize shortcuts.
* Detect conflicts.
* Restore defaults.
* Display a shortcut-help panel.
* Add viewer shortcuts.
* Add gallery shortcuts.
* Add label shortcuts.
* Persist shortcuts per user or local installation.

Verification

* Change a shortcut.
* Restart the application.
* Confirm it persists.
* Attempt to create a conflict.
* Confirm the conflict is rejected or resolved explicitly.
* Confirm shortcuts do not interfere with text inputs.

⸻

Phase 2.4 — Review Queue

Features

Create review queues such as:

* All unreviewed frames
* Frames from one video
* Frames with a selected label
* Rejected frames
* Favorites
* Random sample
* Custom filtered queue

Show:

* Current position
* Total queue length
* Reviewed count
* Remaining count
* Completion percentage

Verification

* Create a queue from filtered frames.
* Review part of the queue.
* Exit and resume.
* Confirm the same queue position is restored.
* Confirm modifying labels does not corrupt queue navigation.

⸻

Phase 2.5 — Statistics Dashboard

Metrics

* Total projects
* Total videos
* Total frames
* Reviewed frames
* Unreviewed frames
* Rejected frames
* Favorite frames
* Frames per label
* Frames per video
* Extraction jobs
* Export jobs
* Review progress over time

Charts

* Label distribution bar chart
* Review-status chart
* Frames per video chart
* Review progress chart

Requirements

* Charts must use aggregated API endpoints.
* Do not send every frame to the frontend for counting.
* Allow filtering by project, video, and date.

Required Endpoint

GET /api/v1/projects/{project_id}/statistics

Verification

* Compare dashboard values with direct database queries.
* Test an empty project.
* Test a large project.
* Confirm statistics update after bulk labeling.
* Confirm statistics update after export where relevant.

⸻

Phase 2.6 — Improved Background Job System

Improvements

* Unified job model for extraction, thumbnail generation, analysis, and export
* Progress reporting
* Cancellation
* Retry
* Failure details
* Job history
* Concurrent-job limit
* Recovery from application restart
* Clear completed-job history

A task queue such as Celery is optional for local use. A simpler internal worker may be preferable.

Verification

* Start multiple jobs.
* Confirm concurrency limits.
* Cancel one job.
* Force one job to fail.
* Retry the failed job.
* Restart the backend during a job.
* Confirm interrupted jobs are marked safely rather than remaining permanently active.

⸻

Phase 2.7 — Action History and Undo/Redo

Features

Track:

* Label assignments
* Label removals
* Review-state changes
* Favorite changes
* Reject changes
* Bulk operations

Support:

* Undo
* Redo
* Action history panel
* User-readable descriptions

Example:

Assigned "Night" to 120 frames
Marked 30 frames as reviewed
Removed "Vehicle" from 8 frames

Verification

* Perform multiple actions.
* Undo them sequentially.
* Redo them.
* Restart the application.
* Confirm persisted actions behave according to the chosen design.
* Test undo for bulk actions.

⸻

Phase 2.8 — Reliability and File Integrity

Features

* Detect missing source videos.
* Detect missing frames.
* Detect missing thumbnails.
* Regenerate thumbnails.
* Validate project paths.
* Run a project integrity scan.
* Prevent path traversal.
* Handle external file renames gracefully.
* Provide a repair report.

Required Endpoint

POST /api/v1/projects/{project_id}/integrity-check

Verification

* Delete a frame manually.
* Delete a thumbnail manually.
* Move or rename a video.
* Run integrity check.
* Confirm issues are detected.
* Confirm safe repairs work.
* Confirm the tool never modifies unrelated directories.

⸻

Phase 2.9 — User Experience Improvements

Features

* Toast notifications
* Confirmation dialogs
* Empty states
* Skeleton loading
* Clear error messages
* Dark mode
* Responsive layout
* Shortcut reference
* First-run onboarding
* Settings page
* Recent projects
* Drag-and-drop import
* Improved accessibility

Verification

* Test all major empty states.
* Test loading states on slower operations.
* Test keyboard navigation.
* Test browser zoom.
* Test dark mode.
* Test common screen sizes.
* Confirm important controls have accessible labels.

⸻

Phase 2.10 — Phase 2 Automated Tests

Add automated tests for:

* Timeline navigation
* Batch operations
* Configurable shortcuts
* Review queues
* Statistics
* Job retries
* Undo and redo
* Integrity scans
* Settings persistence

Add a performance test that:

* Creates 100,000 frame records
* Queries filtered and paginated results
* Measures API response time
* Confirms appropriate indexes are used
* Confirms the browser does not render all records

⸻

Phase 2 Completion Gate

Phase 2 is complete only when:

* All Phase 2 acceptance criteria pass.
* No Phase 1 functionality has regressed.
* Backend, frontend, and end-to-end tests pass.
* A 100,000-frame test project is usable.
* Bulk operations work without loading all frames into the browser.
* Interrupted jobs recover safely.
* Integrity checks detect missing files.
* Keyboard-only review is practical.
* At least one teammate completes a real review workflow and provides feedback.
* Feedback and known limitations are documented.
* Code is tagged as phase-2-complete.

Do not begin Phase 3 before this gate passes.

⸻

Phase 3 — Intelligent Computer Vision Assistance

Phase 3 Objective

Add optional computer-vision features that reduce the number of frames humans must inspect.

All Phase 3 capabilities must be optional.

The user must always be able to inspect original frames and override automated suggestions.

Automated analysis should store results in metadata rather than moving or deleting files automatically.

⸻

Phase 3.1 — Blur Detection

Features

* Calculate a blur score.
* Allow configurable thresholds.
* Mark likely blurry frames.
* Filter by blur score.
* Sort by blur score.
* Review suggested blurry frames.
* Apply reject actions only after user confirmation.

Possible initial method:

* Variance of Laplacian

Design the analysis service so additional methods can be introduced later.

Required Endpoints

POST /api/v1/projects/{project_id}/analysis/blur
GET  /api/v1/projects/{project_id}/frames?blur_min=&blur_max=

Verification

Create a test set containing:

* Sharp images
* Mildly blurred images
* Strongly blurred images
* Motion blur
* Low-light images

Verify:

* Scores are stored.
* Results are sortable.
* Threshold changes do not require recomputing scores.
* The analysis does not automatically delete or reject frames.
* False positives can be manually corrected.

⸻

Phase 3.2 — Brightness and Exposure Analysis

Features

Calculate:

* Mean brightness
* Dark-pixel percentage
* Bright-pixel percentage
* Possible underexposure
* Possible overexposure

Allow:

* Filtering
* Sorting
* Threshold configuration
* Reviewing suggested low-quality frames

Verification

Test:

* Dark images
* Bright images
* High-contrast images
* Normal images
* Night scenes

Confirm the tool presents these as suggestions rather than guaranteed errors.

⸻

Phase 3.3 — Duplicate and Near-Duplicate Detection

Features

Implement duplicate detection in stages.

Stage A: Exact Duplicates

Use a file hash or decoded-image hash.

Stage B: Near Duplicates

Use one or more:

* Perceptual hash
* Difference hash
* Average hash
* Feature embeddings

Group similar frames.

Display:

* Duplicate group
* Representative frame
* Group size
* Similarity score
* Keep-best action
* Review-all action

Do not delete duplicates automatically.

Verification

Test:

* Exact duplicate files
* Same frame with different JPEG quality
* Slight brightness changes
* Adjacent video frames
* Completely unrelated frames

Verify:

* Exact duplicates are detected reliably.
* Near-duplicate threshold is configurable.
* Group membership is stored.
* User can remove a frame from a suggested group.
* No file is deleted without explicit confirmation.

⸻

Phase 3.4 — Scene Change Detection

Features

* Detect scene boundaries.
* Group frames into scenes or segments.
* Display scenes on the video timeline.
* Filter by scene.
* Select representative frames per scene.
* Allow configurable sensitivity.
* Allow manual correction.

Possible methods:

* Histogram difference
* Structural similarity
* PySceneDetect integration

Verification

Test:

* Hard cuts
* Gradual transitions
* Camera motion
* Static scenes
* Lighting changes

Confirm scene boundaries are useful and manually editable.

⸻

Phase 3.5 — Representative Frame Selection

Features

For each scene or similarity cluster:

* Suggest one or more representative frames.
* Prefer sharp frames.
* Prefer well-exposed frames.
* Avoid near duplicates.
* Display the reason for selection.
* Allow users to accept or override suggestions.

Possible ranking inputs:

sharpness
brightness quality
distance from scene boundary
similarity to cluster center
existing labels

Verification

* Run representative selection on several videos.
* Compare suggestions with manual selections.
* Confirm the selected frame belongs to the expected scene.
* Confirm users can replace the suggestion.
* Confirm analysis is deterministic when using the same configuration.

⸻

Phase 3.6 — CLIP or Embedding-Based Similarity Search

Features

* Generate image embeddings.
* Store embeddings efficiently outside SQLite.
* Store embedding metadata in SQLite.
* Search for visually similar frames.
* Select one frame and show similar frames.
* Optionally support text queries if the chosen model supports them.
* Filter similarity search within one project or video.

Possible components:

* OpenCLIP
* FAISS
* NumPy memory-mapped arrays

Requirements

* Model download and model path must be configurable.
* Clearly document hardware requirements.
* CPU execution must be supported where practical.
* GPU use should be optional.
* Embedding model version must be stored.
* Reindexing must be supported.

Verification

* Search using a frame containing a common visual pattern.
* Confirm similar frames rank above unrelated ones.
* Restart the application.
* Confirm the index loads correctly.
* Change model version.
* Confirm the application requests or performs reindexing.
* Test projects with and without embeddings.

⸻

Phase 3.7 — Model-Assisted Pre-Labeling

Features

Create a plugin-style interface for optional model inference.

Initial support may include:

* YOLO-compatible object detection
* ONNX models
* Custom Python inference plugins

Store:

* Model name
* Model version
* Confidence threshold
* Predictions
* Bounding boxes
* Class labels
* Inference timestamp

Display:

* Prediction overlays
* Confidence scores
* Suggested labels
* Accept suggestion
* Reject suggestion
* Edit suggestion

Do not treat predictions as ground truth.

Plugin Interface

Define an interface similar to:

class FrameAnalyzer:
    name: str
    version: str
    def load(self) -> None:
        ...
    def analyze(self, image_path: str) -> dict:
        ...
    def unload(self) -> None:
        ...

Verification

* Load a supported model.
* Run inference on selected frames.
* Run inference on a filtered set.
* Display overlays.
* Accept and reject suggestions.
* Confirm model metadata is stored.
* Confirm disabling the plugin does not affect normal review workflows.
* Confirm inference failure does not corrupt frames or labels.

⸻

Phase 3.8 — Smart Review Queues

Features

Generate queues such as:

* Most blurry first
* Most uncertain model predictions
* Near-duplicate groups
* Representative frame per scene
* Underexposed frames
* Random diverse sample
* Unusual frames based on embedding distance
* Frames not similar to already selected training frames

Each smart queue must explain why frames were selected.

Verification

* Generate each supported queue.
* Confirm queue criteria match stored analysis results.
* Resume a queue after restarting.
* Confirm users can override all suggestions.
* Confirm queue generation does not alter labels automatically.

⸻

Phase 3.9 — Analysis Versioning and Reproducibility

Requirements

Store:

* Analysis method
* Model name
* Model version
* Parameters
* Timestamp
* Code or pipeline version where practical

Allow:

* Re-running analysis
* Comparing analysis versions
* Invalidating stale results
* Deleting analysis metadata without deleting frames

Verification

* Run blur analysis with two configurations.
* Confirm results remain distinguishable.
* Change an embedding model.
* Confirm old and new versions are tracked.
* Delete one analysis version.
* Confirm frames and human labels remain intact.

⸻

Phase 3.10 — Phase 3 Automated Tests

Add tests for:

* Blur-score calculation
* Brightness analysis
* Exact duplicates
* Near-duplicate grouping
* Scene boundaries
* Representative-frame selection
* Embedding indexing
* Similarity search
* Plugin loading
* Inference failure handling
* Smart queue generation
* Analysis versioning

Create small deterministic test fixtures where possible.

For model-based tests:

* Use a tiny test model or mocked inference.
* Do not require a large model download for normal CI.
* Keep GPU tests separate and optional.

⸻

Phase 3 Completion Gate

Phase 3 is complete only when:

* All Phase 3 acceptance criteria pass.
* Phase 1 and Phase 2 workflows still pass.
* Automated suggestions never modify or delete source data without confirmation.
* Analysis results are reproducible and versioned.
* Users can override all automated suggestions.
* Similarity indexes survive application restarts.
* Model plugins fail safely.
* Smart queues provide understandable selection reasons.
* At least one real project demonstrates measurable review-time improvement.
* Performance results and limitations are documented.
* Code is tagged as phase-3-complete.

⸻

Final System Verification

After all three phases, perform the following complete test.

Test Dataset

Prepare:

* At least 10 videos
* At least one long video
* At least one corrupt video
* At least one variable-frame-rate video if available
* At least 100,000 extracted frame records
* Sharp and blurry frames
* Bright and dark frames
* Duplicate and near-duplicate frames
* Multiple scene transitions

Full Workflow

1. Start from a clean installation.
2. Run database migrations.
3. Start backend and frontend.
4. Create a project.
5. Import videos.
6. Extract frames using all three extraction modes.
7. Cancel one extraction.
8. Retry one failed extraction.
9. Browse the virtualized gallery.
10. Create labels.
11. Review frames using keyboard shortcuts.
12. Perform bulk labeling.
13. Create and resume a review queue.
14. Close and restart the application.
15. Confirm session restoration.
16. Run blur analysis.
17. Run exposure analysis.
18. Detect duplicate groups.
19. Detect scenes.
20. Generate representative frames.
21. Build a similarity index.
22. Run similar-frame search.
23. Run optional model inference.
24. Accept and reject model suggestions.
25. Export a curated dataset.
26. Validate the export manifest.
27. Run a project integrity check.
28. Confirm source videos and source frames remain unchanged.

⸻

Non-Functional Requirements

Performance

* Support at least 100,000 frame records per project.
* Use pagination or cursor-based APIs.
* Use virtualized frontend rendering.
* Use thumbnail caching.
* Add database indexes.
* Avoid synchronous long-running API requests.
* Do not load all frame images into memory.
* Do not load all frame records into the browser.

Data Safety

* Never modify source videos.
* Never delete files outside project storage.
* Require confirmation for destructive actions.
* Validate all generated paths.
* Preserve human labels when analysis is re-run.
* Support database backup.
* Use transactions for bulk metadata updates.

Security

Although this is initially local:

* Validate file paths.
* Prevent path traversal.
* Restrict file-serving endpoints to configured project directories.
* Validate uploaded or selected file types.
* Avoid shell commands containing untrusted strings.
* Do not expose the server beyond localhost by default.
* Document how authentication should be added before remote deployment.

Maintainability

* Keep services modular.
* Keep UI components reusable.
* Document APIs.
* Include migrations.
* Include tests.
* Include sample configuration.
* Add structured logs.
* Add a troubleshooting section.
* Avoid premature distributed-system complexity.

⸻

Copilot Implementation Instructions

Implement one task group at a time.

For every task group:

1. Explain the proposed implementation.
2. List files that will be created or changed.
3. Implement the smallest complete version.
4. Add or update tests.
5. Run relevant tests.
6. Report failures honestly.
7. Fix failures before proceeding.
8. Update documentation.
9. Mark the task complete only after acceptance criteria pass.

Do not generate the entire application in one response.

Do not skip tests.

Do not begin the next phase until the current phase completion gate passes.

When uncertain, prefer a simple local implementation over unnecessary infrastructure.

⸻

Suggested Copilot Prompts

Start Phase 1

Read tasks.md and implement only Phase 1.1: Project Setup.
Before coding:
1. Explain the architecture.
2. List the files you will create or modify.
3. Identify assumptions.
Then implement Phase 1.1, add tests, run the tests, and verify every acceptance criterion. Do not start Phase 1.2.

Continue Within a Phase

Read tasks.md and inspect the current repository.
Implement only Phase 1.4: Frame Extraction.
Do not change completed features unless required. Add backend and frontend tests, run them, and verify every item in the Phase 1.4 verification checklist. Report any unresolved issue before marking the task complete.

Verify Phase 1

Read the Phase 1 Completion Gate in tasks.md.
Do not implement Phase 2.
Audit the complete Phase 1 implementation, run all backend, frontend, end-to-end, and performance tests, and produce a verification report containing:
- Passed criteria
- Failed criteria
- Missing tests
- Bugs found
- Performance observations
- Required fixes
Fix all critical and high-severity issues, rerun the tests, and only then mark Phase 1 complete.

Start Phase 2

Confirm that the Phase 1 Completion Gate has passed.
Then implement only Phase 2.1: Video Timeline Navigation. Add tests and verify every acceptance criterion. Do not proceed to Phase 2.2.

Verify Phase 2

Audit the implementation against the Phase 2 Completion Gate in tasks.md.
Run regression tests for Phase 1 and all Phase 2 tests. Run the 100,000-frame performance test. Fix critical and high-severity issues. Produce a final Phase 2 verification report before beginning Phase 3.

Start Phase 3

Confirm that the Phase 2 Completion Gate has passed.
Implement only Phase 3.1: Blur Detection. Automated results must be suggestions only and must not reject or delete frames. Add deterministic tests and verify every acceptance criterion.

Final Audit

Perform the Final System Verification defined in tasks.md.
Do not assume features work because unit tests pass. Run the full workflow from a clean installation, document results, record performance observations, identify missing or unstable functionality, and fix critical and high-severity issues.
Produce a final report with:
- Environment
- Test data
- Features tested
- Passed checks
- Failed checks
- Known limitations
- Performance results
- Recommended next steps

⸻

Definition of Done

A task is done only when:

* Implementation is complete.
* Acceptance criteria pass.
* Tests exist.
* Tests pass.
* Errors are handled.
* Documentation is updated.
* No critical regression is introduced.
* The verification result is recorded.

A phase is done only when its completion gate passes.