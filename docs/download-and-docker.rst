Download and Docker setup
=========================

Docker is the recommended way to run Frame Studio. It downloads prebuilt
frontend and backend images from GitHub Container Registry, applies database
migrations automatically, and keeps the database, imported videos, frames,
thumbnails, and exports in a persistent Docker volume.

Requirements
------------

Install Docker Desktop on Windows, macOS, or Linux, or install Docker Engine
with the Compose plugin on Linux. Verify both commands work:

.. code-block:: console

   $ docker --version
   $ docker compose version

Run the prebuilt release
------------------------

Create a directory and download the Compose file—no source checkout or local
build is required:

.. code-block:: console

   $ mkdir frame-studio
   $ cd frame-studio
   $ curl -LO https://raw.githubusercontent.com/nikhilgiji/frame-studio/main/compose.yaml
   $ docker compose pull
   $ docker compose up -d

Open ``http://localhost:3000``. The first start can take a little longer while
the images download and the backend checks database migrations.

Use a different host port by setting ``FRAME_STUDIO_PORT``:

.. code-block:: console

   $ FRAME_STUDIO_PORT=8080 docker compose up -d

Then open ``http://localhost:8080``. No backend configuration is necessary:
browser traffic uses the same-origin Nginx proxy.

.. note::

   The public images are published for Intel/AMD 64-bit and ARM64 systems,
   including Apple Silicon, and can be pulled without signing in to GitHub.

Manage the application
----------------------

.. code-block:: console

   # View status
   $ docker compose ps

   # Follow logs
   $ docker compose logs -f

   # Stop without deleting data
   $ docker compose down

   # Start again
   $ docker compose up -d

Do not add ``--volumes`` to ``docker compose down`` unless you deliberately
want to delete the Frame Studio data volume.

Upgrade
-------

The ``latest`` tag tracks the main branch. Pull and recreate containers to
upgrade while preserving data:

.. code-block:: console

   $ docker compose pull
   $ docker compose up -d

For a tagged release, set ``FRAME_STUDIO_VERSION`` to the release number used
by the image, for example:

.. code-block:: console

   $ FRAME_STUDIO_VERSION=0.1.0 docker compose pull
   $ FRAME_STUDIO_VERSION=0.1.0 docker compose up -d

Back up data
------------

Stop the application briefly for a consistent SQLite backup, then archive the
named volume into the current directory:

.. code-block:: console

   $ docker compose down
   $ docker run --rm \
       -v frame-studio-data:/data:ro \
       -v "$PWD":/backup \
       alpine:3.21 \
       tar czf /backup/frame-studio-backup.tgz -C /data .
   $ docker compose up -d

Store ``frame-studio-backup.tgz`` somewhere safe. It contains the database and
all managed media. Test backups periodically before relying on them.

Build from source
-----------------

Developers can clone the repository and build both images locally by applying
the build override:

.. code-block:: console

   $ git clone https://github.com/nikhilgiji/frame-studio.git
   $ cd frame-studio
   $ docker compose -f compose.yaml -f compose.build.yaml build
   $ docker compose -f compose.yaml -f compose.build.yaml up -d

The local Python/Node development setup remains available in
:doc:`getting-started`.

Container architecture
----------------------

The frontend image contains the compiled React application and Nginx. Nginx
serves static assets, supports direct navigation to React routes, accepts large
video uploads, and proxies ``/api`` requests to the private backend service.
The backend image runs Alembic migrations before FastAPI starts. Only the
frontend port is exposed to the host.
