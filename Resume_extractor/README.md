# Resume Extractor

This is a Streamlit-based application for extracting structured information from PDF resumes using Large Language Models (LLMs) via LangChain and Together API.

## Features
- Upload PDF resumes and extract:
  - Name, email, phone
  - Skills
  - Work experience (with projects, durations, etc.)
- View and filter saved resumes by skills
- All resume data is stored in `resumes.json`

## How to Run (Docker)
1. Make sure Docker and Docker Compose are installed.
2. From the project root, build and run:
   ```sh
   docker compose up --build
   ```
3. Access the app at [http://localhost:8501](http://localhost:8501)

## How to Run (Locally)
1. Install Python 3.9+ and dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the app:
   ```sh
   streamlit run langchain_resume_extractor.py
   ```

## Folder Structure
- `langchain_resume_extractor.py` – Main Streamlit app
- `resumes.json` – Saved extracted resumes
- `uploaded_resumes/` – Folder for uploaded PDF files

## Notes
- Requires a valid Together API key (currently hardcoded for demo)
- For deployment, move API keys to environment variables

---
