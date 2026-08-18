Getting started
===============

This page describes the Python-only installation. The compiled web interface is
included in the backend package, so normal users do not need Node.js, npm, or a
frontend build. Docker remains available in :doc:`download-and-docker`.

Requirements
------------

Frame Studio requires Git, Python 3.11 or newer, and a modern browser. FFmpeg,
Node.js, and npm are not required; video probing and frame extraction use
OpenCV. Node.js 20 or newer is needed only by contributors changing the React
source.

Install
-------

Create and activate the repository-local virtual environment **before**
installing Python packages:

.. code-block:: console

   $ python3 -m venv .venv
   $ source .venv/bin/activate
   (.venv) $ python -m pip install --upgrade pip
   (.venv) $ python -m pip install ./backend
   (.venv) $ cp .env.example .env

Apply database migrations:

.. code-block:: console

   (.venv) $ cd backend
   (.venv) $ ../.venv/bin/alembic upgrade head
   (.venv) $ cd ..

Run the application
-------------------

Start Frame Studio:

.. code-block:: console

   (.venv) $ cd backend
   (.venv) $ ../.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

Open ``http://127.0.0.1:8000``. FastAPI serves both the packaged interface and
the API from one process. Interactive API documentation is at
``http://127.0.0.1:8000/docs`` and the health check is at ``/api/v1/health``.

Windows PowerShell
------------------

.. code-block:: powershell

   git clone https://github.com/nikhilgiji/frame-studio.git
   Set-Location frame-studio
   git checkout v0.1.1
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install .\backend
   Copy-Item .env.example .env
   Set-Location backend
   ..\.venv\Scripts\alembic.exe upgrade head
   ..\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000

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
   Build-time API URL used only when a developer rebuilds the frontend. The
   packaged interface uses the same-origin ``/api/v1`` path.

Frontend development
--------------------

Only contributors modifying ``frontend/`` need Node.js and npm. Install with
``npm ci --prefix frontend`` and run ``npm run dev`` inside ``frontend/``. To
refresh the assets embedded in Python, build with ``VITE_API_URL=/api/v1`` and
copy ``frontend/dist`` into ``backend/app/static``.

.. warning::

   Frame Studio is designed as a single-user localhost application. Do not
   expose it to a network without authentication, authorization, TLS, and a
   review of its filesystem and CORS configuration.
