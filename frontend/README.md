# Metamorph React Frontend

This directory is the home for the React (Node 18) SPA. `docker-compose` mounts it into the `frontend` service. Add `package.json`, source files, and any build scripts under this directory.

In development the service runs the dev server with hot reload, while production builds static assets served either by the same container or a lightweight static server.
