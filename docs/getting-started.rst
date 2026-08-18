Getting started
===============

This page describes the source-based development setup. Most users should use
the prebuilt containers in :doc:`download-and-docker`; they do not require
Python, Node.js, npm, or a local build.

Requirements
------------

Frame Studio requires Python 3.11 or newer, Node.js 20 or newer, npm, and a
modern Chromium-compatible browser. FFmpeg is not required; video probing and
frame extraction use OpenCV.

Install
-------

Create and activate the repository-local virtual environment **before**
installing Python packages:

.. code-block:: console

   $ python3 -m venv .venv
   $ source .venv/bin/activate
   (.venv) $ python -m pip install --upgrade pip
   (.venv) $ python -m pip install -e './backend[dev]'
   (.venv) $ npm ci --prefix frontend
   (.venv) $ cp .env.example .env

Apply database migrations:

.. code-block:: console

   (.venv) $ cd backend
   (.venv) $ ../.venv/bin/alembic upgrade head
   (.venv) $ cd ..

Run the application
-------------------

Start the backend from one terminal:

.. code-block:: console

   (.venv) $ cd backend
   (.venv) $ ../.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Start the frontend from a second terminal:

.. code-block:: console

   (.venv) $ cd frontend
   (.venv) $ npm run dev

Open ``http://127.0.0.1:3000``. A ``404`` response at
``http://127.0.0.1:8000/`` is expected because the backend serves API routes,
not the frontend. Use ``http://127.0.0.1:8000/docs`` for interactive API
documentation or ``/api/v1/health`` for the health check.

Configuration
-------------

Settings are read from the repository ``.env`` file. The important variables
are:

``VISION_CURATOR_DATABASE_URL``
   SQLite connection URL. The historical prefix is preserved for upgrades.

``VISION_CURATOR_STORAGE_ROOT``
   Managed video, frame, thumbnail, and export directory.

``VISION_CURATOR_CORS_ORIGINS``
   JSON list of frontend origins allowed to call the API.

``VISION_CURATOR_CONCURRENT_JOB_LIMIT``
   Maximum simultaneous background jobs; defaults to two.

``VITE_API_URL``
   API base URL used by the frontend.

.. warning::

   Frame Studio is designed as a single-user localhost application. Do not
   expose it to a network without authentication, authorization, TLS, and a
   review of its filesystem and CORS configuration.
