# Required libraries
import streamlit as st
import openai
import json
from google.cloud import storage
from datetime import datetime
from google.oauth2.service_account import Credentials
import os


#This function will create logs about candidates' info and the conversation he/she does with the chatbot
def upload_to_gcs(bucket_name, data, file_prefix="interview_log"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{file_prefix}_{timestamp}.json"
    json_data = json.dumps(data, indent=2)

    # If using secrets:
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    
    client = storage.Client(credentials=credentials)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_string(json_data, content_type='application/json')
    gcs = f"gs://{bucket_name}/{filename}"
    return gcs


# initializing variables for the entire session

if "messages" not in st.session_state: # this variable stores all the questions and answers 
    st.session_state.messages = []
if "interview_started" not in st.session_state: # this variable is to state whether the interview has started or not
    st.session_state.interview_started = False
if "question_count" not in st.session_state: # this variable is to keep count of the number of questions
    st.session_state.question_count = 0
if "interview_ended" not in st.session_state: # this variable is to state whether the interview has ended or not
    st.session_state.interview_ended = False
if "full_name" not in st.session_state:
    st.session_state.full_name = ''
if "email" not in st.session_state:
    st.session_state.email = ''
if "phone" not in st.session_state:
    st.session_state.phone = ''
if "experience" not in st.session_state:
    st.session_state.experience = ''
if "desired_positions" not in st.session_state:
    st.session_state.desired_positions = ''
if "location" not in st.session_state:
    st.session_state.location = ''
if "tech_stack" not in st.session_state:
    st.session_state.tech_stack = ''


openai.api_key = st.secrets.get("OPENAI_API_KEY")

st.set_page_config(page_title="TalentScout Interview Bot", page_icon="🤖")
st.title("🤖 TalentScout AI/ML Intern Interview Bot")
st.write("This chatbot will gather your details and ask up to 5 technical questions based on your tech stack.")

#if the interview is not yet started, we want this to display to the user
if not st.session_state.interview_started:
    with st.form("candidate_info_form"):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        experience = st.number_input("Years of Experience", min_value=0, max_value=50, value=0)
        desired_positions = st.text_input("Desired Position(s)")
        location = st.text_input("Current Location")
        tech_stack = st.multiselect(
            "Tech Stack (languages, frameworks, databases, tools)",
            options=[
                "Python", "JavaScript", "Java", "C++", "Go", "Ruby", "C#", 'None',
                "Django", "Flask", "React", "Angular", "Vue.js", "Streamlit", 
                "TensorFlow", "PyTorch", "PostgreSQL", "MySQL", "MongoDB", "Docker", "Kubernetes"
            ],
            default=["Python"]
        )
        
        start = st.form_submit_button("Submit & Start Interview")
        
        # when user hits the submit button
        if start:
            if not all([full_name, email, phone, desired_positions, location, tech_stack]): #all fields are mandatory
                st.error("Please fill in all fields before continuing.")
            else:
                st.success("All details submitted successfully!")
                st.session_state.interview_started = True
                st.session_state.question_count = 0
                st.session_state.interview_ended = False
                st.session_state.messages = []

 
        system_prompt = (
            "You are an expert technical interviewer at TalentScout. "
            f"Do not tolerate any illicit content. "
            f"strictly tell the candidate you are not allowed to respond to any illicit content. ! and keep on moving forward with the questions."
            f"if the candidate doesn't provide any answer or wrong answer, then Only provide a slight one line definition. Not more than that! "
            f" if the candidate provides correct answer, then congratulate and move on with the questions. "
            f" The details provided to you about the candidate, just greet him/her with their name. that'all. "
            f"Any rubbish the candidate might tell, you can respond, but then keep moving forward with the questions. "
            f"if no details are provided, greet normally, and give a brief about the interview and then begin. "
            f"You are playing the role of an assistant here. "
            f"You will be provided with a Python dictionary that contains a dialogue between the assistant and the user. "
            f"If there is no such dictionary available, you should generate your response based on the candidate's details provided to you. "
            f"if the tech stack is None, you should use the desired positions detail to ask questions. "
            f"Use that information to ask a relevant and personalized questions. "
            f"You must read through the entire dialogue (if present) and respond appropriately based on the most recent user input. "
            f"Ask one clear and technical question at a time. "
            f"No matter what the candidate says—on-topic or off-topic—you must remain focused on the subject. "
            f"Briefly analyze the user's response and state whether the answer is correct or not. "
            f"You do not need to provide the correct answer. "
            f"Just casually let the candidate know if their response is incorrect. "
            f"Be supportive and encouraging, then proceed to ask the next question. "
            f"Candidate Details — Name: {full_name}, Email: {email}, Phone: {phone}, "
            f"Experience: {experience} years, Desired Position(s): {desired_positions}, "
            f"Location: {location}, Tech Stack: {', '.join(tech_stack)}."
        )
        st.session_state.messages.append({"role": "system", "content": system_prompt})

if st.session_state.interview_started: #when the interview starts

   
    if st.session_state.question_count == 0: #when the question count is zero, we want the chatbot to begin the conversation
        try:
            resp = openai.chat.completions.create( 
                model="gpt-4o",
                messages=st.session_state.messages
            )
            q = resp.choices[0].message.content
    
            st.session_state.messages.append({"role": "assistant", "content": q})
            
            
        except Exception as e:
                    st.error(f"Failed to generate a question: {e}")
    
        st.chat_message(st.session_state.messages[-1]['role']).write(st.session_state.messages[-1]['content']) #display the question
        st.session_state.question_count += 1 # increase the question count 
        
    if st.session_state.question_count < 5: # we only ask 5 questions at max
    
        answer = st.chat_input("Your answer... (type 'exit' to end)")

        if answer: #when the user gives an answer
            
            st.session_state.messages.append({"role": "user", "content": answer}) # answers will get appended in the list 

            if answer.strip().lower() in ["exit", "quit", "bye", "end"]:
                st.session_state.messages.append({"role": "assistant", "content": "Thank you for your time! We will be in touch soon."})
                st.session_state.interview_ended = True
            elif st.session_state.question_count < 5: # as long as question count is less than 5, we keep generating the questions

                try:
                    resp = openai.chat.completions.create(
                        model="gpt-4o",
                        messages=st.session_state.messages
                    )
                    next_q = resp.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": next_q}) # questions will get appended in the list
                except Exception as e:
                    st.error(f"Failed to get next question: {e}")
                st.chat_message(st.session_state.messages[-1]['role']).write(st.session_state.messages[-1]['content']) 
                st.session_state.question_count +=1
            
    else: # if the question count >= 5
        closing = (
            "Thank you for completing the interview! We appreciate your thoughtful responses. "
            "Please wait to hear from us soon."
        )
        st.session_state.messages.append({"role": "assistant", "content": closing})
        st.chat_message(st.session_state.messages[-1]['role']).write(st.session_state.messages[-1]['content'])
        st.session_state.interview_ended = True

        candidate_data = {
        "name": st.session_state['full_name'],
        "email": st.session_state['email'],
        "phone": st.session_state['phone'], 
        "experience": st.session_state['experience'],
        "desired_positions": st.session_state['desired_positions'],
        "location": st.session_state['location'],
        "tech_stack": st.session_state['tech_stack'],
        "interview_log": st.session_state.get("messages", [])
        }

        gcs_path = upload_to_gcs("logs_chatbotbyfaheem", candidate_data)
        st.success("Interview finished. Please wait to hear from us.")
        st.balloons()


else:
    st.info("🔹 Please complete your details above to begin the interview.")


