# News Brief Desk

## Overview
News Brief Desk is a lightweight newsroom workflow demo designed for a take-home assignment. It simulates the flow from raw incoming items to grouped stories, draft briefs, editorial review, approval, and publication. The app is intended to show how a small editorial desk can reduce duplicate reporting, create concise briefs from clustered sources, and track publication delay.

## Problem
The newsroom receives raw items from multiple sources throughout the day. Many are repetitive, some are similar but not the same event, and a few become known as a single story only after more information arrives. The system needs to help reporters cluster likely duplicates, draft a short brief, and give editors a simple review-and-publish workflow without allowing the reporter role to publish.

## Features
- Demo role selector for Reporter, Editor, and Desk Head
- SQLite-backed dataset and workflow history
- Grouping and deduplication from source material using lightweight text similarity
- Draft story creation from grouped items
- Brief generation using OpenAI when an API key is available, otherwise a deterministic fallback summary
- Role-based permission checks for publishing and duplication prevention
- Desk dashboard with publication timing metrics and publication history
- Synthetic newsroom sample data covering duplicate and near-duplicate stories

## Architecture
The app uses a simple layered architecture:
- `app.py` holds the Streamlit interface and page logic
- `database.py` manages SQLite setup, schema, data seeding, and CRUD access
- `models.py` contains the lightweight data classes
- `news_data.py` contains the synthetic newsroom feed
- `clustering.py` identifies likely duplicates or similar events
- `ai_service.py` runs AI brief generation when configured and falls back otherwise
- `workflow.py` enforces permissions and story state transitions
- `dashboard.py` calculates publication metrics
- `utils/helpers.py` supports text normalization and time formatting

## Tech Stack
- Python 3.12
- Streamlit
- SQLite
- Pandas
- Python-dotenv
- Optional OpenAI API client

## Project Structure
- `app.py`
- `database.py`
- `models.py`
- `news_data.py`
- `clustering.py`
- `ai_service.py`
- `workflow.py`
- `dashboard.py`
- `requirements.txt`
- `README.md`
- `.gitignore`
- `.env.example`
- `data/news.db`
- `utils/helpers.py`

## How to Run
Create a virtual environment and install dependencies:

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Then start the app:

```powershell
streamlit run app.py
```

## Environment Variables
This app uses a `.env` file for optional AI configuration. Create a `.env` file in the project root.

Example:

```env
OPENAI_API_KEY=your-key-here
```

If no API key is configured, the app will not crash and will generate a deterministic brief from the grouped source material instead.

## User Roles
- Reporter: groups raw items and drafts briefs; cannot publish
- Editor: reviews, rewrites, approves, and publishes
- Desk Head: monitors published output and publication timing

This is a demo authentication model. In production, this would be replaced with a secure user system and proper authorization.

## Workflow
Incoming
→ Group
→ Draft
→ Editor Review
→ Approve
→ Publish

## Grouping Approach
The system uses lightweight, deterministic grouping rather than a full ML pipeline. It normalizes headlines and content, compares shared keywords and token overlap, and uses a simple similarity threshold to suggest likely duplicate clusters. This keeps the application reliable in a demo environment and ensures it works without an external API.

When a story later turns out to be a merged event after publication, the app records that activity in the story history instead of creating a second published story record. The published story remains the authoritative record while new source items are added to it.

## AI Usage
This app does not require an AI tool to function. The code in `ai_service.py` checks for `OPENAI_API_KEY` and, if present, sends a prompt to OpenAI using the Responses API. If no key is available, the app uses a deterministic fallback summarizer. No secrets are stored in source code.

Files/features that rely on AI:
- `ai_service.py`
- brief generation during story creation and editorial review when applicable

## Decisions and Assumptions
- Grouping logic is intentionally simple and deterministic: text similarity + keyword overlap + source context.
- Reporter is not authorized to publish because the backend permission layer blocks that action.
- A published story cannot be published again; the workflow raises a permission error.
- Merge-after-publication behavior is handled by preserving the published story, adding new sources, and logging a `MERGED_WITH_EXISTING_STORY` event in `story_history`.
- Demo authentication uses a role selector in the Streamlit UI rather than full user login.
- Time-to-publication is computed as the difference between the published timestamp and the earliest received timestamp among the story’s source items.
- Fallback summarization is deterministic and based on the grouped material so the app works in offline or API-less environments.

## Sample Data
The sample feed is intentionally synthetic and labeled as demo data in the UI. It includes multiple real-world-looking items from sources such as Reuters, The Hindu, Associated Press, BBC News, Indian Express, and local desk feeds. The dataset includes:
- three versions of the same Bengaluru Metro signalling disruption
- a similar but different Chennai Metro signalling issue
- several unrelated but realistic stories such as flood response, school heat advisories, public transport disruption, and health service expansion

## Testing
The following checks were performed during development and validation:
1. Three source items for the same event are grouped together.
2. Similar-looking different stories remain separate.
3. Reporter cannot publish.
4. Editor can publish.
5. A published story cannot be published twice.
6. Story merge preserves history.
7. Dashboard calculates publication delay from the first incoming source.
8. The app works without an API key and generates a fallback brief.

## Future Improvements
If more time were available, I would add:
- real authentication and authorization
- better semantic clustering with embeddings or a vector database
- background ingestion and story processing jobs
- source ingestion APIs and feed polling
- richer audit logging for editorial actions
- more analytics and alerting for desk operations
- production-grade database and deployment configuration
- automated UI and workflow tests
- monitoring and operational dashboards

## Deployment
The app is built to run on Streamlit Community Cloud with minimal changes. For deployment:
1. Ensure `requirements.txt` includes the Python dependencies.
2. Keep secrets out of source control and use environment variables in the deployment environment.
3. Run `streamlit run app.py` in the deployed environment.

## GitHub Readiness
The repository is designed for public GitHub use. It includes a `.gitignore` file with `.env` and local database files excluded. No API key should be committed to the repo.

## Notes
This project is a demo newsroom application built for local demonstration and assignment validation. It is not a production editorial platform and does not include enterprise authentication or full audit controls.
