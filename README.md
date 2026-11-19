# Vector Code AI

A lightweight, mobile-first AI coding workspace. The phone runs only the web interface; GitHub repository access and AI code generation run on the Render server.

## Features
- Chat-style coding workspace with a collapsible conversation-history sidebar.
- Chat history is saved locally in the browser on the device.
- GitHub OAuth sign-in; repositories are loaded from the signed-in account.
- AI repository planning and code generation in batches of up to six files.
- Review proposed complete file contents before committing.
- Approved changes are committed to a new branch; the base branch is left unchanged.

## GitHub OAuth setup

1. In GitHub, open **Settings → Developer settings → OAuth Apps → New OAuth App**.
2. Set the Homepage URL to your Render service URL.
3. Set the Authorization callback URL to:
   `https://YOUR-RENDER-SERVICE.onrender.com/auth/github/callback`
4. Create the OAuth App and copy its Client ID. Generate a Client Secret.
5. In Render, add these environment variables:

- `GITHUB_CLIENT_ID`: OAuth App Client ID.
- `GITHUB_CLIENT_SECRET`: OAuth App Client Secret.
- `FLASK_SECRET_KEY`: a long, random secret used to sign browser sessions.
- `GEMINI_API_KEY`: AI provider API key.
- Optional `GEMINI_MODEL`: defaults to `gemini-3.1-flash-lite`.

Do not put any of these secrets in GitHub source files or browser JavaScript. Never share them in chat.

The OAuth app requests `repo` and `read:user` scopes so it can list and work with repositories the signed-in account is authorized to access. Only create commits after reviewing the proposed changes.

## Render

- Runtime: Python 3
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT app:app`
- Deploy branch: `vector-code-ai`

The server keeps OAuth tokens in process memory and the browser receives only a signed opaque session identifier. Use one Gunicorn worker with this lightweight in-memory session implementation. Users may need to sign in again after a server restart or redeploy.

## Current limits

- Up to 100 repositories are loaded in the picker.
- Each generation step can inspect and change at most six text files.
- Binary files and very large/truncated repository trees are not supported.
- Chat history is stored in the current browser's local storage; it is not synchronized across devices.
- Run project tests and review the new branch before merging.
