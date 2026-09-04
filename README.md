# News Brief Desk

A Streamlit-based newsroom dashboard for tracking incoming news items, published stories, and publishing turnaround time.

## 🚀 Live Demo

https://vivek65666-news-brief-desk-app-hblsd8.streamlit.app/

## 📊 Dashboard Metrics

- Published today
- Published yesterday
- Average time to publish
- Incoming news items
- Recent published stories

## 🛠️ Tech Stack

- Python
- Streamlit
- SQLite
- Pandas

## ✨ Features

## 🧠 Decisions & Assumptions

- The application uses a synthetic newsroom dataset because no production data was provided.
- Raw news items are grouped into story clusters based on similarity so that multiple reports about the same event can be handled as one story.
- Similar-looking but unrelated stories are intentionally included in the dataset to test grouping behavior.
- A story follows a newsroom workflow from incoming item → grouping → draft → editorial review → publication.
- Reporters can work on incoming items and prepare drafts, but they cannot publish stories.
- Editors are responsible for rewriting, approving, and publishing stories.
- Once a story is published, it is treated as final and cannot be published again.
- Publishing metrics are calculated using source and publication timestamps.
- Authentication is implemented as demo authentication for this assessment; production would require proper authentication and authorization.
- SQLite was selected as a lightweight database suitable for this assessment and easy local/deployed demonstration.

## 🤖 AI Tools Used

AI tools were used during development to assist with implementation, debugging, documentation, and problem solving.

- ChatGPT — used for development guidance, debugging, code suggestions, README preparation, and troubleshooting.
- AI-assisted development suggestions were reviewed and tested manually before being included in the project.
- The application includes AI/service logic for assisting with newsroom brief generation where applicable.

## 🔮 What I Would Do With Another Week

With another week, I would improve the application in the following areas:

- Implement production-grade authentication and role-based authorization.
- Improve story clustering using embeddings and more robust semantic similarity.
- Add stronger duplicate detection and allow editors to merge related stories after publication with an audit trail.
- Add automated tests for workflow rules, clustering, database operations, and permissions.
- Add richer desk analytics with publishing-time trends and subject/category breakdowns.
- Add search, filtering, and sorting for incoming and published stories.
- Add persistent production database storage instead of relying on SQLite.
- Add monitoring, logging, and stronger error handling for production deployment.
- Improve the UI for faster newsroom workflows and mobile responsiveness.

## ▶️ Run Locally

Clone the repository:

git clone https://github.com/vivek65666/news-brief-desk.git

Navigate to the project:

cd news-brief-desk

Create and activate a virtual environment:

python -m venv .venv

Install dependencies:

pip install -r requirements.txt

Run the application:

streamlit run app.py

## 🔐 Authentication

This project currently uses demo authentication for demonstration purposes. Production deployment would require real authentication and authorization.

## 📌 Project Status

Deployed successfully on Streamlit Community Cloud.
