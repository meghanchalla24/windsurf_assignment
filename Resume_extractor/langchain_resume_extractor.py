import streamlit as st
import os
import tempfile
import json
from langchain_core.prompts import PromptTemplate
from langchain_together import Together
import fitz

# Helper to extract only the first valid JSON object from a string
def extract_first_json_object(text):
    start = text.find('{')
    if start == -1:
        return None
    count = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            count += 1
        elif text[i] == '}':
            count -= 1
            if count == 0:
                return text[start:i+1]
    return None

os.environ["TOGETHER_API_KEY"] = "YOUR API KEY"

llm = Together(
    model="meta-llama/Llama-4-Scout-17B-16E-Instruct",
    max_tokens=2000,
    temperature=0
)

# Step 1: PDF extraction function
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "".join([page.get_text() for page in doc])
    doc.close()
    return text

# Step 2: Instruction Prompt (escaped correctly)
INSTRUCTION_PROMPT ="""
You are a resume information extractor. Given a candidate's resume text, extract the following details and return them in a single, valid JSON object with these exact keys and structure:

- name: (string, candidate's full name)
- email: (string, candidate's email address)
- phone: (string, candidate's phone number)
- skills: (list of strings, e.g. ["Python", "SQL", "Machine Learning"])
- work_experience: (list of objects, each with the following keys:)
    - Designation: (string, job title or role)
    - Company: (string, company name)
    - Duration: (string, e.g. "Jan 2024 - June 2024")
    - Duration_years: (integer, total years in this role)
    - Duration_months: (integer, additional months in this role, if any)
    - Projects: (list of objects, each with:)
        - Title: (string, project title)
        - Description: (string, short and summarized project description)

For each work experience, calculate and include the duration in both years and months (e.g., "Jul 2024 - Dec 2024" = 0 years, 6 months).
If any field is missing in the resume, set its value to null or an empty list as appropriate.

NOTE : STRICTLY ADHERE TO THE ABOVE FORMAT ONLY AND DO NOT INCLUDE ANYTHING EXTRA. 
The response should directly start with json wihtout any characters like '```'

Example output:
{{
  "name": "Meghan Challa",
  "email": "meghan@email.com",
  "phone": "+91-1234567890",
  "skills": ["Python", "SQL", "Machine Learning"],
  "work_experience": [
    {{
      "Designation": "AI/ML, Data Scientist",
      "Company": "Genpact",
      "Duration": "Jul 2024 - Dec 2024",
      "Duration_years": 0,
      "Duration_months": 6,
      "Projects": [
        {{
          "Title": "Human-in-the-Loop Pipeline: Refining Prompt Tuning with Human Feedback Integration",
          "Description": "Developed an interactive Human-in-the-Loop (HITL) pipeline to enhance entity extraction accuracy by using human feedback for prompt tuning as few shot examples."
        }}
      ]
    }}
  ]
}}

Extract the details as accurately as possible and return only the JSON.
if the projects are not explicitly mentioned, summarize the work experience in that particular company

The below is the candidate resume:
{candidate_resume}
"""

prompt_template = PromptTemplate.from_template(INSTRUCTION_PROMPT)

st.title("Resume Skill Extractor")

if 'extracted_json' not in st.session_state:
    st.session_state['extracted_json'] = None

import os

# Tab UI
tab1, tab2 = st.tabs(["Extract Resume", "All Resumes"])

with tab1:
    with st.sidebar:
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
        temp_file_path = None
        all_text = None
        if uploaded_file is not None:
            # Save uploaded file to a temp location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_file_path = tmp_file.name
            st.success(f"Uploaded: {uploaded_file.name}")

            # Show PDF preview only after upload
            st.subheader("Resume Preview (PDF)")
            import base64
            with open(temp_file_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="500" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

            # Extract text from PDF (for later extraction)
            all_text = extract_text_from_pdf(temp_file_path)
            # Button to extract details
            if st.button("Extract Details"):
                with st.spinner("Extracting details from resume using LLM..."):
                    try:
                        response = (prompt_template | llm).invoke({"candidate_resume": all_text})
                        print("LLM raw response:\n", response)
                        # Check for triple backticks and strip them
                        cleaned_response = response.strip()
                        if cleaned_response.startswith("```") and cleaned_response.endswith("```"):
                            cleaned_response = cleaned_response[3:-3].strip()
                        # Extract only the first valid JSON object using bracket counting
                        json_str = extract_first_json_object(cleaned_response)
                        print("Extracted JSON string for parsing:\n", json_str)
                        # Try to parse JSON safely
                        try:
                            extracted_json = json.loads(json_str)
                        except Exception:
                            st.warning("Could not parse LLM output as JSON. Showing raw output.")
                            extracted_json = cleaned_response
                        st.session_state['extracted_json'] = extracted_json
                    except Exception as e:
                        st.error(f"Failed to extract details: {e}")
                        st.session_state['extracted_json'] = None

        # Show extracted JSON in the sidebar if available
        if st.session_state.get('extracted_json'):
            st.subheader("Extracted JSON Output")
            st.json(st.session_state['extracted_json'])

    # Main area: Show extracted details in a summarized, readable format
    if st.session_state.get('extracted_json'):
        data = st.session_state['extracted_json']
        st.markdown("<h2>Extracted Resume Summary</h2>", unsafe_allow_html=True)
        # Basic Info
        st.markdown(f"<b>Name:</b> {data.get('name', 'N/A')}", unsafe_allow_html=True)
        st.markdown(f"<b>Email:</b> {data.get('email', 'N/A')}", unsafe_allow_html=True)
        st.markdown(f"<b>Phone:</b> {data.get('phone', 'N/A')}", unsafe_allow_html=True)
        # Skills
        skills = data.get('skills', [])
        if skills:
            st.markdown(f"<b>Skills:</b> {', '.join(skills)}", unsafe_allow_html=True)
        # Work Experience
        work_experience = data.get('work_experience', [])
        if work_experience:
            st.markdown("<h3>Work Experience</h3>", unsafe_allow_html=True)
            for idx, exp in enumerate(work_experience, 1):
                st.markdown(f"<b>{idx}. {exp.get('Designation', 'N/A')} at {exp.get('Company', 'N/A')}</b>", unsafe_allow_html=True)
                st.markdown(f"<b>Duration:</b> {exp.get('Duration', 'N/A')} ({exp.get('Duration_years', 0)} years, {exp.get('Duration_months', 0)} months)", unsafe_allow_html=True)
                # Projects
                projects = exp.get('Projects', [])
                if projects:
                    st.markdown("<b>Projects:</b>", unsafe_allow_html=True)
                    for proj in projects:
                        st.markdown(f"&nbsp;&nbsp;- <b>{proj.get('Title', 'N/A')}</b>: {proj.get('Description', 'N/A')}", unsafe_allow_html=True)
        # Save Resume button below summary
        if st.button("Save Resume"):
            file_path = "resumes.json"
            resume = st.session_state['extracted_json']
            import os
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        resumes = json.load(f)
                    except Exception:
                        resumes = []
            else:
                resumes = []
            resumes.append(resume)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(resumes, f, indent=2, ensure_ascii=False)
            st.success("Resume saved to resumes.json!")

with tab2:
    st.title("All Saved Resumes")
    file_path = "resumes.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                resumes = json.load(f)
            except Exception:
                resumes = []
        if resumes:
            # Get all unique skills
            all_skills = set()
            for res in resumes:
                all_skills.update(res.get('skills', []))
            all_skills = sorted(all_skills)
            # Skill filter
            selected_skills = st.multiselect("Filter by Skills", options=all_skills)
            # Dynamic filtering: update instantly (AND filter)
            if selected_skills:
                filtered_resumes = [
                    r for r in resumes if all(skill in r.get('skills', []) for skill in selected_skills)
                ]
            else:
                filtered_resumes = resumes
            # Show resumes
            if filtered_resumes:
                for idx, data in enumerate(filtered_resumes, 1):
                    st.markdown(f"<h2>Resume {idx}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<b>Name:</b> {data.get('name', 'N/A')}", unsafe_allow_html=True)
                    st.markdown(f"<b>Email:</b> {data.get('email', 'N/A')}", unsafe_allow_html=True)
                    st.markdown(f"<b>Phone:</b> {data.get('phone', 'N/A')}", unsafe_allow_html=True)
                    skills = data.get('skills', [])
                    if skills:
                        st.markdown(f"<b>Skills:</b> {', '.join(skills)}", unsafe_allow_html=True)
                    work_experience = data.get('work_experience', [])
                    if work_experience:
                        st.markdown("<h3>Work Experience</h3>", unsafe_allow_html=True)
                        for i, exp in enumerate(work_experience, 1):
                            st.markdown(f"<b>{i}. {exp.get('Designation', 'N/A')} at {exp.get('Company', 'N/A')}</b>", unsafe_allow_html=True)
                            st.markdown(f"<b>Duration:</b> {exp.get('Duration', 'N/A')} ({exp.get('Duration_years', 0)} years, {exp.get('Duration_months', 0)} months)", unsafe_allow_html=True)
                            projects = exp.get('Projects', [])
                            if projects:
                                st.markdown("<b>Projects:</b>", unsafe_allow_html=True)
                                for proj in projects:
                                    st.markdown(f"&nbsp;&nbsp;- <b>{proj.get('Title', 'N/A')}</b>: {proj.get('Description', 'N/A')}", unsafe_allow_html=True)
                    st.markdown("---")
            else:
                st.info("No resumes match the selected skills.")
        else:
            st.info("No resumes saved yet.")
    else:
        st.info("No resumes.json file found.")
