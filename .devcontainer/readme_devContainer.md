# Dev Container

Note: This folder is useful for online IDE -Codespaces (not needed for local development).

This folder contains the GitHub Codespaces / VS Code Dev Containers setup for the project.

- `devcontainer.json` provisions the universal base image, runs `npm install && npm run build` after cloning, and launches `npm run dev` when the workspace attaches.
- Port `3000` is forwarded and labelled "Application" so the Codespaces preview opens automatically.
- `icon.svg` is just the icon that appears in the Dev Containers UI.


