# Vector Code AI

A mobile-first coding assistant designed for low-memory phones. The browser stays lightweight; repository inspection, AI planning and code generation run on the Flask server.

## Features
- Lists repositories accessible to the configured GitHub account.
- Inspects repository files and creates a focused implementation plan.
- Generates reviewable full-file changes in batches of up to six files.
- Displays proposed file contents before writing anything.
- Commits approved changes to a new branch; the base branch is not changed.
- Keeps GitHub and AI credentials on the server, never in browser code.

## Render setup
Connect this repository to a Render Web Service.

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT app:app`
- Runtime: Python 3

Set these environment variables in the Render service:
- `GEMINI_API_KEY`: your AI provider API key.
- `GITHUB_TOKEN`: a GitHub fine-grained personal access token limited to the repositories this app should access, with Contents read/write permission.
- `APP_ACCESS_KEY`: a long private access key you create. The app requires it for all API requests.
- Optional `GEMINI_MODEL`: defaults to `gemini-3.1-flash-lite`.

Never paste secrets into source code, commits, or chat. Never expose the GitHub token in browser JavaScript.

## Safety and limits
- The access key is required on all API routes.
- AI output is only a proposal until you inspect it and press the commit button.
- Commits are made to a new branch, never directly to the selected base branch.
- One generation step can inspect and modify at most six text files.
- Binary files and very large repository trees are not supported.
- Review the branch and run tests before merging.

## Local run
```bash
pip install -r requirements.txt
export GEMINI_API_KEY="..."
export GITHUB_TOKEN="..."
export APP_ACCESS_KEY="..."
python app.py
```
