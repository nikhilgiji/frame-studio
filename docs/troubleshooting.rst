Troubleshooting
===============

The browser says the API is unavailable
---------------------------------------

Confirm the backend is running on port 8000 and that ``VITE_API_URL`` points to
``http://127.0.0.1:8000/api/v1``. If using a different frontend port, add its
origin to ``VISION_CURATOR_CORS_ORIGINS`` and restart the backend.

The backend root returns 404
----------------------------

This is expected. The backend serves ``/api/v1/*`` and ``/docs``. Open the UI
from the Vite address, normally ``http://127.0.0.1:3000``.

The project page still looks too wide
-------------------------------------

Hard-refresh the browser after updating the frontend. Confirm Vite rebuilt
``src/styles.css`` and reset browser zoom to 100%. The automated RWD suite checks
the dashboard and populated gallery from 320 through 1440 pixels.

A video cannot be imported or decoded
--------------------------------------

Verify that the extension is MP4, AVI, MOV, MKV, or WebM and that OpenCV can
decode its codec. The import result includes a per-file error. Converting the
video to H.264 MP4 is a broadly compatible fallback.

Frames or thumbnails are missing
--------------------------------

Open **File integrity** on the project Overview. Missing thumbnails can be
regenerated from valid frame images. Missing source frames or videos are
reported but not fabricated.

Migration uses the wrong database
---------------------------------

Run ``alembic current`` from ``backend/`` and inspect
``VISION_CURATOR_DATABASE_URL``. Relative SQLite paths are sensitive to the
working directory. Back up valuable databases before changing migration
history.

Build the documentation locally
-------------------------------

Use the existing repository virtual environment:

.. code-block:: console

   (.venv) $ python -m pip install -r docs/requirements.txt
   (.venv) $ sphinx-build -W -b html docs docs/_build/html

Open ``docs/_build/html/index.html``. On Read the Docs, import the repository;
the root ``.readthedocs.yaml`` installs the documentation requirements and
builds the same Sphinx site.
