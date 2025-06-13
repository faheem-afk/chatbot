TalentScout Interview Bot

This is a fun little AI-based Interview Bot built using Streamlit + OpenAI GPT-4o. It asks up to 5 technical questions to a candidate based on their tech stack or preferred role, and logs everything into Google Cloud Storage.

⸻

What it Does?
	1.	Gathers candidate’s basic details using a simple form.
	2.	Starts a chat-based interview — like a real one!
	3.	Asks 5 smart questions using GPT-4o based on skills you gave.
	4.	Checks if your answers are on point (but doesn’t explain the answers).
	5.	Saves the entire convo + details to a .json file on Google Cloud Storage.

⸻

How it Works?

1. Libraries Used

import streamlit as st
import openai
import json
from google.cloud import storage
from datetime import datetime
from google.oauth2.service_account import Credentials

2. What are we storing?

We are saving:
	•	Name, email, phone etc.
	•	Tech stack like Python, Django, etc.
	•	Interview Q&A logs — everything the bot and user say.

⸻

Session Initialization

Before anything happens, we make sure that some variables exist in memory:

if "messages" not in st.session_state:
    st.session_state.messages = []

	•	messages → stores all chatbot and user messages
	•	interview_started, interview_ended → to control the flow
	•	All the form details → name, email, experience, etc.

⸻

Candidate Info Form

When the user visits the app, if interview not started, it shows a form like this:

st.text_input("Full Name")
st.number_input("Years of Experience")
st.multiselect("Tech Stack")

Once submitted:
	•	If anything is missing → shows error.
	•	Else → starts the interview!

⸻

System Prompt Setup (For GPT-4)

This is how GPT-4o knows how to behave:

"You are an expert technical interviewer at TalentScout..."

We tell it things like:
	•	Ask only 5 questions.
	•	Stay on topic.
	•	Don’t tolerate rubbish.
	•	Give feedback (but no long explanations).
	•	Be friendly, but also strict with flow.

⸻

💬 Starting the Interview

If the candidate submitted their form:
	•	First question is generated using openai.chat.completions.create().
	•	It’s shown using st.chat_message.

st.session_state.messages.append({"role": "assistant", "content": q})


⸻

For Each Answer

User types the answer in st.chat_input. Then:
	•	We check if it’s “exit”, then end early.
	•	Else:
	•	Send updated conversation to GPT.
	•	Get next question.
	•	Show it and update state.

if st.session_state.question_count < 5:
    # keep asking


⸻

After 5 Questions

After 5 rounds:
	•	It says thank you and ends politely.
	•	Shows balloons 
	•	Calls upload_to_gcs() to save everything.

⸻

Google Cloud Logging

What it does:

def upload_to_gcs(bucket_name, data):

	•	Creates a JSON file using current date and time
	•	Uses your GCP service account credentials from st.secrets
	•	Uploads to a bucket like: gs://logs_chatbotbyfaheem/interview_log_20250613_001539.json

⸻

Secrets

Make sure you save these in your .streamlit/secrets.toml:

OPENAI_API_KEY = "sk-..."
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n..."
client_email = "..."
client_id = "..."


⸻

How to Run It?
	1.	Clone the repo:

git clone https://github.com/yourusername/interview-bot.git
cd interview-bot


	2.	Install requirements:

pip install -r requirements.txt


	3.	Create .streamlit/secrets.toml and paste your keys.
	4.	Run it:

streamlit run app.py



⸻

Deployment Tips
	•	You can deploy on Streamlit Cloud.
	•	Just upload code, and paste your secrets using the settings menu.
	•	Make sure the GCS bucket exists already.

⸻

Sample Log File Structure (JSON)

{
  "name": "John Doe",
  "email": "john@example.com",
  "experience": 2,
  "desired_positions": "AI Intern",
  "tech_stack": ["Python", "TensorFlow"],
  "interview_log": [
    {"role": "assistant", "content": "Hi John! Let's begin."},
    {"role": "user", "content": "Sure."},
    {"role": "assistant", "content": "What is a tensor in TensorFlow?"}
  ]
}


Features
	•	GPT-4 powered chat
	•	Stores data to Google Cloud
	•	Friendly and professional tone
	•	Early exit possible
	•	Saves answers even if interview is quit

⸻


If you liked it, share it, fork it, or even better — improve it!
No matter who runs this bot, it will log every chat smartly and make your hiring smooth like butter

