import streamlit as st
import os
import sqlite3
import pandas as pd
from langchain_together import Together
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.schema import OutputParserException
from langchain.tools import Tool

# Set Together API key securely (for demo only; move to env var in prod!)
os.environ["TOGETHER_API_KEY"] = "ce142861c7d89ac010c16d12d7da1ca855a95f7cb4bc405d799c8dcca06a40b5"

# Initialize LLM
llm = Together(
    model="meta-llama/Llama-4-Scout-17B-16E-Instruct",
    max_tokens=512,
    temperature=0.7
)

DB_PATH = "social_media.db"
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

INSTRUCTION_PROMPT = """
You are an intelligent assistant that translates natural language into correct SQL queries.
- Always use correct SQL syntax.
- Use only the provided tables and columns.
- Do not use any table or column that is not listed in the schema.
- If the user refers to something not in the schema, ignore it.
- Only use the tables: Users, Posts, Comments.
- Return ONLY the SQL query, nothing else.
- Do not explain or add commentary.
- Do NOT use code blocks or markdown formatting. Output only plain SQL.

NOTE : Give the SQL Query directly without any special characters like '```' and avoid duplicate queries

Go through user question carefully and generate the correct SQL query.

Schema:
{schema}

User Question: {input}
SQL Query:
"""

prompt_template = PromptTemplate(
    input_variables=["schema", "input"],
    template=INSTRUCTION_PROMPT
)

def elaborate_user_query(nl_query: str) -> str:
    prompt = f"""
You are a helpful assistant who clarifies vague or subjective natural language database queries.

Given the query:
"{nl_query}"

1. Identify and explain any ambiguous or subjective terms (e.g., "popular", "negative", "recent").
2. Suggest how they could be interpreted in terms of the schema (Users, Posts, Comments).
3. Rephrase the query in a more precise way to help an LLM generate SQL.

Response:
"""
    return llm.predict(prompt).strip()

query_explainer_tool = Tool(
    name="QueryExplainer",
    func=elaborate_user_query,
    description=(
        """Use this tool when the user's question is vague, emotional, or subjective. 
        This tool helps clarify terms like 'negative', 'frequent', 'popular', etc. 
        Input should be the raw user question. The tool explains how to interpret the query clearly. Also provide with diverse examples to make the subjective query as clear as possible"""
    ),
)

import io
import contextlib

def run_agent(query, max_retries=2, capture_verbose=False):
    schema = db.get_table_info()
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()
    tools.append(query_explainer_tool)

    agent = initialize_agent(
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        tools=tools,
        llm=llm,
        verbose=True if capture_verbose else False,
        handle_parsing_errors=True,
        agent_kwargs={
            "prefix": prompt_template.template.format(schema=schema, input="{input}")
        }
    )

    retries = 0
    logs = ""
    while retries < max_retries:
        try:
            if capture_verbose:
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    result = agent.run(query)
                logs = buf.getvalue()
                return result, logs
            else:
                return agent.run(query), None
        except OutputParserException:
            retries += 1
    raise Exception("Failed to parse LLM output after retries.")

def fallback_llm(query):
    schema = db.get_table_info()
    prompt_text = prompt_template.format(schema=schema, input=query)
    raw_output = llm.predict(prompt_text)
    sql = raw_output.strip()
    if sql.startswith("```sql"):
        sql = sql.replace("```sql", "").replace("```", "").strip()
    sql = sql.split(";")[0].strip()
    return sql

def execute_sql(sql):
    if not sql.lower().startswith("select"):
        return None, "LLM output does not appear to be a valid SELECT SQL query."
    try:
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(sql, conn)
        return df, None
    except Exception as e:
        return None, str(e)

def test_sql_execute_query(query):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        return None

# --- Streamlit UI ---
st.set_page_config(page_title="Social Media DB Query", layout="wide")
st.markdown(
    """
    <h1 style='text-align: center; color: #4CAF50; font-size: 50px;'>
        Social Media Database Query System 🤖
    </h1>
    """,
    unsafe_allow_html=True
)
tabs = st.tabs(["nlp_to_sql", "test_sql"])

# --- NLP to SQL Tab ---
with tabs[0]:
    st.title("Natural Language Queries to SQL")
    st.markdown("""
    Enter a natural language question about your database. Example queries:
    - Show me all the male users
    - Show me all the users with age above 25
    - show me all the posts posted by <particular username>
    - show me the all the posts in the year of 2024
    """)

    if 'query' not in st.session_state:
        st.session_state['query'] = ''
    if 'sql' not in st.session_state:
        st.session_state['sql'] = ''
    if 'df' not in st.session_state:
        st.session_state['df'] = None
    if 'agent_logs' not in st.session_state:
        st.session_state['agent_logs'] = ''

    query = st.text_area("Your question:", st.session_state['query'], height=120)
    submit = st.button("Submit")

    if submit and query.strip():
        with st.spinner("Processing your query..."):
            sql = None
            df = None
            logs = ""
            try:
                result, logs = run_agent(query, capture_verbose=True)
                if isinstance(result, (pd.DataFrame, dict, list)):
                    df = pd.DataFrame(result) if not isinstance(result, pd.DataFrame) else result
                else:
                    sql = str(result).strip()
                    if sql.lower().startswith("select"):
                        df, _ = execute_sql(sql)
            except Exception:
                sql = fallback_llm(query)
                df, _ = execute_sql(sql)
                logs = "(No agent logs available for fallback LLM mode.)"
            st.session_state['query'] = query
            st.session_state['sql'] = sql if sql else fallback_llm(query)
            st.session_state['df'] = df
            st.session_state['agent_logs'] = logs

    if st.session_state['df'] is not None and not getattr(st.session_state['df'], 'empty', True):
        st.dataframe(st.session_state['df'])
    elif st.session_state['df'] is not None:
        st.write("No results found.")

    # Show the button for viewing generated SQL
    if 'show_sql_code' not in st.session_state:
        st.session_state['show_sql_code'] = False
    if 'show_agent_working' not in st.session_state:
        st.session_state['show_agent_working'] = False

    # Reset display flags on new submit
    if submit and query.strip():
        st.session_state['show_sql_code'] = False
        st.session_state['show_agent_working'] = False

    # View generated SQL code button
    if st.session_state['sql']:
        if st.button('View generated SQL code'):
            st.session_state['show_sql_code'] = True
    if st.session_state['show_sql_code']:
        st.code(st.session_state['sql'], language='sql')

    # Show agent working process
    import re
    def clean_agent_logs(logs):
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        logs = ansi_escape.sub('', logs)
        logs = logs.replace('│', '|').replace('─', '-').replace('└', '+').replace('┌', '+').replace('┐', '+').replace('┘', '+')
        logs = logs.replace('╭', '+').replace('╰', '+').replace('╯', '+').replace('╮', '+').replace('═', '=').replace('║', '|')
        logs = re.sub(r'\n{3,}', '\n\n', logs)
        return logs.strip()
    if st.session_state['agent_logs']:
        if st.button("Show agent working"):
            st.session_state['show_agent_working'] = True
    if st.session_state['show_agent_working']:
        st.subheader("Agent Working Process")
        st.code(clean_agent_logs(st.session_state['agent_logs']), language="text")

    # Reset persistent displays on new query
    if submit and query.strip():
        st.session_state['show_sql_code'] = False
        st.session_state['show_agent_working'] = False

# --- Test SQL Tab ---
with tabs[1]:
    st.title("Test SQL Queries")
    # Sidebar only for this tab
    with st.sidebar:
        st.header("Database Viewer")
        table = st.selectbox("Select Table", ["Users", "Posts", "Comments", "All Tables"], key="test_sql_table")

    def test_sql_execute_query(query):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            st.error(f"Query failed: {str(e)}")
            return pd.DataFrame()

    if table == "Users":
        st.header("Users Table")
        query = "SELECT * FROM Users"
        result = test_sql_execute_query(query)
        st.dataframe(result)
    elif table == "Posts":
        st.header("Posts Table")
        query = "SELECT * FROM Posts"
        result = test_sql_execute_query(query)
        st.dataframe(result)
    elif table == "Comments":
        st.header("Comments Table")
        query = "SELECT * FROM Comments"
        result = test_sql_execute_query(query)
        st.dataframe(result)
    elif table == "All Tables":
        st.header("Database Overview")
        st.subheader("Users")
        query = "SELECT * FROM Users"
        result = test_sql_execute_query(query)
        st.dataframe(result)
        st.subheader("Posts")
        query = "SELECT * FROM Posts"
        result = test_sql_execute_query(query)
        st.dataframe(result)
        st.subheader("Comments")
        query = "SELECT * FROM Comments"
        result = test_sql_execute_query(query)
        st.dataframe(result)
        st.subheader("Relationships")
        st.write("Users → Posts")
        st.write("Users → Comments")
        st.write("Posts → Comments")

    st.header("Run Custom SQL Query")
    st.write("Enter your SQL query below:")
    sql_query = st.text_area("SQL Query", height=350, key="test_sql_query")
    if st.button("Execute Query", key="test_sql_exec"):
        if not sql_query.strip():
            st.warning("Please enter a SQL query!")
        else:
            with st.spinner("Executing query..."):
                result_df = test_sql_execute_query(sql_query)
                if result_df is not None and not result_df.empty:
                    st.header("Query Results")
                    st.dataframe(result_df)
                else:
                    st.info("No results returned from query")
    st.markdown("---")
    st.write("""
    💡 **Tips:**
    - Use JOIN to connect users with their interactions
    - Use WHERE clause to filter results
    - Use ORDER BY to sort results
    - Remember to end queries with semicolon (;)
    """)