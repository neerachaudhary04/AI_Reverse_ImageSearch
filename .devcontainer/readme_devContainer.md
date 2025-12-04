# Dev Container

Note: This folder is only needed when working in an online IDE like GitHub Codespaces; please ignore it for local development.

This folder contains the GitHub Codespaces / VS Code Dev Containers setup for the project.

- `devcontainer.json` provisions the universal base image, runs `npm install && npm run build` after cloning, and launches `npm run dev` when the workspace attaches.
- Port `3000` is forwarded and labelled "Application" so the Codespaces preview opens automatically.
- `icon.svg` is just the icon that appears in the Dev Containers UI.


