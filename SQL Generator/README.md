# SQL Generator (Natural Language to SQL)

This is a Streamlit-based application that translates natural language questions into SQL queries for a social media database using LLMs (LangChain + Together API).

## Features
- Enter natural language questions about your database (e.g., "Show me all the male users")
- See the generated SQL query and the query results
- Explore and test custom SQL queries directly
- View agent reasoning and logs for advanced debugging

## How to Run (Docker)
1. Make sure Docker and Docker Compose are installed.
2. From the project root, build and run:
   ```sh
   docker compose up --build
   ```
3. Access the app at [http://localhost:8502](http://localhost:8502)

## How to Run (Locally)
1. Install Python 3.9+ and dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the app:
   ```sh
   streamlit run nlp_to_sql.py
   ```

## Folder Structure
- `nlp_to_sql.py` – Main Streamlit app for NL-to-SQL
- `create_db.py` – Script to create and populate `social_media.db` (run if DB is missing)
- `social_media.db` – SQLite database file

## Notes
- Requires a valid Together API key (currently hardcoded for demo)
- For deployment, move API keys to environment variables
- The app supports schema-aware, explainable SQL generation with fallback for ambiguous queries

---
